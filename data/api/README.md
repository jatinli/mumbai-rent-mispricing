# Frontend Data Contract (`data/api/`)

This directory is the **seam between the backend and the frontend**.

- **Backend writes it** — `python -m rentlens.api.export` regenerates every
  file here from the real scored data.
- **Frontend reads it** — the frontend (in `frontend/`) consumes these static
  JSON files. There is no server.

These files are **aggregates only** and safe to commit and serve publicly. The
export step enforces this in code (`_assert_aggregates_only`): it fails if any
per-listing field (listing_id, latitude/longitude, rent, detail_url, …) ever
leaks into a listing-derived file. Do not hand-edit these files — change the
exporter and regenerate.

> The frontend should treat this contract as **read-only and stable**. If a
> field needs to change, change it in `src/rentlens/api/export.py`, bump the
> note below, and tell the frontend owner — don't edit the JSON by hand.

## Files

### `meta.json` — object
Provenance and the parameters the UI needs to frame the data.
```json
{
  "city": "mumbai",
  "display_name": "Mumbai",
  "bounding_box": { "lat_min": 18.89, "lat_max": 19.35, "lon_min": 72.77, "lon_max": 73.05 },
  "source": ["MAGICBRICKS"],
  "scrape_date": "2026-06-23",
  "n_listings": 573,
  "localities": ["Andheri East", "Mulund", "Powai"],
  "generated_at": "<ISO-8601 UTC>",
  "disclaimer": "Aggregates only. No individual listings are published. …"
}
```

### `locality_mispricing.json` — array (one record per locality)
The headline finding. Sorted by `residual_pct` descending.
```json
{
  "locality": "Powai",
  "n": 218,                       // listings with a fair-rent estimate (the priced set)
  "median_rent": 85000,           // ₹/month
  "fair_rent_cross_market": 73242,// ₹/month, modelled from fundamentals only
  "residual_pct": 14.88,          // median (rent − fair) / fair, %
  "pct_overpriced": 73.9,         // % of listings above fair value
  "signal": "OVERPRICED"          // OVERPRICED | UNDERPRICED | FAIR (±5% band)
}
```

### `arbitrage_summary.json` — array (one record per locality)
Per-locality rollup of underpriced listings near an under-construction station.
Counts and medians only — never the individual candidate rows. Sorted by
`n_candidates` descending.
```json
{
  "locality": "Mulund",
  "n_candidates": 133,            // underpriced AND within 2.5km of a UC station
  "median_discount_pct": -24.94   // median residual_pct of those candidates
}
```

### `transit.json` — array (one record per station)
OpenStreetMap stations — public infrastructure, exposed with coordinates so the
frontend can draw the network.
```json
{
  "station_name": "Powai Lake Station",
  "line": "Metro Line 6",
  "latitude": 19.12,
  "longitude": 72.906,
  "status": "operational",        // operational | under_construction | planned
  "opening_date": null            // "YYYY-MM-DD" or null if unconfirmed
}
```

## Regenerating

```bash
# requires the real scored data on disk (data/processed/listings_scored.parquet),
# which is produced by the real pipeline — see the main README "Reproducing".
python -m rentlens.api.export
```

The committed JSON here is the public face of the real analysis: the per-listing
parquet it is derived from is git-ignored, so these aggregates are the only
representation of the real data that ships.
