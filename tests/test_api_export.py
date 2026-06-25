"""Tests for the frontend data contract export (rentlens.api.export).

The load-bearing concern is privacy: the export must emit only aggregates and
must fail loudly if per-listing data ever leaks. These tests build a tiny
synthetic 'scored' frame (no network, no real data) and assert both the shape
of the contract and the guard.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from rentlens.api.export import (
    _assert_aggregates_only,
    build_arbitrage_summary,
    build_locality_mispricing,
    build_transit,
    run,
)


def _scored(n_per_locality: int = 6) -> pd.DataFrame:
    """Minimal scored frame with the columns the exporter reads."""
    rows = []
    specs = {
        "Powai": (14.0, 200.0),     # overpriced, near UC
        "Mulund": (-23.0, 150.0),   # underpriced, near UC
        "Andheri East": (2.0, 3000.0),  # fair, far from UC
    }
    for loc, (resid, uc_dist) in specs.items():
        for i in range(n_per_locality):
            rows.append({
                "listing_id": f"{loc[:3]}{i}",
                "source": "MAGICBRICKS",
                "scrape_timestamp": "2026-06-23T00:00:00+00:00",
                "locality": loc,
                "monthly_rent": 50_000 + i * 1000,
                "fundamental_fair_rent": 48_000,
                "residual_cm_pct": resid + i * 0.1,
                "dist_nearest_under_construction_m": uc_dist,
            })
    return pd.DataFrame(rows)


# ── privacy guard ─────────────────────────────────────────────────────────────

def test_guard_passes_for_aggregates():
    records = [{"locality": "Powai", "n": 10}, {"locality": "Mulund", "n": 8}]
    _assert_aggregates_only(records, n_localities=3, label="ok")  # no raise


def test_guard_rejects_per_listing_field():
    leaky = [{"locality": "Powai", "latitude": 19.1, "monthly_rent": 50000}]
    with pytest.raises(ValueError, match="per-listing field"):
        _assert_aggregates_only(leaky, n_localities=3, label="leaky")


def test_guard_rejects_too_many_rows():
    too_many = [{"locality": f"L{i}"} for i in range(5)]
    with pytest.raises(ValueError, match="looks per-listing"):
        _assert_aggregates_only(too_many, n_localities=3, label="toomany")


# ── builders ──────────────────────────────────────────────────────────────────

def test_locality_mispricing_is_one_row_per_locality():
    recs = build_locality_mispricing(_scored())
    assert len(recs) == 3
    assert {r["locality"] for r in recs} == {"Powai", "Mulund", "Andheri East"}
    # no per-listing fields present
    assert all("listing_id" not in r and "latitude" not in r for r in recs)


def test_locality_mispricing_signal_classification():
    recs = {r["locality"]: r for r in build_locality_mispricing(_scored())}
    assert recs["Powai"]["signal"] == "OVERPRICED"
    assert recs["Mulund"]["signal"] == "UNDERPRICED"
    assert recs["Andheri East"]["signal"] == "FAIR"


def test_locality_mispricing_ignores_nan_residual_rows():
    df = _scored()
    df.loc[df["locality"] == "Powai", "residual_cm_pct"] = np.nan
    recs = {r["locality"]: r for r in build_locality_mispricing(df)}
    # Powai had only NaN residuals -> excluded entirely from the priced set
    assert "Powai" not in recs


def test_arbitrage_summary_counts_only_near_uc_underpriced():
    recs = {r["locality"]: r for r in build_arbitrage_summary(_scored())}
    # Mulund: underpriced + near UC -> candidates; Andheri East: fair + far -> none
    assert "Mulund" in recs
    assert recs["Mulund"]["n_candidates"] == 6
    assert "Andheri East" not in recs


def test_run_writes_contract_and_passes_guard(tmp_path):
    scored = tmp_path / "scored.parquet"
    _scored().to_parquet(scored, index=False)

    transit = tmp_path / "transit.csv"
    pd.DataFrame([{
        "station_name": "X", "line": "L1", "latitude": 19.1,
        "longitude": 72.9, "status": "operational", "opening_date": "2014-06-08",
    }]).to_csv(transit, index=False)

    config = tmp_path / "city.yaml"
    config.write_text(
        "city: testcity\ndisplay_name: Testcity\n"
        "bounding_box: { lat_min: 18.9, lat_max: 19.3, lon_min: 72.8, lon_max: 73.0 }\n",
        encoding="utf-8",
    )

    out = tmp_path / "api"
    written = run(scored, transit, config, out)

    assert set(written) == {
        "index.json", "meta.json", "locality_mispricing.json",
        "arbitrage_summary.json", "transit.json",
    }
    meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
    assert meta["n_listings"] == 18
    assert meta["source"] == ["MAGICBRICKS"]

    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    assert set(index["endpoints"].values()) == {
        "meta.json", "locality_mispricing.json",
        "arbitrage_summary.json", "transit.json",
    }

    transit_json = json.loads((out / "transit.json").read_text(encoding="utf-8"))
    assert transit_json[0]["station_name"] == "X"
    assert transit_json[0]["opening_date"] == "2014-06-08"


def test_run_publishes_to_extra_dirs(tmp_path):
    scored = tmp_path / "scored.parquet"
    _scored().to_parquet(scored, index=False)
    transit = tmp_path / "transit.csv"
    pd.DataFrame([{
        "station_name": "X", "line": "L1", "latitude": 19.1,
        "longitude": 72.9, "status": "operational", "opening_date": "2014-06-08",
    }]).to_csv(transit, index=False)
    config = tmp_path / "city.yaml"
    config.write_text("city: t\ndisplay_name: T\nbounding_box: {}\n", encoding="utf-8")

    canonical = tmp_path / "api"
    published = tmp_path / "docs" / "api"
    run(scored, transit, config, canonical, publish_dirs=[published])

    # both copies must be byte-identical
    for name in ["index.json", "meta.json", "locality_mispricing.json"]:
        assert (canonical / name).read_bytes() == (published / name).read_bytes()
