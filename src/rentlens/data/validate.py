"""
Phase C+ — per-listing validation, completeness, and confidence scoring.

Runs on *cleaned* listings (the output of clean.py) and annotates each row with
three canonical-schema quality fields:

  completeness_score : 0-1 fraction of the analytically key fields populated
  quality_flags      : list of soft quality flags (not drop reasons — clean.py
                       already dropped the hard failures; these mark survivors
                       worth treating with caution)
  confidence         : per-field provenance confidence (0-1) + an overall

Honest scope
------------
The spec asks to "verify extracted values against page content". That check
needs the raw HTML and therefore belongs in the *scraper* (the adapter, where
the page text is in hand) — see the `verify_*` hook note in scrape/base.py.
This module does what can be done rigorously from cleaned data alone:
completeness, plausibility flags, and a confidence derived from provenance
signals the pipeline already records (e.g. `carpet_area_is_estimated`, distance
of the listing from its assigned locality centroid). Confidence here is a
documented heuristic, not a claim of source-verified truth.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Fields that matter for "is this listing analytically usable".
KEY_FIELDS = [
    "locality", "monthly_rent", "carpet_area_sqft", "bhk", "bathrooms",
    "furnishing", "floor", "latitude", "longitude", "property_type",
]

# A listing below this completeness is "low quality" (flagged, not dropped).
MIN_COMPLETENESS = 0.8

# Distance (m) from the assigned locality centroid beyond which the bucket
# assignment is shakier — clean.py drops > 4 km; this softer flag marks the
# 2.5-4 km band.
SOFT_CENTROID_FLAG_M = 2_500


def compute_completeness(df: pd.DataFrame) -> pd.Series:
    present = [f for f in KEY_FIELDS if f in df.columns]
    return df[present].notna().mean(axis=1).round(3)


def compute_quality_flags(df: pd.DataFrame, completeness: pd.Series) -> pd.Series:
    n = len(df)

    def col(name):
        return df[name] if name in df.columns else pd.Series([np.nan] * n, index=df.index)

    rent_psf = col("monthly_rent") / col("carpet_area_sqft")
    rent_psf_lo, rent_psf_hi = rent_psf.quantile(0.01), rent_psf.quantile(0.99)

    flag_masks = {
        "low_completeness":   completeness < MIN_COMPLETENESS,
        "carpet_area_estimated": col("carpet_area_is_estimated") == True,  # noqa: E712
        "missing_floor":      col("floor").isna(),
        "missing_building_age": col("building_age_years").isna(),
        "no_deposit":         col("deposit").isna(),
        "far_from_centroid":  col("dist_to_locality_centroid_m") > SOFT_CENTROID_FLAG_M,
        "rent_psf_extreme":   (rent_psf < rent_psf_lo) | (rent_psf > rent_psf_hi),
    }

    flags_per_row = [[] for _ in range(n)]
    for name, mask in flag_masks.items():
        mask = mask.fillna(False).to_numpy()
        for i, on in enumerate(mask):
            if on:
                flags_per_row[i].append(name)
    return pd.Series(flags_per_row, index=df.index)


def _locality_confidence(dist_m: pd.Series) -> pd.Series:
    # closer to the assigned centroid -> more confident bucket
    conf = pd.Series(0.6, index=dist_m.index)
    conf[dist_m <= 2_500] = 0.8
    conf[dist_m <= 1_000] = 1.0
    conf[dist_m.isna()] = 0.5
    return conf


def compute_confidence(df: pd.DataFrame) -> pd.Series:
    n = len(df)

    def col(name, default=np.nan):
        return df[name] if name in df.columns else pd.Series([default] * n, index=df.index)

    # carpet area: measured vs estimated-from-super-area
    estimated = (col("carpet_area_is_estimated") == True).fillna(False)  # noqa: E712
    area_conf = pd.Series(np.where(col("carpet_area_sqft").isna(), 0.0,
                                   np.where(estimated, 0.6, 1.0)), index=df.index)
    # geo: present (from source) or not
    geo_conf = (col("latitude").notna() & col("longitude").notna()).astype(float)
    loc_conf = _locality_confidence(col("dist_to_locality_centroid_m"))
    rent_conf = col("monthly_rent").notna().astype(float)

    records = []
    for a, g, l, r in zip(area_conf, geo_conf, loc_conf, rent_conf):
        per_field = {
            "carpet_area_sqft": round(float(a), 2),
            "geo": round(float(g), 2),
            "locality": round(float(l), 2),
            "monthly_rent": round(float(r), 2),
        }
        per_field["overall"] = round(float(np.mean(list(per_field.values()))), 3)
        records.append(per_field)
    return pd.Series(records, index=df.index)


def annotate(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    completeness = compute_completeness(out)
    out["completeness_score"] = completeness
    out["quality_flags"] = compute_quality_flags(out, completeness)
    out["confidence"] = compute_confidence(out)
    return out


def build_report(df: pd.DataFrame) -> dict:
    flags = df["quality_flags"]
    all_flag_names = sorted({f for row in flags for f in row})
    flag_counts = {name: int(flags.apply(lambda r: name in r).sum()) for name in all_flag_names}
    overall_conf = df["confidence"].apply(lambda c: c["overall"])
    return {
        "n_listings": int(len(df)),
        "completeness_mean": round(float(df["completeness_score"].mean()), 3),
        "pct_below_min_completeness": round(float((df["completeness_score"] < MIN_COMPLETENESS).mean() * 100), 1),
        "confidence_overall_mean": round(float(overall_conf.mean()), 3),
        "flag_counts": flag_counts,
        "missing_per_key_field": {
            f: round(float(df[f].isna().mean() * 100), 1)
            for f in KEY_FIELDS if f in df.columns
        },
    }


def write_report(report: dict, out_path: Path) -> None:
    lines = [
        "# RentLens — Validation & Confidence Report",
        "",
        f"Listings validated: **{report['n_listings']:,}**",
        f"Mean completeness:  **{report['completeness_mean']:.3f}**  "
        f"({report['pct_below_min_completeness']}% below the {MIN_COMPLETENESS} threshold)",
        f"Mean overall confidence: **{report['confidence_overall_mean']:.3f}**",
        "",
        "## Soft quality flags (counts)",
        "",
        "| Flag | Listings |",
        "|------|----------|",
    ]
    for name, count in sorted(report["flag_counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {name} | {count:,} |")
    lines += ["", "## Missing % per key field", "", "| Field | % missing |", "|-------|-----------|"]
    for field, pct in report["missing_per_key_field"].items():
        lines.append(f"| {field} | {pct} |")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(listings_path: Path, output_path: Path, report_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(listings_path)
    annotated = annotate(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    annotated.to_parquet(output_path, index=False)
    write_report(build_report(annotated), report_path)
    return annotated


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    df = run(
        listings_path=root / "data" / "processed" / "listings.parquet",
        output_path=root / "data" / "processed" / "listings_validated.parquet",
        report_path=root / "data" / "processed" / "validation_report.md",
    )
    rep = build_report(df)
    print(f"\n{'='*60}")
    print("RENTLENS — Validation & Confidence")
    print(f"{'='*60}")
    print(f"Listings           : {rep['n_listings']:,}")
    print(f"Mean completeness  : {rep['completeness_mean']:.3f}")
    print(f"Mean confidence    : {rep['confidence_overall_mean']:.3f}")
    print(f"Flag counts        : {rep['flag_counts']}")
