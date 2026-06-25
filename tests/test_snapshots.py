"""Tests for historical snapshots + price tracking (rentlens.data.snapshots)."""

from __future__ import annotations

import pandas as pd

from rentlens.data import snapshots


def _listings(rows):
    return pd.DataFrame(rows)


def test_baseline_snapshot_records_all_as_new():
    history = snapshots.load_history(__import__("pathlib").Path("does_not_exist.parquet"))
    assert history.empty
    cur = _listings([
        {"listing_id": "A", "locality": "Powai", "monthly_rent": 50_000},
        {"listing_id": "B", "locality": "Mulund", "monthly_rent": 40_000},
    ])
    new_history, diff = snapshots.append_snapshot(history, cur, "2026-06-23")
    assert len(new_history) == 2
    assert diff["new_ids"] == {"A", "B"}
    assert diff["removed_ids"] == set()


def test_detects_new_removed_and_price_change():
    day1 = snapshots._snapshot_rows(
        _listings([
            {"listing_id": "A", "locality": "Powai", "monthly_rent": 50_000},
            {"listing_id": "B", "locality": "Powai", "monthly_rent": 40_000},
        ]), "2026-06-23")
    day2 = _listings([
        {"listing_id": "A", "locality": "Powai", "monthly_rent": 55_000},  # price change
        {"listing_id": "C", "locality": "Powai", "monthly_rent": 30_000},  # new
    ])  # B removed
    new_history, diff = snapshots.append_snapshot(day1, day2, "2026-07-23")
    assert diff["new_ids"] == {"C"}
    assert diff["removed_ids"] == {"B"}
    assert diff["price_changes"] == [("A", 50_000.0, 55_000.0)]
    assert len(new_history) == 4  # 2 from day1 + 2 from day2 (append-only)


def test_idempotent_on_same_scrape_date():
    cur = _listings([{"listing_id": "A", "locality": "Powai", "monthly_rent": 50_000}])
    h1, _ = snapshots.append_snapshot(pd.DataFrame(columns=snapshots.SNAPSHOT_FIELDS), cur, "2026-06-23")
    h2, _ = snapshots.append_snapshot(h1, cur, "2026-06-23")  # same date again
    assert len(h2) == len(h1)  # not duplicated


def test_change_report_aggregates_direction():
    diff = {
        "new_ids": {"X"},
        "removed_ids": set(),
        "price_changes": [("A", 50_000.0, 55_000.0), ("B", 60_000.0, 54_000.0)],
    }
    rep = snapshots.build_change_report(diff, n_current=3, is_baseline=False)
    assert rep["n_new"] == 1
    assert rep["n_price_changes"] == 2
    assert rep["n_increased"] == 1
    assert rep["n_decreased"] == 1


def test_written_report_excludes_per_listing_data(tmp_path):
    diff = {"new_ids": {"SECRET_ID"}, "removed_ids": set(),
            "price_changes": [("SECRET_ID", 50_000.0, 55_000.0)]}
    rep = snapshots.build_change_report(diff, n_current=1, is_baseline=False)
    out = tmp_path / "snapshot_report.md"
    snapshots.write_report(rep, out)
    text = out.read_text(encoding="utf-8")
    assert "SECRET_ID" not in text
    assert "55" not in text or "55,000" not in text  # no raw rents


def test_baseline_report_text(tmp_path):
    rep = snapshots.build_change_report(
        {"new_ids": set(), "removed_ids": set(), "price_changes": []},
        n_current=500, is_baseline=True)
    out = tmp_path / "r.md"
    snapshots.write_report(rep, out)
    assert "Baseline snapshot" in out.read_text(encoding="utf-8")
