/**
 * Normalization: raw snake_case contract -> camelCase view-models the UI
 * consumes. This is the boundary between the wire format and the components;
 * nothing past here should touch raw field names.
 *
 * Scale seams (dormant on today's single-snapshot contract):
 *   - LocalityVM.delta is reserved for snapshot-over-snapshot change; null now.
 *   - localities are sorted by residual (the Horizon's ordering primitive), so
 *     three localities read as a triptych today and a ranked ridge at scale.
 */
import { signalTone, type SignalTone } from '@/lib/signal/scale';

import { loadRawContract, type RawContract } from './load';
import type { Signal, TransitStatus } from './schema';
import { toSlug } from './slug';

export interface MetaVM {
  city: string;
  displayName: string;
  boundingBox: { latMin: number; latMax: number; lonMin: number; lonMax: number };
  sources: string[];
  scrapeDate: string | null;
  nListings: number;
  localityNames: string[];
  generatedAt: string;
  disclaimer: string;
}

export interface ArbitrageVM {
  nCandidates: number;
  medianDiscountPct: number;
}

export interface LocalityVM {
  slug: string;
  name: string;
  n: number;
  medianRent: number;
  fairRent: number;
  residualPct: number;
  pctOverpriced: number;
  signal: Signal;
  tone: SignalTone;
  arbitrage: ArbitrageVM | null;
  /** Reserved for historical snapshots; null on a single snapshot. */
  delta: number | null;
}

export interface TransitStationVM {
  stationName: string;
  line: string;
  lat: number;
  lon: number;
  status: TransitStatus;
  openingDate: string | null;
}

export interface ContractData {
  meta: MetaVM;
  localities: LocalityVM[];
  transit: TransitStationVM[];
}

export function normalize(raw: RawContract): ContractData {
  const arbitrageByLocality = new Map<string, ArbitrageVM>(
    raw.arbitrage.map((a) => [
      a.locality,
      { nCandidates: a.n_candidates, medianDiscountPct: a.median_discount_pct },
    ]),
  );

  const localities: LocalityVM[] = raw.localities
    .map((l) => ({
      slug: toSlug(l.locality),
      name: l.locality,
      n: l.n,
      medianRent: l.median_rent,
      fairRent: l.fair_rent_cross_market,
      residualPct: l.residual_pct,
      pctOverpriced: l.pct_overpriced,
      signal: l.signal,
      tone: signalTone(l.residual_pct),
      arbitrage: arbitrageByLocality.get(l.locality) ?? null,
      delta: null,
    }))
    .sort((a, b) => b.residualPct - a.residualPct);

  const meta: MetaVM = {
    city: raw.meta.city,
    displayName: raw.meta.display_name,
    boundingBox: {
      latMin: raw.meta.bounding_box.lat_min,
      latMax: raw.meta.bounding_box.lat_max,
      lonMin: raw.meta.bounding_box.lon_min,
      lonMax: raw.meta.bounding_box.lon_max,
    },
    sources: raw.meta.source,
    scrapeDate: raw.meta.scrape_date,
    nListings: raw.meta.n_listings,
    localityNames: raw.meta.localities,
    generatedAt: raw.meta.generated_at,
    disclaimer: raw.meta.disclaimer,
  };

  const transit: TransitStationVM[] = raw.transit.map((t) => ({
    stationName: t.station_name,
    line: t.line,
    lat: t.latitude,
    lon: t.longitude,
    status: t.status,
    openingDate: t.opening_date,
  }));

  return { meta, localities, transit };
}

/** Convenience: the single most underpriced locality (the headline subject). */
export function mostUnderpriced(localities: LocalityVM[]): LocalityVM | undefined {
  return localities.reduce<LocalityVM | undefined>(
    (min, l) => (min === undefined || l.residualPct < min.residualPct ? l : min),
    undefined,
  );
}

/** Build the full normalized contract from disk. Build/server-only. */
export function loadContract(): ContractData {
  return normalize(loadRawContract());
}
