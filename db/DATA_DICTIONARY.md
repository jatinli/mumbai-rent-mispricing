# RentLens Data Dictionary

Canonical schema for a **cleaned rental listing**. Generated from
`src/rentlens/schema.py` — run `python -m rentlens.schema` to regenerate.

> **Privacy.** This describes the *private* per-listing record. Per-listing
> rows are never published; only aggregates derived from them ship publicly
> (see `rentlens.api.export`). Fields marked **PII** are personal data.

Total fields: **41** (7 required, 2 PII).

## Identity & provenance

| Field | Type | Required | PII | Description |
|-------|------|----------|-----|-------------|
| `listing_id` | string | yes |  | Canonical unique id for the (deduplicated) listing. |
| `source` | string | yes |  | Source site key, e.g. MAGICBRICKS, SYNTHETIC_GENERATED. |
| `source_listing_id` | string |  |  | The source site's own listing id, if exposed. |
| `listing_url` | string |  |  | Canonical URL of the listing on the source site. |
| `scrape_timestamp` | timestamp | yes |  | UTC time the record was scraped. |
| `first_seen` | timestamp |  |  | First scrape that observed this listing (snapshot history). |
| `last_seen` | timestamp |  |  | Most recent scrape that observed this listing (snapshot history). |
| `listing_status` | string |  |  | active | removed | unknown. |

## Property

| Field | Type | Required | PII | Description |
|-------|------|----------|-----|-------------|
| `title` | string |  |  | Listing headline text. |
| `property_type` | string |  |  | apartment | independent | studio | ... |
| `bhk` | int |  |  | Bedrooms (Indian 'BHK' convention; bhk == bedrooms). |
| `bathrooms` | float |  |  | Number of bathrooms. |
| `carpet_area_sqft` | float |  |  | Carpet (interior usable) area in square feet. |
| `super_area_sqft` | float |  |  | Super built-up area in square feet, when distinguished from carpet. |
| `area_is_estimated` | bool |  |  | True if carpet area was estimated from super area via the loading factor. |
| `furnishing` | string |  |  | unfurnished | semi | furnished. |
| `floor` | float |  |  | Floor of the unit (0 = ground, -1 = basement). |
| `total_floors` | float |  |  | Total floors in the building. |
| `building_age_years` | float |  |  | Approx building age in years, when stated. |
| `amenities_count` | int |  |  | Count of amenities. |
| `amenities` | json |  |  | Array of amenity strings. |
| `pet_policy` | string |  |  | Stated pet policy, if any. |
| `parking` | string |  |  | Parking description, if any. |
| `availability_date` | date |  |  | Date the unit is available from, if stated. |

## Pricing

| Field | Type | Required | PII | Description |
|-------|------|----------|-----|-------------|
| `monthly_rent` | float | yes |  | Monthly rent in INR. |
| `deposit` | float |  |  | Security deposit in INR, if disclosed. |

## Location

| Field | Type | Required | PII | Description |
|-------|------|----------|-----|-------------|
| `city` | string |  |  | City, e.g. Mumbai. |
| `locality` | string | yes |  | Canonical locality bucket used in analysis. |
| `neighborhood` | string |  |  | Source-reported sub-locality / neighborhood. |
| `full_address` | string |  | yes | Full street address. |
| `postal_code` | string |  |  | Postal / PIN code. |
| `latitude` | float | yes |  | WGS84 latitude (building/society level, not per-unit). |
| `longitude` | float | yes |  | WGS84 longitude. |

## Content & media

| Field | Type | Required | PII | Description |
|-------|------|----------|-----|-------------|
| `description` | text |  |  | Free-text listing description (source's copyright). |
| `image_urls` | json |  |  | Array of image URLs (URLs only; images are never rehosted). |
| `landlord_name` | string |  | yes | Landlord / agent name if publicly shown. |

## Lifecycle

| Field | Type | Required | PII | Description |
|-------|------|----------|-----|-------------|
| `listing_date` | date |  |  | Date the listing was posted, if stated. |
| `last_updated_date` | date |  |  | Date the listing was last updated, if stated. |

## Data quality

| Field | Type | Required | PII | Description |
|-------|------|----------|-----|-------------|
| `completeness_score` | float |  |  | 0-1 fraction of key fields populated. |
| `confidence` | json |  |  | Per-field extraction confidence scores. |
| `quality_flags` | json |  |  | Array of suspicious-listing flags (e.g. missing_address, unrealistic_rent). |
