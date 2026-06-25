"""
Historical snapshots + price-change tracking.

Each scrape appends an immutable snapshot to an append-only history store
(`data/processed/listings_snapshots.parquet`) rather than overwriting the
previous data. Comparing the newest scrape to the prior one yields:

  - new listings     (ids present now, absent before)
  - removed listings (ids active before, absent now)
  - price changes    (ids in both whose monthly_rent moved)

Identity note (honest scope): listings are tracked by `listing_id` across time.
That is exact when a source keeps stable ids; when a portal reassigns ids on
repost, the same flat looks "removed + new". Robust cross-time identity would
reuse the fuzzy matcher in `dedup.py` (same building/BHK/rent) — a clean
extension left as a hook rather than overclaimed here.

Privacy: the committed change report is aggregate only (counts + a
distribution); per-listing rents and ids are never written to it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SNAPSHOT_FIELDS = ["scrape_date", "listing_id", "locality", "monthly_rent", "status"]


def load_history(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame(columns=SNAPSHOT_FIELDS)


def _snapshot_rows(listings: pd.DataFrame, scrape_date: str) -> pd.DataFrame:
    rows = listings[["listing_id", "locality", "monthly_rent"]].copy()
    rows["scrape_date"] = scrape_date
    rows["status"] = "active"
    return rows[SNAPSHOT_FIELDS]


def diff_snapshots(prev: pd.DataFrame, current: pd.DataFrame) -> dict:
    """Compare two single-scrape snapshots (prev, current) by listing_id."""
    prev_ids = set(prev["listing_id"])
    cur_ids = set(current["listing_id"])
    new_ids = cur_ids - prev_ids
    removed_ids = prev_ids - cur_ids

    prev_rent = prev.set_index("listing_id")["monthly_rent"]
    cur_rent = current.set_index("listing_id")["monthly_rent"]
    price_changes = []
    for lid in prev_ids & cur_ids:
        old, new = prev_rent.get(lid), cur_rent.get(lid)
        if pd.notna(old) and pd.notna(new) and old != new:
            price_changes.append((lid, float(old), float(new)))

    return {"new_ids": new_ids, "removed_ids": removed_ids, "price_changes": price_changes}


def append_snapshot(
    history: pd.DataFrame, listings: pd.DataFrame, scrape_date: str
) -> tuple[pd.DataFrame, dict]:
    """Append `listings` as the `scrape_date` snapshot; return (history, diff).

    Idempotent on scrape_date: if that date is already in history the snapshot
    is not re-appended (the diff is computed against the prior date as usual).
    """
    current = _snapshot_rows(listings, scrape_date)

    dates = sorted(history["scrape_date"].unique()) if not history.empty else []
    prior_dates = [d for d in dates if d < scrape_date]
    prev = (history[history["scrape_date"] == prior_dates[-1]]
            if prior_dates else pd.DataFrame(columns=SNAPSHOT_FIELDS))

    diff = diff_snapshots(prev, current)

    if scrape_date in dates:
        new_history = history  # already recorded; don't duplicate
    else:
        new_history = pd.concat([history, current], ignore_index=True)
    return new_history, diff


def build_change_report(diff: dict, n_current: int, is_baseline: bool) -> dict:
    changes = diff["price_changes"]
    pct = [((new - old) / old * 100) for _, old, new in changes if old]
    return {
        "is_baseline": is_baseline,
        "n_current": int(n_current),
        "n_new": len(diff["new_ids"]),
        "n_removed": len(diff["removed_ids"]),
        "n_price_changes": len(changes),
        "n_increased": int(sum(p > 0 for p in pct)),
        "n_decreased": int(sum(p < 0 for p in pct)),
        "median_abs_pct_change": round(float(np.median(np.abs(pct))), 2) if pct else 0.0,
    }


def write_report(report: dict, out_path: Path) -> None:
    lines = ["# RentLens — Snapshot / Price-Change Report", ""]
    if report["is_baseline"]:
        lines += [
            "**Baseline snapshot** — first scrape recorded; no prior to compare against.",
            "",
            f"Listings recorded: **{report['n_current']:,}**",
            "",
            "Re-run after a future scrape to populate new / removed / price-change counts.",
        ]
    else:
        lines += [
            f"Listings in latest scrape: **{report['n_current']:,}**",
            "",
            "| Change | Count |",
            "|--------|-------|",
            f"| New listings | {report['n_new']:,} |",
            f"| Removed listings | {report['n_removed']:,} |",
            f"| Price changes | {report['n_price_changes']:,} |",
            f"| &nbsp;&nbsp;↑ increased | {report['n_increased']:,} |",
            f"| &nbsp;&nbsp;↓ decreased | {report['n_decreased']:,} |",
            f"| Median |Δrent| | {report['median_abs_pct_change']}% |",
        ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _infer_scrape_date(listings: pd.DataFrame) -> str:
    ts = pd.to_datetime(listings["scrape_timestamp"], errors="coerce", utc=True)
    if ts.notna().any():
        return str(ts.max().date())
    return str(pd.Timestamp.utcnow().date())


def run(listings_path: Path, history_path: Path, report_path: Path,
        scrape_date: str | None = None) -> pd.DataFrame:
    listings = pd.read_parquet(listings_path)
    scrape_date = scrape_date or _infer_scrape_date(listings)
    history = load_history(history_path)
    is_baseline = history.empty

    new_history, diff = append_snapshot(history, listings, scrape_date)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    new_history.to_parquet(history_path, index=False)

    report = build_change_report(diff, n_current=len(listings), is_baseline=is_baseline)
    write_report(report, report_path)
    return new_history


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    hist = run(
        listings_path=root / "data" / "processed" / "listings_canonical.parquet",
        history_path=root / "data" / "processed" / "listings_snapshots.parquet",
        report_path=root / "data" / "processed" / "snapshot_report.md",
    )
    print(f"\n{'='*60}")
    print("RENTLENS — Snapshots / price tracking")
    print(f"{'='*60}")
    print(f"Snapshot rows in history: {len(hist):,}")
    print(f"Distinct scrape dates   : {hist['scrape_date'].nunique()}")
