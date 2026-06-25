/**
 * Validated contract loader (build/server-only).
 *
 * Reads the four committed JSON files from ../data/api and parses each through
 * its Zod schema, throwing on any drift. Used by the static DataSource (at
 * build time, inside server components) and by the validate-contract script.
 *
 * Path is resolved from process.cwd(), which is the frontend workspace during
 * `next build` and `tsx` script runs. Do not import this from client
 * components — it touches node:fs.
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

import {
  ArbitrageSummaryListSchema,
  LocalityMispricingListSchema,
  MetaSchema,
  TransitListSchema,
  type RawArbitrageSummary,
  type RawLocalityMispricing,
  type RawMeta,
  type RawTransitStation,
} from './schema';

export interface RawContract {
  meta: RawMeta;
  localities: RawLocalityMispricing[];
  arbitrage: RawArbitrageSummary[];
  transit: RawTransitStation[];
}

const API_DIR = resolve(process.cwd(), '..', 'data', 'api');

function readJson(file: string): unknown {
  return JSON.parse(readFileSync(resolve(API_DIR, file), 'utf8'));
}

export function loadRawContract(): RawContract {
  return {
    meta: MetaSchema.parse(readJson('meta.json')),
    localities: LocalityMispricingListSchema.parse(
      readJson('locality_mispricing.json'),
    ),
    arbitrage: ArbitrageSummaryListSchema.parse(
      readJson('arbitrage_summary.json'),
    ),
    transit: TransitListSchema.parse(readJson('transit.json')),
  };
}
