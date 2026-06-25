/**
 * The signal axis: map a mispricing residual (% above/below fair value) to a
 * color and a tone. This is the single mapping every surface uses — skylines,
 * the Spread, locality fields on the map, the Verdict cards — so the encoding
 * is identical everywhere.
 *
 * Colors come from the locked token ramp (lib/tokens). Tone mirrors the
 * backend contract's ±5% band semantics (export.py `_signal`).
 */
import { tokens } from '@/lib/tokens/tokens';

export type SignalTone = 'underpriced' | 'fair' | 'overpriced';

/** Diverging color for a residual %, intensifying with magnitude. */
export function signalColor(residualPct: number): string {
  const s = tokens.signal;
  if (residualPct < -20) return s.under3;
  if (residualPct < -10) return s.under2;
  if (residualPct < -5) return s.under1;
  if (residualPct <= 5) return s.fair;
  if (residualPct < 10) return s.over1;
  if (residualPct < 20) return s.over2;
  return s.over3;
}

/** Categorical tone with the ±5% fair band, matching the contract `signal`. */
export function signalTone(residualPct: number): SignalTone {
  if (residualPct > 5) return 'overpriced';
  if (residualPct < -5) return 'underpriced';
  return 'fair';
}

/** Human label for a tone, e.g. for the Verdict badge. */
export function signalLabel(tone: SignalTone): string {
  return tone === 'underpriced'
    ? 'Underpriced'
    : tone === 'overpriced'
      ? 'Overpriced'
      : 'Fair';
}
