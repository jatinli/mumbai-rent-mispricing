"""Tests for the canonical-record / fuzzy-dedup pipeline (rentlens.data.dedup)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from rentlens.data import dedup


def _row(listing_id, lat=19.1100, lon=72.9000, bhk=2.0, bath=2.0,
         rent=70_000.0, area=600.0, title="2 BHK Flat for Rent in Powai", **extra):
    row = {
        "listing_id": listing_id, "latitude": lat, "longitude": lon, "bhk": bhk,
        "bathrooms": bath, "monthly_rent": rent, "carpet_area_sqft": area,
        "title": title, "locality": "Powai", "furnishing": "semi",
    }
    row.update(extra)
    return row


# ── helpers ───────────────────────────────────────────────────────────────────

def test_title_similarity_identical_and_disjoint():
    assert dedup.title_similarity("Lake View Apartment", "Lake View Apartment") == 1.0
    assert dedup.title_similarity("Lodha Park Tower", "Oberoi Esquire Wing") == 0.0


def test_title_similarity_empty_is_zero():
    # generic tokens are stop-words -> empty informative set -> 0
    assert dedup.title_similarity("Flat for Rent in Mumbai", "Flat for Rent in Mumbai") == 0.0


# ── is_duplicate ──────────────────────────────────────────────────────────────

def test_same_unit_slightly_different_rent_is_duplicate():
    a = pd.Series(_row("A", rent=70_000, area=600))
    b = pd.Series(_row("B", rent=72_000, area=610))  # within 5% on both
    assert dedup.is_duplicate(a, b)


def test_different_bhk_not_duplicate():
    a = pd.Series(_row("A", bhk=2.0))
    b = pd.Series(_row("B", bhk=3.0))
    assert not dedup.is_duplicate(a, b)


def test_far_apart_not_duplicate():
    a = pd.Series(_row("A", lat=19.1100, lon=72.9000))
    b = pd.Series(_row("B", lat=19.1700, lon=72.9500))  # different building
    assert not dedup.is_duplicate(a, b)


def test_rent_beyond_tolerance_not_duplicate():
    a = pd.Series(_row("A", rent=70_000))
    b = pd.Series(_row("B", rent=90_000))  # >5%
    assert not dedup.is_duplicate(a, b)


# ── build_canonical ───────────────────────────────────────────────────────────

def test_collapses_cluster_to_one_canonical():
    df = pd.DataFrame([
        _row("A", rent=70_000, area=600),
        _row("B", rent=71_000, area=605),  # dup of A
        _row("C", lat=19.2000, lon=72.9500, rent=50_000, area=400),  # distinct
    ])
    canonical, report = dedup.build_canonical(df)
    assert report["n_input"] == 3
    assert report["n_canonical"] == 2
    assert report["n_merged_away"] == 1
    # the surviving canonical for the A/B cluster carries both source ids
    kept = canonical[canonical["n_merged"] == 2].iloc[0]
    assert set(kept["merged_source_ids"]) == {"A", "B"}


def test_distinct_units_same_building_not_over_merged():
    # same building + bhk but rent and area both clearly different -> must stay separate
    df = pd.DataFrame([
        _row("A", rent=70_000, area=600),
        _row("B", rent=95_000, area=900),
    ])
    _, report = dedup.build_canonical(df)
    assert report["n_canonical"] == 2
    assert report["n_merged_away"] == 0


def test_canonical_keeps_most_complete_row():
    df = pd.DataFrame([
        _row("A", floor=np.nan, building_age_years=np.nan),  # less complete
        _row("B", floor=5.0, building_age_years=3.0),        # more complete
    ])
    canonical, _ = dedup.build_canonical(df)
    assert len(canonical) == 1
    assert canonical.iloc[0]["listing_id"] == "B"


def test_report_has_aggregate_size_distribution():
    df = pd.DataFrame([_row("A"), _row("B", rent=71_000)])
    _, report = dedup.build_canonical(df)
    assert report["cluster_size_distribution"].get(2) == 1


def test_written_report_excludes_per_listing_ids(tmp_path):
    df = pd.DataFrame([_row("SECRET_ID_1"), _row("SECRET_ID_2", rent=71_000)])
    _, report = dedup.build_canonical(df)
    out = tmp_path / "dedup_report.md"
    dedup.write_report(report, out)
    text = out.read_text(encoding="utf-8")
    assert "SECRET_ID_1" not in text  # no per-listing ids leak into the committed report
    assert "Cluster size distribution" in text
