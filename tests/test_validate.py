"""Tests for the per-listing validation / confidence layer (rentlens.data.validate)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from rentlens.data import validate


def _row(**overrides) -> dict:
    row = {
        "listing_id": "L1",
        "locality": "Powai",
        "monthly_rent": 50_000.0,
        "carpet_area_sqft": 600.0,
        "bhk": 2.0,
        "bathrooms": 2.0,
        "furnishing": "semi",
        "floor": 5.0,
        "latitude": 19.11,
        "longitude": 72.90,
        "property_type": "apartment",
        "building_age_years": 5.0,
        "deposit": 150_000.0,
        "carpet_area_is_estimated": False,
        "dist_to_locality_centroid_m": 500.0,
    }
    row.update(overrides)
    return row


def _df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ── completeness ──────────────────────────────────────────────────────────────

def test_full_row_is_fully_complete():
    df = _df([_row()])
    assert validate.compute_completeness(df).iloc[0] == 1.0


def test_missing_key_field_lowers_completeness():
    df = _df([_row(floor=np.nan)])
    # one of ten key fields missing -> 0.9
    assert validate.compute_completeness(df).iloc[0] == pytest.approx(0.9)


# ── flags ─────────────────────────────────────────────────────────────────────

def test_estimated_area_flagged():
    df = _df([_row(carpet_area_is_estimated=True)])
    out = validate.annotate(df)
    assert "carpet_area_estimated" in out["quality_flags"].iloc[0]


def test_missing_deposit_and_age_flagged():
    df = _df([_row(deposit=np.nan, building_age_years=np.nan)])
    flags = validate.annotate(df)["quality_flags"].iloc[0]
    assert "no_deposit" in flags
    assert "missing_building_age" in flags


def test_far_from_centroid_flagged():
    df = _df([_row(dist_to_locality_centroid_m=3500.0)])
    assert "far_from_centroid" in validate.annotate(df)["quality_flags"].iloc[0]


def test_clean_row_has_no_problem_flags():
    df = _df([_row()])
    assert validate.annotate(df)["quality_flags"].iloc[0] == []


# ── confidence ────────────────────────────────────────────────────────────────

def test_estimated_area_has_lower_confidence_than_measured():
    measured = validate.compute_confidence(_df([_row()])).iloc[0]
    estimated = validate.compute_confidence(_df([_row(carpet_area_is_estimated=True)])).iloc[0]
    assert estimated["carpet_area_sqft"] < measured["carpet_area_sqft"]
    assert estimated["overall"] < measured["overall"]


def test_confidence_overall_in_unit_interval():
    conf = validate.compute_confidence(_df([_row(), _row(latitude=np.nan, longitude=np.nan)]))
    for c in conf:
        assert 0.0 <= c["overall"] <= 1.0


# ── annotate + report ─────────────────────────────────────────────────────────

def test_annotate_adds_schema_quality_columns():
    out = validate.annotate(_df([_row()]))
    for col in ["completeness_score", "quality_flags", "confidence"]:
        assert col in out.columns


def test_build_report_shape():
    out = validate.annotate(_df([_row(), _row(carpet_area_is_estimated=True)]))
    rep = validate.build_report(out)
    assert rep["n_listings"] == 2
    assert "carpet_area_estimated" in rep["flag_counts"]
    assert 0.0 <= rep["confidence_overall_mean"] <= 1.0
