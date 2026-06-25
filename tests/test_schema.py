"""Schema validation tests for the synthetic listing generator."""

import textwrap
from pathlib import Path

import pandas as pd
import pytest

from rentlens.data.generate import generate_listings, validate_schema, planted_signal_check

CONFIG = Path(__file__).resolve().parents[1] / "config" / "cities" / "mumbai.yaml"

REQUIRED_COLUMNS = [
    "listing_id", "source", "scrape_timestamp", "locality",
    "latitude", "longitude", "carpet_area_sqft", "bhk", "bathrooms",
    "furnishing", "floor", "total_floors", "building_age_years",
    "amenities_count", "property_type", "monthly_rent", "deposit",
]


@pytest.fixture(scope="module")
def listings() -> pd.DataFrame:
    return generate_listings(CONFIG, n_total=500, seed=0)


def test_row_count(listings):
    assert len(listings) == 500


def test_required_columns_present(listings):
    for col in REQUIRED_COLUMNS:
        assert col in listings.columns, f"Missing column: {col}"


def test_source_tag(listings):
    assert listings["source"].eq("SYNTHETIC_GENERATED").all()


def test_no_nulls_in_required(listings):
    assert listings[REQUIRED_COLUMNS].isnull().sum().sum() == 0


def test_no_duplicate_listing_ids(listings):
    assert listings.duplicated("listing_id").sum() == 0


def test_rent_positive(listings):
    assert (listings["monthly_rent"] > 0).all()


def test_lat_lon_in_mumbai_range(listings):
    assert listings["latitude"].between(18.5, 19.5).all()
    assert listings["longitude"].between(72.7, 73.2).all()


def test_furnishing_categories(listings):
    valid = {"unfurnished", "semi", "furnished"}
    assert set(listings["furnishing"].unique()).issubset(valid)


def test_property_type_categories(listings):
    valid = {"apartment", "independent"}
    assert set(listings["property_type"].unique()).issubset(valid)


def test_bhk_range(listings):
    assert listings["bhk"].between(1, 5).all()


def test_floor_leq_total_floors(listings):
    assert (listings["floor"] <= listings["total_floors"]).all()


def test_schema_validation_passes(listings):
    validate_schema(listings)


def test_planted_signal_recoverable(listings):
    checks = planted_signal_check(listings)
    for locality, res in checks.items():
        assert res["pass"], (
            f"Planted signal not recovered for {locality}: "
            f"expected {res['expected_bias_pct']:+.1f}%, "
            f"observed {res['observed_bias_pct']:+.2f}%"
        )


def test_non_seven_locality_config_not_truncated(tmp_path):
    """The 'city-as-config' claim requires the generator to honour any number
    of localities — not silently truncate to a hardcoded length-7 weight
    vector. A 3-locality config must produce exactly n_total rows spread
    across all 3 localities.
    """
    cfg = tmp_path / "tinytown.yaml"
    cfg.write_text(textwrap.dedent("""
        city: tinytown
        display_name: Tinytown
        bounding_box: { lat_min: 18.9, lat_max: 19.3, lon_min: 72.8, lon_max: 73.0 }
        localities:
          - { name: Alpha, lat: 19.10, lon: 72.90, base_rent_per_sqft: 60 }
          - { name: Beta,  lat: 19.15, lon: 72.92, base_rent_per_sqft: 50 }
          - { name: Gamma, lat: 19.20, lon: 72.95, base_rent_per_sqft: 45 }
        planted_mispricing: {}
        transit_table: data/reference/transit_mumbai.csv
        spatial_cv_column: locality
    """), encoding="utf-8")

    df = generate_listings(cfg, n_total=300, seed=1)
    assert len(df) == 300
    assert set(df["locality"].unique()) == {"Alpha", "Beta", "Gamma"}
