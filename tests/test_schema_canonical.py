"""Tests for the canonical schema (rentlens.schema) and its generators.

Ties the schema to the real pipeline: the synthetic generator's output must
satisfy the canonical schema's required fields, so the schema can't drift away
from what the pipeline actually produces.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from rentlens import schema
from rentlens.data.generate import generate_listings

CONFIG = Path(__file__).resolve().parents[1] / "config" / "cities" / "mumbai.yaml"


def test_required_fields_are_a_subset_of_all_fields():
    assert set(schema.required_fields()) <= set(schema.field_names())


def test_listing_id_is_required_and_first():
    assert schema.CANONICAL_SCHEMA[0].name == "listing_id"
    assert "listing_id" in schema.required_fields()


def test_synthetic_data_satisfies_required_schema():
    df = generate_listings(CONFIG, n_total=200, seed=3)
    schema.validate(df)  # must not raise


def test_validate_rejects_missing_required_column():
    df = generate_listings(CONFIG, n_total=50, seed=3).drop(columns=["locality"])
    with pytest.raises(ValueError, match="missing required columns"):
        schema.validate(df)


def test_validate_rejects_null_in_required_column():
    df = generate_listings(CONFIG, n_total=50, seed=3)
    df.loc[0, "monthly_rent"] = None
    with pytest.raises(ValueError, match="nulls in required columns"):
        schema.validate(df)


def test_pii_fields_are_flagged():
    assert "full_address" in schema.PII_FIELDS
    assert "landlord_name" in schema.PII_FIELDS
    # core analytic fields must NOT be marked PII
    assert "monthly_rent" not in schema.PII_FIELDS
    assert "locality" not in schema.PII_FIELDS


def test_ddl_generates_valid_looking_sql():
    ddl = schema.generate_postgres_ddl()
    assert "CREATE TABLE IF NOT EXISTS listings (" in ddl
    assert "listing_id             TEXT PRIMARY KEY NOT NULL" in ddl
    # every field appears as a column
    for name in schema.field_names():
        assert name in ddl
    # no double-comma artifacts from the trailing-comma trimming
    assert ",," not in ddl


def test_data_dictionary_lists_every_field():
    md = schema.generate_data_dictionary_md()
    for name in schema.field_names():
        assert f"`{name}`" in md
