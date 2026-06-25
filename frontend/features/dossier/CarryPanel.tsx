import { NumberFlowValue } from '@/features/number/NumberFlowValue';
import type { ArbitrageVM } from '@/lib/contract/normalize';

/**
 * The Carry — the unpriced metro option. Underpriced listings near an
 * under-construction station: how many, the median discount, and the count of
 * under-construction stations in scope (from the transit contract).
 */
export interface CarryPanelProps {
  arbitrage: ArbitrageVM | null;
  ucStationCount: number;
}

export function CarryPanel({ arbitrage, ucStationCount }: CarryPanelProps) {
  return (
    <section
      aria-label="Transit arbitrage"
      style={{
        background: 'var(--rl-color-surface)',
        border: '1px solid var(--rl-color-hairline)',
        borderRadius: 'var(--rl-radius-lg)',
        padding: '20px 22px',
      }}
    >
      <div
        style={{
          fontSize: 'var(--rl-font-size-12)',
          letterSpacing: '0.03em',
          color: 'var(--rl-color-brand)',
          marginBottom: 14,
        }}
      >
        Carry — unpriced metro option
      </div>

      {arbitrage ? (
        <>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
            <span
              style={{
                fontFamily: 'var(--rl-font-mono)',
                fontSize: 'var(--rl-font-size-40)',
                fontWeight: 'var(--rl-font-weight-medium)',
                color: 'var(--rl-color-text-hi)',
                lineHeight: 1,
              }}
            >
              <NumberFlowValue value={arbitrage.nCandidates} kind="int" />
            </span>
            <span style={{ fontSize: 'var(--rl-font-size-13)', color: 'var(--rl-color-text-lo)' }}>
              candidates
            </span>
          </div>

          <div
            style={{
              fontFamily: 'var(--rl-font-mono)',
              fontSize: 'var(--rl-font-size-15)',
              color: 'var(--rl-signal-under-3)',
              margin: '8px 0 12px',
            }}
          >
            <NumberFlowValue value={arbitrage.medianDiscountPct} kind="signedPct" /> median
            discount
          </div>

          <p style={{ margin: 0, fontSize: 'var(--rl-font-size-13)', color: 'var(--rl-color-text-lo)' }}>
            Underpriced and within 2.5&nbsp;km of one of {ucStationCount} stations under
            construction.
          </p>
        </>
      ) : (
        <p style={{ margin: 0, fontSize: 'var(--rl-font-size-13)', color: 'var(--rl-color-text-lo)' }}>
          No underpriced listings near an under-construction station here.
        </p>
      )}
    </section>
  );
}
