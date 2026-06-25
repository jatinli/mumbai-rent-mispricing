"""
Canonical-record builder — fuzzy de-duplication beyond exact match.

clean.py already drops *exact* relistings (identical building/BHK/bath/area/
rent). This pass catches the softer case: the same physical unit reposted with
slightly different stated numbers (rent or carpet area off by a few percent,
common when two brokers list the same flat). It clusters such near-duplicates
into one canonical record and records which source ids were merged.

Conservatism is deliberate. Generic single-source titles ("2 BHK Flat for Rent
in Powai") carry no distinguishing signal, so merging on loose tolerances would
wrongly fuse genuinely distinct units in the same building. The default
tolerances are tight (same building within 60 m, identical BHK, identical
bathrooms, rent and carpet area each within 5%), and `build_canonical` returns a
report of exactly what merged so the thresholds can be audited.

Cross-source ready: `title_similarity` (a dependency-free token-set Jaccard) and
the geo/spec signals generalise across sources. With multiple sources a title /
description / image-hash agreement can be required in addition — see
`is_duplicate`'s `require_title_sim`.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from rentlens.geo.transit import haversine_m

GEO_M = 60.0          # same-building radius
RENT_TOL = 0.05       # 5% rent tolerance
AREA_TOL = 0.05       # 5% carpet-area tolerance

# Fields used to pick the "best" record in a cluster (most complete wins).
_COMPLETENESS_FIELDS = [
    "monthly_rent", "carpet_area_sqft", "bhk", "bathrooms", "furnishing",
    "floor", "building_age_years", "latitude", "longitude", "property_type",
]

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize_title(title: str | None) -> set[str]:
    """Lowercased token set, stop-words dropped — for cross-source fuzzy title
    matching. Returns an empty set for missing/blank titles."""
    if not title or not isinstance(title, str):
        return set()
    stop = {"bhk", "flat", "for", "rent", "in", "the", "a", "mumbai", "apartment"}
    return {t for t in _TOKEN_RE.findall(title.lower()) if t not in stop}


def title_similarity(a: str | None, b: str | None) -> float:
    """Jaccard similarity of normalized title token sets (0..1). 0 if either
    side has no informative tokens (so it can't *support* a merge)."""
    ta, tb = normalize_title(a), normalize_title(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _within(a: float, b: float, tol: float) -> bool:
    if pd.isna(a) or pd.isna(b):
        return False
    base = max(abs(a), abs(b))
    return base == 0 or abs(a - b) / base <= tol


def is_duplicate(a: pd.Series, b: pd.Series, require_title_sim: float = 0.0) -> bool:
    """Conservative same-unit test for two listings in the same block."""
    if a.get("bhk") != b.get("bhk"):
        return False
    # bathrooms must match when both are present (a missing value doesn't veto)
    ba, bb = a.get("bathrooms"), b.get("bathrooms")
    if pd.notna(ba) and pd.notna(bb) and ba != bb:
        return False
    dist = haversine_m(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
    if dist > GEO_M:
        return False
    if not _within(a.get("monthly_rent"), b.get("monthly_rent"), RENT_TOL):
        return False
    if not _within(a.get("carpet_area_sqft"), b.get("carpet_area_sqft"), AREA_TOL):
        return False
    if require_title_sim > 0 and title_similarity(a.get("title"), b.get("title")) < require_title_sim:
        return False
    return True


class _UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        self.parent[self.find(a)] = self.find(b)


def _block_key(row: pd.Series) -> tuple:
    # round to ~11 m so the same building lands in one block; BHK splits further
    return (round(row["latitude"], 4), round(row["longitude"], 4), row.get("bhk"))


def find_clusters(df: pd.DataFrame, require_title_sim: float = 0.0) -> np.ndarray:
    """Return an array of cluster ids (one per row). Only listings within the
    same block are ever compared, keeping this near-linear in practice."""
    n = len(df)
    uf = _UnionFind(n)
    positions = {idx: i for i, idx in enumerate(df.index)}

    blocks: dict[tuple, list] = {}
    for idx, row in df.iterrows():
        blocks.setdefault(_block_key(row), []).append(idx)

    for members in blocks.values():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = df.loc[members[i]], df.loc[members[j]]
                if is_duplicate(a, b, require_title_sim):
                    uf.union(positions[members[i]], positions[members[j]])

    return np.array([uf.find(positions[idx]) for idx in df.index])


def _row_completeness(row: pd.Series) -> int:
    return int(sum(pd.notna(row.get(f)) for f in _COMPLETENESS_FIELDS))


def build_canonical(
    df: pd.DataFrame, require_title_sim: float = 0.0
) -> tuple[pd.DataFrame, dict]:
    """Collapse near-duplicate clusters to one canonical record each.

    The canonical row is the most complete in its cluster (tie-break: lowest
    listing_id, for determinism). It gains `merged_source_ids` (all listing_ids
    in the cluster) and `n_merged`. Returns (canonical_df, report)."""
    if df.empty:
        return df.assign(merged_source_ids=[], n_merged=[]), {
            "n_input": 0, "n_canonical": 0, "n_merged_away": 0, "n_clusters_multi": 0, "examples": [],
        }

    work = df.copy()
    work["_cluster"] = find_clusters(work, require_title_sim)
    work["_completeness"] = work.apply(_row_completeness, axis=1)

    canonical_rows = []
    examples = []
    n_merged_away = 0
    n_clusters_multi = 0

    for _, group in work.groupby("_cluster", sort=False):
        ids = list(group["listing_id"])
        best = group.sort_values(["_completeness", "listing_id"], ascending=[False, True]).iloc[0].copy()
        best["merged_source_ids"] = ids
        best["n_merged"] = len(ids)
        canonical_rows.append(best)
        if len(ids) > 1:
            n_clusters_multi += 1
            n_merged_away += len(ids) - 1
            if len(examples) < 10:
                examples.append({
                    "kept": best["listing_id"],
                    "merged": [i for i in ids if i != best["listing_id"]],
                    "locality": best.get("locality"),
                    "bhk": best.get("bhk"),
                    "rent_range": [int(group["monthly_rent"].min()), int(group["monthly_rent"].max())],
                })

    canonical = pd.DataFrame(canonical_rows).drop(columns=["_cluster", "_completeness"]).reset_index(drop=True)
    size_dist = canonical["n_merged"].value_counts().sort_index()
    report = {
        "n_input": int(len(df)),
        "n_canonical": int(len(canonical)),
        "n_merged_away": int(n_merged_away),
        "n_clusters_multi": int(n_clusters_multi),
        "cluster_size_distribution": {int(k): int(v) for k, v in size_dist.items()},
        # Per-listing examples are kept in-memory for local audit only; they are
        # NOT written to the committed report (they would expose per-listing
        # id/locality/rent, which the aggregates-only policy forbids publishing).
        "examples": examples,
    }
    return canonical, report


def write_report(report: dict, out_path: Path) -> None:
    lines = [
        "# RentLens — Canonical Record / Dedup Report",
        "",
        f"Input listings:        **{report['n_input']:,}**",
        f"Canonical records:     **{report['n_canonical']:,}**",
        f"Near-duplicates merged: **{report['n_merged_away']:,}** "
        f"(across {report['n_clusters_multi']:,} multi-listing clusters)",
        "",
        f"Tolerances: same building within {GEO_M:.0f} m, identical BHK & bathrooms, "
        f"rent within {RENT_TOL:.0%}, carpet area within {AREA_TOL:.0%}.",
        "",
        "## Cluster size distribution",
        "",
        "| Listings in cluster | Number of canonical records |",
        "|---------------------|-----------------------------|",
    ]
    for size, count in sorted(report["cluster_size_distribution"].items()):
        label = "1 (unique)" if size == 1 else str(size)
        lines.append(f"| {label} | {count:,} |")
    lines += [
        "",
        "_Per-listing merge examples are available locally but not published "
        "(aggregates-only policy)._",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(listings_path: Path, output_path: Path, report_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(listings_path)
    canonical, report = build_canonical(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canonical.to_parquet(output_path, index=False)
    write_report(report, report_path)
    return canonical


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    canonical = run(
        listings_path=root / "data" / "processed" / "listings.parquet",
        output_path=root / "data" / "processed" / "listings_canonical.parquet",
        report_path=root / "data" / "processed" / "dedup_report.md",
    )
    print(f"\n{'='*60}")
    print("RENTLENS — Canonical records / fuzzy dedup")
    print(f"{'='*60}")
    print(f"Canonical records: {len(canonical):,}")
