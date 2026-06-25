-- RentLens canonical listings schema (PostgreSQL).
-- GENERATED from src/rentlens/schema.py - do not edit by hand;
-- run `python -m rentlens.schema` to regenerate.
--
-- PRIVACY: this is the PRIVATE per-listing store. Per-listing rows are
-- never published; only aggregates derived from them ship publicly.

CREATE TABLE IF NOT EXISTS sources (
    source            TEXT PRIMARY KEY,
    base_url          TEXT,
    robots_checked_at TIMESTAMPTZ,
    notes             TEXT
);

CREATE TABLE IF NOT EXISTS listings (
    listing_id             TEXT PRIMARY KEY NOT NULL,  -- Canonical unique id for the (deduplicated) listing.
    source                 TEXT NOT NULL,  -- Source site key, e.g. MAGICBRICKS, SYNTHETIC_GENERATED.
    source_listing_id      TEXT,  -- The source site's own listing id, if exposed.
    listing_url            TEXT,  -- Canonical URL of the listing on the source site.
    scrape_timestamp       TIMESTAMPTZ NOT NULL,  -- UTC time the record was scraped.
    first_seen             TIMESTAMPTZ,  -- First scrape that observed this listing (snapshot history).
    last_seen              TIMESTAMPTZ,  -- Most recent scrape that observed this listing (snapshot history).
    listing_status         TEXT,  -- active | removed | unknown.
    title                  TEXT,  -- Listing headline text.
    property_type          TEXT,  -- apartment | independent | studio | ...
    bhk                    INTEGER,  -- Bedrooms (Indian 'BHK' convention; bhk == bedrooms).
    bathrooms              DOUBLE PRECISION,  -- Number of bathrooms.
    carpet_area_sqft       DOUBLE PRECISION,  -- Carpet (interior usable) area in square feet.
    super_area_sqft        DOUBLE PRECISION,  -- Super built-up area in square feet, when distinguished from carpet.
    area_is_estimated      BOOLEAN,  -- True if carpet area was estimated from super area via the loading factor.
    furnishing             TEXT,  -- unfurnished | semi | furnished.
    floor                  DOUBLE PRECISION,  -- Floor of the unit (0 = ground, -1 = basement).
    total_floors           DOUBLE PRECISION,  -- Total floors in the building.
    building_age_years     DOUBLE PRECISION,  -- Approx building age in years, when stated.
    amenities_count        INTEGER,  -- Count of amenities.
    amenities              JSONB,  -- Array of amenity strings.
    pet_policy             TEXT,  -- Stated pet policy, if any.
    parking                TEXT,  -- Parking description, if any.
    availability_date      DATE,  -- Date the unit is available from, if stated.
    monthly_rent           DOUBLE PRECISION NOT NULL,  -- Monthly rent in INR.
    deposit                DOUBLE PRECISION,  -- Security deposit in INR, if disclosed.
    city                   TEXT,  -- City, e.g. Mumbai.
    locality               TEXT NOT NULL,  -- Canonical locality bucket used in analysis.
    neighborhood           TEXT,  -- Source-reported sub-locality / neighborhood.
    full_address           TEXT,  -- PII. Full street address.
    postal_code            TEXT,  -- Postal / PIN code.
    latitude               DOUBLE PRECISION NOT NULL,  -- WGS84 latitude (building/society level, not per-unit).
    longitude              DOUBLE PRECISION NOT NULL,  -- WGS84 longitude.
    description            TEXT,  -- Free-text listing description (source's copyright).
    image_urls             JSONB,  -- Array of image URLs (URLs only; images are never rehosted).
    landlord_name          TEXT,  -- PII. Landlord / agent name if publicly shown.
    listing_date           DATE,  -- Date the listing was posted, if stated.
    last_updated_date      DATE,  -- Date the listing was last updated, if stated.
    completeness_score     DOUBLE PRECISION,  -- 0-1 fraction of key fields populated.
    confidence             JSONB,  -- Per-field extraction confidence scores.
    quality_flags          JSONB  -- Array of suspicious-listing flags (e.g. missing_address, unrealistic_rent).
    , FOREIGN KEY (source) REFERENCES sources (source)
);

CREATE INDEX IF NOT EXISTS idx_listings_locality ON listings (locality);
CREATE INDEX IF NOT EXISTS idx_listings_source   ON listings (source);
CREATE INDEX IF NOT EXISTS idx_listings_rent     ON listings (monthly_rent);
