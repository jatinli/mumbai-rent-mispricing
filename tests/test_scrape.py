"""Parser-fixture regression tests for the MagicBricks adapter.

These pin the *current* parsing behavior of rentlens.scrape.magicbricks against a
small, self-contained HTML fixture mirroring the structure the live parser keys
off (div#cardid<N> cards + a positional JSON-LD Apartment array). No network, no
live HTML; tests assert only what the code does today.
"""

from __future__ import annotations

import pytest

from rentlens.scrape.base import CachedFetcher, ScraperAdapter
from rentlens.scrape.magicbricks import (
    MagicBricksAdapter,
    _floor_to_pair,
    _property_type_from_title,
    _rupee_to_number,
)


# ── pure helpers ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("text,expected", [
    ("₹3.5 Lac", 350_000.0),
    ("₹45,000", 45_000.0),
    ("₹1.2 Cr", 12_000_000.0),
    ("₹1.5 Lakh", 150_000.0),
])
def test_rupee_to_number(text, expected):
    assert _rupee_to_number(text) == expected


def test_rupee_to_number_empty_is_none():
    assert _rupee_to_number("") is None
    assert _rupee_to_number(None) is None


def test_rupee_to_number_leading_punctuation_does_not_crash():
    # An unanchored regex ([\d.]+) can match a lone leading "." (e.g. in
    # "Approx. 45000") and crash float(".") — the anchored (\d[\d.]*) pattern
    # plus a try/except must return None instead of raising.
    assert _rupee_to_number("Approx. 45000") == 45000.0
    assert _rupee_to_number("...") is None


def test_floor_to_pair_out_of():
    assert _floor_to_pair("5 out of 10") == (5.0, 10.0)


def test_floor_to_pair_no_match():
    assert _floor_to_pair("Ground") == (None, None)


@pytest.mark.parametrize("title,expected", [
    ("3 BHK Independent House for Rent in Mulund", "independent"),
    ("2 BHK Villa for Rent in Powai", "independent"),
    ("Studio Apartment for Rent in Andheri East", "apartment"),
    ("2 BHK Flat for Rent in Powai", "apartment"),
])
def test_property_type_from_title(title, expected):
    assert _property_type_from_title(title) == expected


def test_property_type_unknown_is_none():
    assert _property_type_from_title("2 BHK Penalty for Rent") is None


# ── search_url ────────────────────────────────────────────────────────────────

def test_search_url_page_one():
    adapter = MagicBricksAdapter()
    assert adapter.search_url("Andheri East", 1) == (
        "https://www.magicbricks.com/flats-for-rent-in-andheri-east-mumbai-pppfr"
    )


def test_search_url_pagination():
    adapter = MagicBricksAdapter()
    assert adapter.search_url("Powai", 3) == (
        "https://www.magicbricks.com/flats-for-rent-in-powai-mumbai-pppfr?page=3"
    )


# ── parse_search_page + to_canonical (HTML fixture) ───────────────────────────

FIXTURE_HTML = """
<html><body>
<script type="application/ld+json">
[{"@type":"Apartment","numberOfRooms":2,
  "address":{"addressLocality":"Powai"},
  "geo":{"latitude":"19.1176","longitude":"72.9060"}}]
</script>
<div id="cardid12345">
  <h2 class="mb-srp__card--title" title="2 BHK Flat for Rent in Powai, Mumbai">2 BHK Flat</h2>
  <div data-summary="carpet-area"><div class="mb-srp__card__summary--value">600 sqft</div></div>
  <div data-summary="floor"><div class="mb-srp__card__summary--value">5 out of 10</div></div>
  <div data-summary="furnishing"><div class="mb-srp__card__summary--value">Semi-Furnished</div></div>
  <div data-summary="bathroom"><div class="mb-srp__card__summary--value">2</div></div>
  <div data-summary="status"><div class="mb-srp__card__summary--value">Immediately</div></div>
  <div class="mb-srp__card__price--amount">&#8377;50,000</div>
  <a class="mb-srp__card__society--name" href="/propertyDetails/abc">Lake Society</a>
</div>
</body></html>
"""


@pytest.fixture(scope="module")
def parsed():
    adapter = MagicBricksAdapter()
    raw = adapter.parse_search_page(FIXTURE_HTML, "Powai")
    canonical = [adapter.to_canonical(r) for r in raw]
    return raw, canonical


def test_parse_finds_single_card(parsed):
    raw, _ = parsed
    assert len(raw) == 1
    assert raw[0]["property_id"] == "12345"
    assert raw[0]["search_locality"] == "Powai"


def test_summary_fields_extracted(parsed):
    raw, _ = parsed
    summary = raw[0]["summary"]
    assert summary["carpet-area"] == "600 sqft"
    assert summary["floor"] == "5 out of 10"
    assert summary["furnishing"] == "Semi-Furnished"


def test_geo_attached_positionally(parsed):
    raw, _ = parsed
    assert raw[0]["geo"]["geo"]["latitude"] == "19.1176"


