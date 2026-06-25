/**
 * Zod schemas mirroring the public data contract (data/api/*.json).
 *
 * These are the frontend's enforcement of the contract: parsing through them
 * fails loudly if the backend ever changes a field shape, which is exactly the
 * "treat the contract as stable" guarantee from the build spec. Inferred types
 * are the raw (snake_case) shapes; normalization (normalize.ts) turns them into
 * camelCase view-models.
 */
import { z } from 'zod';

export const BoundingBoxSchema = z.object({
  lat_min: z.number(),
  lat_max: z.number(),
  lon_min: z.number(),
  lon_max: z.number(),
});

export const MetaSchema = z.object({
  city: z.string(),
  display_name: z.string(),
  bounding_box: BoundingBoxSchema,
  source: z.array(z.string()),
  scrape_date: z.string().nullable(),
  n_listings: z.number().int().nonnegative(),
  localities: z.array(z.string()),
  generated_at: z.string(),
  disclaimer: z.string(),
});

export const SignalSchema = z.enum(['OVERPRICED', 'UNDERPRICED', 'FAIR']);

export const LocalityMispricingSchema = z.object({
  locality: z.string(),
  n: z.number().int().nonnegative(),
  median_rent: z.number(),
  fair_rent_cross_market: z.number(),
  residual_pct: z.number(),
  pct_overpriced: z.number(),
  signal: SignalSchema,
});
export const LocalityMispricingListSchema = z.array(LocalityMispricingSchema);

export const ArbitrageSummarySchema = z.object({
  locality: z.string(),
  n_candidates: z.number().int().nonnegative(),
  median_discount_pct: z.number(),
});
export const ArbitrageSummaryListSchema = z.array(ArbitrageSummarySchema);

export const TransitStatusSchema = z.enum([
  'operational',
  'under_construction',
  'planned',
]);

export const TransitStationSchema = z.object({
  station_name: z.string(),
  line: z.string(),
  latitude: z.number(),
  longitude: z.number(),
  status: TransitStatusSchema,
  opening_date: z.string().nullable(),
});
export const TransitListSchema = z.array(TransitStationSchema);

export type RawMeta = z.infer<typeof MetaSchema>;
export type RawLocalityMispricing = z.infer<typeof LocalityMispricingSchema>;
export type RawArbitrageSummary = z.infer<typeof ArbitrageSummarySchema>;
export type RawTransitStation = z.infer<typeof TransitStationSchema>;
export type TransitStatus = z.infer<typeof TransitStatusSchema>;
export type Signal = z.infer<typeof SignalSchema>;
