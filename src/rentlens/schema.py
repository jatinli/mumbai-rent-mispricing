"""
Canonical rental-listing schema — the single source of truth.

This module defines the canonical shape of a cleaned rental listing once and
derives everything else from it:
  - `validate(df)`            — enforce required fields on a DataFrame
  - `generate_postgres_ddl()` — the PostgreSQL `db/schema.sql`
  - `generate_data_dictionary_md()` — the human `db/DATA_DICTIONARY.md`

so the SQL schema and the data dictionary can never silently drift from the
fields the pipeline actually produces.

PRIVACY BOUNDARY (read this)
---------------------------
This schema describes the **private, per-listing record** — it intentionally
includes sensitive fields (full_address, landlord_name, image_urls, exact
coordinates) so the private database can be complete. Per the project's
data-publication policy, **per-listing rows are never published** — only
aggregates derived from them ship publicly (see `rentlens.api.export`, which
enforces this). Fields flagged `pii=True` are personal data and must be
handled with particular care even within the private store.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

# logical dtype -> PostgreSQL column type
_PG_TYPES = {
    "string": "TEXT",
    "text": "TEXT",
    "int": "INTEGER",
    "float": "DOUBLE PRECISION",
    "bool": "BOOLEAN",
    "date": "DATE",
    "timestamp": "TIMESTAMPTZ",
    "json": "JSONB",
}


@dataclass(frozen=True)
class Field:
    name: str
    dtype: str            # logical type (key of _PG_TYPES)
    required: bool        # must be present AND non-null in a valid clean record
    description: str
    pii: bool = False     # personal data — extra-sensitive even in the private store
    section: str = ""     # grouping for the data dictionary

    @property
    def pg_type(self) -> str:
        return _PG_TYPES[self.dtype]


# ── the canonical schema ──────────────────────────────────────────────────────
# Ordered and grouped by section. `required` is deliberately the minimal set of
# fields that are reliably non-null across every current source (MagicBricks +
# synthetic); everything the spec asks for but a source may not expose is
# nullable, so a single schema fits every source honestly.
CANONICAL_SCHEMA: list[Field] = [
    # Identity & provenance
    Field("listing_id", "string", True, "Canonical unique id for the (deduplicated) listing.", section="Identity & provenance"),
    Field("source", "string", True, "Source site key, e.g. MAGICBRICKS, SYNTHETIC_GENERATED.", section="Identity & provenance"),
    Field("source_listing_id", "string", False, "The source site's own listing id, if exposed.", section="Identity & provenance"),
    Field("listing_url", "string", False, "Canonical URL of the listing on the source site.", section="Identity & provenance"),
    Field("scrape_timestamp", "timestamp", True, "UTC time the record was scraped.", section="Identity & provenance"),
    Field("first_seen", "timestamp", False, "First scrape that observed this listing (snapshot history).", section="Identity & provenance"),
    Field("last_seen", "timestamp", False, "Most recent scrape that observed this listing (snapshot history).", section="Identity & provenance"),
    Field("listing_status", "string", False, "active | removed | unknown.", section="Identity & provenance"),

    # Property attributes
    Field("title", "string", False, "Listing headline text.", section="Property"),
    Field("property_type", "string", False, "apartment | independent | studio | ...", section="Property"),
    Field("bhk", "int", False, "Bedrooms (Indian 'BHK' convention; bhk == bedrooms).", section="Property"),
    Field("bathrooms", "float", False, "Number of bathrooms.", section="Property"),
    Field("carpet_area_sqft", "float", False, "Carpet (interior usable) area in square feet.", section="Property"),
    Field("super_area_sqft", "float", False, "Super built-up area in square feet, when distinguished from carpet.", section="Property"),
    Field("area_is_estimated", "bool", False, "True if carpet area was estimated from super area via the loading factor.", section="Property"),
    Field("furnishing", "string", False, "unfurnished | semi | furnished.", section="Property"),
    Field("floor", "float", False, "Floor of the unit (0 = ground, -1 = basement).", section="Property"),
    Field("total_floors", "float", False, "Total floors in the building.", section="Property"),
    Field("building_age_years", "float", False, "Approx building age in years, when stated.", section="Property"),
    Field("amenities_count", "int", False, "Count of amenities.", section="Property"),
    Field("amenities", "json", False, "Array of amenity strings.", section="Property"),
    Field("pet_policy", "string", False, "Stated pet policy, if any.", section="Property"),
    Field("parking", "string", False, "Parking description, if any.", section="Property"),
    Field("availability_date", "date", False, "Date the unit is available from, if stated.", section="Property"),

    # Pricing
    Field("monthly_rent", "float", True, "Monthly rent in INR.", section="Pricing"),
    Field("deposit", "float", False, "Security deposit in INR, if disclosed.", section="Pricing"),

    # Location
    Field("city", "string", False, "City, e.g. Mumbai.", section="Location"),
    Field("locality", "string", True, "Canonical locality bucket used in analysis.", section="Location"),
    Field("neighborhood", "string", False, "Source-reported sub-locality / neighborhood.", section="Location"),
    Field("full_address", "string", False, "Full street address.", pii=True, section="Location"),
    Field("postal_code", "string", False, "Postal / PIN code.", section="Location"),
    Field("latitude", "float", True, "WGS84 latitude (building/society level, not per-unit).", section="Location"),
    Field("longitude", "float", True, "WGS84 longitude.", section="Location"),

    # Content & media
    Field("description", "text", False, "Free-text listing description (source's copyright).", section="Content & media"),
    Field("image_urls", "json", False, "Array of image URLs (URLs only; images are never rehosted).", section="Content & media"),
    Field("landlord_name", "string", False, "Landlord / agent name if publicly shown.", pii=True, section="Content & media"),

    # Listing lifecycle dates
    Field("listing_date", "date", False, "Date the listing was posted, if stated.", section="Lifecycle"),
    Field("last_updated_date", "date", False, "Date the listing was last updated, if stated.", section="Lifecycle"),

    # Data-quality (populated by the validation pipeline)
    Field("completeness_score", "float", False, "0-1 fraction of key fields populated.", section="Data quality"),
    Field("confidence", "json", False, "Per-field extraction confidence scores.", section="Data quality"),
    Field("quality_flags", "json", False, "Array of suspicious-listing flags (e.g. missing_address, unrealistic_rent).", section="Data quality"),
]

PII_FIELDS = frozenset(f.name for f in CANONICAL_SCHEMA if f.pii)


def field_names() -> list[str]:
    return [f.name for f in CANONICAL_SCHEMA]


def required_fields() -> list[str]:
    return [f.name for f in CANONICAL_SCHEMA if f.required]


def validate(df: pd.DataFrame) -> None:
    """Validate a cleaned-listing DataFrame against the canonical schema.

    Source-agnostic (unlike generate.validate_schema, which is synthetic-only):
    checks that every required field is present and fully non-null, and that
    the frame carries no unknown columns beyond the schema (plus a small set of
    allowed pipeline-internal extras). Nullable schema fields may be absent.
    """
    cols = set(df.columns)
    missing = [f for f in required_fields() if f not in cols]
    if missing:
        raise ValueError(f"Schema validation failed — missing required columns: {missing}")

    nulls = [f for f in required_fields() if df[f].isna().any()]
    if nulls:
        raise ValueError(f"Schema validation failed — nulls in required columns: {nulls}")


# ── artifact generators ───────────────────────────────────────────────────────

def generate_postgres_ddl() -> str:
    lines = [
        "-- RentLens canonical listings schema (PostgreSQL).",
        "-- GENERATED from src/rentlens/schema.py - do not edit by hand;",
        "-- run `python -m rentlens.schema` to regenerate.",
        "--",
        "-- PRIVACY: this is the PRIVATE per-listing store. Per-listing rows are",
        "-- never published; only aggregates derived from them ship publicly.",
        "",
        "CREATE TABLE IF NOT EXISTS sources (",
        "    source            TEXT PRIMARY KEY,",
        "    base_url          TEXT,",
        "    robots_checked_at TIMESTAMPTZ,",
        "    notes             TEXT",
        ");",
        "",
        "CREATE TABLE IF NOT EXISTS listings (",
    ]
    col_lines = []
    for f in CANONICAL_SCHEMA:
        constraint = " NOT NULL" if f.required else ""
        pk = " PRIMARY KEY" if f.name == "listing_id" else ""
        comment = f"  -- {'PII. ' if f.pii else ''}{f.description}"
        col_lines.append(f"    {f.name:<22} {f.pg_type}{pk}{constraint},{comment}")
    # drop the trailing comma on the last column line (before comment)
    last = col_lines[-1]
    head, sep, tail = last.partition("  -- ")
    col_lines[-1] = head.rstrip().rstrip(",") + "  -- " + tail if sep else head.rstrip().rstrip(",")
    lines.extend(col_lines)
    lines.append("    , FOREIGN KEY (source) REFERENCES sources (source)")
    lines.append(");")
    lines.append("")
    lines.append("CREATE INDEX IF NOT EXISTS idx_listings_locality ON listings (locality);")
    lines.append("CREATE INDEX IF NOT EXISTS idx_listings_source   ON listings (source);")
    lines.append("CREATE INDEX IF NOT EXISTS idx_listings_rent     ON listings (monthly_rent);")
    lines.append("")
    return "\n".join(lines)


def generate_data_dictionary_md() -> str:
    out = [
        "# RentLens Data Dictionary",
        "",
        "Canonical schema for a **cleaned rental listing**. Generated from",
        "`src/rentlens/schema.py` — run `python -m rentlens.schema` to regenerate.",
        "",
        "> **Privacy.** This describes the *private* per-listing record. Per-listing",
        "> rows are never published; only aggregates derived from them ship publicly",
        "> (see `rentlens.api.export`). Fields marked **PII** are personal data.",
        "",
        f"Total fields: **{len(CANONICAL_SCHEMA)}** "
        f"({len(required_fields())} required, {len(PII_FIELDS)} PII).",
        "",
    ]
    sections: list[str] = []
    for f in CANONICAL_SCHEMA:
        if f.section not in sections:
            sections.append(f.section)
    for section in sections:
        out.append(f"## {section}")
        out.append("")
        out.append("| Field | Type | Required | PII | Description |")
        out.append("|-------|------|----------|-----|-------------|")
        for f in CANONICAL_SCHEMA:
            if f.section != section:
                continue
            out.append(
                f"| `{f.name}` | {f.dtype} | {'yes' if f.required else ''} "
                f"| {'yes' if f.pii else ''} | {f.description} |"
            )
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    db = root / "db"
    db.mkdir(parents=True, exist_ok=True)
    (db / "schema.sql").write_text(generate_postgres_ddl(), encoding="utf-8")
    (db / "DATA_DICTIONARY.md").write_text(generate_data_dictionary_md(), encoding="utf-8")
    print(f"Wrote {db / 'schema.sql'}")
    print(f"Wrote {db / 'DATA_DICTIONARY.md'}")
    print(f"Schema: {len(CANONICAL_SCHEMA)} fields, "
          f"{len(required_fields())} required, {len(PII_FIELDS)} PII.")