def test_canonical_core_fields(parsed):
    _, canonical = parsed
    c = canonical[0]
    assert c["listing_id"] == "MAGICBRICKS_12345"
    assert c["source"] == "MAGICBRICKS"
    assert c["bhk"] == 2.0
    assert c["bathrooms"] == 2.0
    assert c["monthly_rent"] == 50_000.0
    assert c["property_type"] == "apartment"


def test_canonical_area_is_carpet(parsed):
    _, canonical = parsed
    c = canonical[0]
    assert c["carpet_area_sqft"] == 600.0
    assert c["area_type_raw"] == "carpet"


def test_canonical_furnishing_mapped(parsed):
    _, canonical = parsed
    c = canonical[0]
    assert c["furnishing"] == "semi"
    assert c["furnishing_raw"] == "Semi-Furnished"


def test_canonical_floor_pair(parsed):
    _, canonical = parsed
    c = canonical[0]
    assert c["floor"] == 5.0
    assert c["total_floors"] == 10.0


def test_canonical_geo_and_locality(parsed):
    _, canonical = parsed
    c = canonical[0]
    assert c["latitude"] == pytest.approx(19.1176)
    assert c["longitude"] == pytest.approx(72.9060)
    assert c["raw_locality"] == "Powai"
    assert c["search_locality"] == "Powai"


def test_canonical_deposit_not_disclosed(parsed):
    _, canonical = parsed
    assert canonical[0]["deposit"] is None


def test_carpet_area_leading_punctuation_does_not_crash():
    html = FIXTURE_HTML.replace(
        '<div data-summary="carpet-area"><div class="mb-srp__card__summary--value">600 sqft</div></div>',
        '<div data-summary="carpet-area"><div class="mb-srp__card__summary--value">Approx. 600 sqft</div></div>',
    )
    adapter = MagicBricksAdapter()
    raw = adapter.parse_search_page(html, "Powai")
    c = adapter.to_canonical(raw[0])
    assert c["carpet_area_sqft"] == 600.0


def test_apartment_jsonld_skips_non_dict_first_element():
    # A JSON-LD array whose first element isn't a dict (e.g. an unrelated
    # array of plain strings) must be skipped, not crash on data[0].get(...).
    html = """
    <html><body>
    <script type="application/ld+json">["not", "a", "dict"]</script>
    <div id="cardid1">
      <h2 class="mb-srp__card--title" title="1 BHK Flat for Rent in Powai">1 BHK</h2>
    </div>
    </body></html>
    """
    adapter = MagicBricksAdapter()
    raw = adapter.parse_search_page(html, "Powai")
    assert raw[0]["geo"] is None


def test_super_area_fallback_sets_area_type():
    """When only super-area is present, area_type_raw flags the fallback and
    carpet_area_sqft is left None (the cleaner applies the loading factor later)."""
    html = FIXTURE_HTML.replace(
        '<div data-summary="carpet-area"><div class="mb-srp__card__summary--value">600 sqft</div></div>',
        '<div data-summary="super-area"><div class="mb-srp__card__summary--value">850 sqft</div></div>',
    )
    adapter = MagicBricksAdapter()
    raw = adapter.parse_search_page(html, "Powai")
    c = adapter.to_canonical(raw[0])
    assert c["area_type_raw"] == "super_area_fallback"
    assert c["carpet_area_sqft"] is None
    assert c["area_sqft_raw"] == 850.0


# ── ScraperAdapter.fetch_listings: null-id dedup safety ────────────────────────

class _FakeAdapter(ScraperAdapter):
    """Pages 1 and 2 each contain one valid-id listing plus one listing whose
    id never parses (None) — page 3 is empty, ending pagination. Without the
    fix, page 1's null-id row marks None as "seen", so page 2's (unrelated)
    null-id row would be wrongly treated as a duplicate and dropped.
    """
    source_name = "FAKE"

    def search_url(self, locality: str, page: int) -> str:
        return f"https://example.test/{locality}/{page}"

    def parse_search_page(self, html: str, locality: str) -> list[dict]:
        if html == "page1":
            return [{"id": "A"}, {"id": None}]
        if html == "page2":
            return [{"id": "B"}, {"id": None}]
        return []

    def to_canonical(self, raw: dict) -> dict:
        return {"listing_id": raw["id"], "locality": "X"}


def test_null_id_rows_not_deduped_against_each_other(tmp_path):
    fetcher = CachedFetcher(tmp_path, min_delay_s=0.0)
    adapter = _FakeAdapter()

    pages = {":1": "page1", ":2": "page2", ":3": "page3"}
    fetcher.get = lambda url, cache_key=None: next(
        v for k, v in pages.items() if cache_key.endswith(k)
    )
    df = adapter.fetch_listings(["Powai"], fetcher, max_pages_per_locality=3)

    assert len(df) == 4  # A, None, B, None — not 3 (which would mean a
    # null-id row got wrongly collapsed as a "duplicate" of the other)
    assert df["listing_id"].isna().sum() == 2
    assert set(df["listing_id"].dropna()) == {"A", "B"}
