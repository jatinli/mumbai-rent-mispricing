# RentLens Frontend

This directory is the **frontend workspace** — owned by the frontend developer.
Pick whatever stack you like (React, Vue, Svelte, plain JS…); nothing outside
this directory needs to know.

## The data contract (your input)

The backend publishes a small, fixed set of **aggregates-only** JSON files at
[`../data/api/`](../data/api/). That is your entire interface to the backend —
you never need to run Python, the pipeline, or touch `src/`. See
[`../data/api/README.md`](../data/api/README.md) for the exact shape of each
file:

| File | What it is |
|------|------------|
| `meta.json` | provenance + map bounding box + locality list |
| `locality_mispricing.json` | the headline finding, one row per locality |
| `arbitrage_summary.json` | per-locality arbitrage counts/medians |
| `transit.json` | metro/rail stations to draw |

Those files are committed to the repo, so you can read them directly (fetch at
runtime, or import at build time — your call).

## Privacy boundary (please keep)

The contract is **aggregates only by design** — there is no per-listing data in
it, and there must never be. Don't try to source per-listing rent/location data
into a publicly deployed build. If you need a field the contract doesn't expose,
ask the backend owner to add it to the exporter rather than scraping or
hardcoding it.

## Deploying

The public site is served from `../docs/` via GitHub Pages today (currently the
synthetic map). When your build is ready, coordinate with the backend owner on
how the built assets land in `docs/` — that's the one shared touchpoint between
frontend and backend.

## Suggested local workflow

```bash
# from this directory, once you've scaffolded your app of choice, e.g.:
#   npm create vite@latest .
#   npm install && npm run dev
# point your data loader at ../data/api/*.json
```
