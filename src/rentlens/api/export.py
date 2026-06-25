"""
Frontend data contract — aggregates-only JSON export.

This is the SEAM between the Python backend and the (separately owned)
frontend. The backend writes a small, fixed set of JSON files to ``data/api/``;
the frontend reads them. There is no server — these files are static and safe
to commit and serve publicly (e.g. via GitHub Pages).

PRIVACY (non-negotiable, enforced in code below)
-------------------------------------------------
Per the project's data-publication policy, **individual real listings are
never published — only aggregates.** Everything emitted here is locality-level
(or coarser), or is already-public OpenStreetMap transit infrastructure. A
guard (`_assert_aggregates_only`) fails the export if any per-listing field
(listing_id, latitude/longitude, rent, detail_url, …) ever leaks into a
listing-derived payload, so a future careless change can't silently expose
raw data.

Contract files written to data/api/ (see data/api/README.md):
  meta.json                 provenance + the locality/bbox the UI needs
  locality_mispricing.json  one record per locality (the headline finding)
  arbitrage_summary.json    one record per locality (counts/medians, no rows)
  transit.json              OSM stations (public infrastructure, has coords)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

# Fields that identify or locate an individual listing. None of these may ever
# appear in a listing-derived contract payload (transit data is exempt — it is
# public infrastructure, not listings).
PER_LISTING_FIELDS = frozenset({
    "listing_id", "latitude", "longitude", "detail_url", "raw_locality",
    "monthly_rent", "carpet_area_sqft", "scrape_timestamp", "address",
})


def _assert_aggregates_only(records: list[dict], n_localities: int, label: str) -> None:
    """Fail loudly if a listing-derived payload looks per-listing rather than
    aggregated. Two independent checks: granularity (no more rows than there
    are localities) and schema (no per-listing identifier/locator fields)."""
    if len(records) > n_localities:
        raise ValueError(
            f"[privacy] '{label}' has {len(records)} records but only "
            f"{n_localities} localities — looks per-listing, not aggregated."
        )
    for rec in records:
        leaked = PER_LISTING_FIELDS & set(rec)
        if leaked:
            raise ValueError(
                f"[privacy] '{label}' record exposes per-listing field(s): "
                f"{sorted(leaked)}"
            )


def _signal(residual_pct: float) -> str:
    if residual_pct > 5:
        return "OVERPRICED"
    if residual_pct < -5:
        return "UNDERPRICED"
    return "FAIR"


def build_locality_mispricing(df: pd.DataFrame) -> list[dict]:
    """Headline finding, one record per locality. Mirrors the locality table
    printed in Phase 4, as plain JSON-serialisable aggregates.

    Computed over the *priced* set (rows with a cross-market residual) so the
    public numbers match the README's locality table exactly — a handful of
    rows have no fair-rent estimate (e.g. missing floor dropped them from the
    OLS fit) and would otherwise pull pct_overpriced down."""
    df = df[df["residual_cm_pct"].notna()]
    records = []
    for locality, g in df.groupby("locality"):
        resid = g["residual_cm_pct"]
        residual_pct = round(float(resid.median()), 2)
        records.append({
            "locality": locality,
            "n": int(len(g)),
            "median_rent": int(g["monthly_rent"].median()),
            "fair_rent_cross_market": int(g["fundamental_fair_rent"].median()),
            "residual_pct": residual_pct,
            "pct_overpriced": round(float((resid > 0).mean() * 100), 1),
            "signal": _signal(residual_pct),
        })
    return sorted(records, key=lambda r: r["residual_pct"], reverse=True)


def build_arbitrage_summary(df: pd.DataFrame, max_future_dist_m: float = 2_500) -> list[dict]:
    """Per-locality arbitrage rollup: how many listings are underpriced AND
    near an under-construction station, and the median discount. Counts and
    medians only — never the individual candidate rows."""
    df = df[df["residual_cm_pct"].notna()]
    near_uc = df["dist_nearest_under_construction_m"] <= max_future_dist_m
    underpriced = df["residual_cm_pct"] < 0
    cands = df[near_uc & underpriced]

    records = []
    for locality, g in cands.groupby("locality"):
        records.append({
            "locality": locality,
            "n_candidates": int(len(g)),
            "median_discount_pct": round(float(g["residual_cm_pct"].median()), 2),
        })
    return sorted(records, key=lambda r: r["n_candidates"], reverse=True)


def build_transit(transit_path: Path) -> list[dict]:
    """OpenStreetMap stations — public infrastructure, exposed with
    coordinates so the frontend can draw the network."""
    t = pd.read_csv(transit_path)
    out = []
    for _, row in t.iterrows():
        opening = row.get("opening_date")
        out.append({
            "station_name": row["station_name"],
            "line": row["line"],
            "latitude": round(float(row["latitude"]), 6),
            "longitude": round(float(row["longitude"]), 6),
            "status": row["status"],
            "opening_date": None if pd.isna(opening) else str(opening)[:10],
        })
    return out


def build_index(meta: dict) -> dict:
    """Discovery document served at the API root, so hitting the base URL
    lists the available endpoints rather than 404-ing."""
    return {
        "name": f"RentLens {meta['display_name']} — public aggregates API",
        "description": (
            "Read-only, aggregates-only rental mispricing data. "
            "No individual listings are published."
        ),
        "version": "0.2",
        "scrape_date": meta["scrape_date"],
        "generated_at": meta["generated_at"],
        "disclaimer": meta["disclaimer"],
        "endpoints": {
            "meta": "meta.json",
            "locality_mispricing": "locality_mispricing.json",
            "arbitrage_summary": "arbitrage_summary.json",
            "transit": "transit.json",
        },
    }


def build_meta(df: pd.DataFrame, config_path: Path) -> dict:
    with open(config_path) as fh:
        cfg = yaml.safe_load(fh)
    scrape_dates = pd.to_datetime(df["scrape_timestamp"], errors="coerce", utc=True)
    return {
        "city": cfg.get("city", "mumbai"),
        "display_name": cfg.get("display_name", "Mumbai"),
        "bounding_box": cfg.get("bounding_box"),
        "source": sorted(df["source"].dropna().unique().tolist()),
        "scrape_date": (None if scrape_dates.isna().all()
                        else str(scrape_dates.max().date())),
        "n_listings": int(len(df)),
        "localities": sorted(df["locality"].dropna().unique().tolist()),
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "disclaimer": (
            "Aggregates only. No individual listings are published. Real "
            "rental data scraped from MagicBricks for a private analytical "
            "study; transit data from OpenStreetMap."
        ),
    }


def build_payloads(df: pd.DataFrame, transit_path: Path, config_path: Path) -> dict[str, object]:
    n_localities = df["locality"].nunique()
    locality = build_locality_mispricing(df)
    arbitrage = build_arbitrage_summary(df)
    _assert_aggregates_only(locality, n_localities, "locality_mispricing")
    _assert_aggregates_only(arbitrage, n_localities, "arbitrage_summary")
    meta = build_meta(df, config_path)
    return {
        "index.json": build_index(meta),
        "meta.json": meta,
        "locality_mispricing.json": locality,
        "arbitrage_summary.json": arbitrage,
        "transit.json": build_transit(transit_path),
    }


def _write_payloads(payloads: dict[str, object], out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, payload in payloads.items():
        path = out_dir / name
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written[name] = path
    return written


def run(
    scored_path: Path,
    transit_path: Path,
    config_path: Path,
    out_dir: Path,
    publish_dirs: list[Path] | None = None,
) -> dict[str, Path]:
    """Write the contract to ``out_dir`` (the canonical seam the frontend repo
    reads) and to any ``publish_dirs`` (e.g. ``docs/api`` — the copy GitHub
    Pages serves as the live free API). Building the payloads once and writing
    them everywhere keeps every published copy byte-identical."""
    df = pd.read_parquet(scored_path)
    payloads = build_payloads(df, transit_path, config_path)
    written = _write_payloads(payloads, out_dir)
    for d in publish_dirs or []:
        _write_payloads(payloads, d)
    return written


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    written = run(
        scored_path=root / "data" / "processed" / "listings_scored.parquet",
        transit_path=root / "data" / "reference" / "transit_mumbai.csv",
        config_path=root / "config" / "cities" / "mumbai.yaml",
        out_dir=root / "data" / "api",
        publish_dirs=[root / "docs" / "api"],  # served free by GitHub Pages
    )
    print(f"\n{'='*60}")
    print("RENTLENS — Aggregates-only API export")
    print(f"{'='*60}")
    print("  canonical : data/api/   (frontend repo reads this)")
    print("  published : docs/api/   (GitHub Pages serves this free)")
    for name in written:
        print(f"    - {name}")
