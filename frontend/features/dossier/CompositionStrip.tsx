import { NumberFlowValue } from '@/features/number/NumberFlowValue';

/**
 * The Composition — a miniature skyline against the Line. Each tower is a
 * listing band; the share rendered in ember (above the line) equals the real
 * pct_overpriced, the rest in jade (below). The motif recurs as data, not
 * decoration.
 */
const TOWERS = 40;

/** Deterministic per-index height jitter so the skyline reads as a ridge. */
function towerHeight(i: number): number {
  const wave = Math.sin(i * 1.7) * 0.5 + Math.sin(i * 0.6) * 0.5;
  return 52 + (wave + 1) * 18; // 52..88%
}

export function CompositionStrip({ pctOverpriced }: { pctOverpriced: number }) {
  const overCount = Math.round((pctOverpriced / 100) * TOWERS);

  return (
    <section aria-label="Share of listings above fair value">
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          marginBottom: 12,
        }}
      >
        <span style={{ fontSize: 'var(--rl-font-size-13)', color: 'var(--rl-color-text-lo)' }}>
          Listings above fair value
        </span>
        <span
          style={{
            fontFamily: 'var(--rl-font-mono)',
            fontSize: 'var(--rl-font-size-18)',
            color: 'var(--rl-color-text-hi)',
          }}
        >
          <NumberFlowValue value={pctOverpriced} kind="pct" />
        </span>
      </div>

      <div
        style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'flex-end',
          gap: 3,
          height: 64,
        }}
      >
        {Array.from({ length: TOWERS }, (_, i) => {
          const isOver = i < overCount;
          return (
            <span
              key={i}
              style={{
                flex: 1,
                height: `${towerHeight(i)}%`,
                borderRadius: 2,
                background: isOver
                  ? 'var(--rl-signal-over-2)'
                  : 'var(--rl-signal-under-3)',
                opacity: 0.92,
              }}
            />
          );
        })}
        <span
          aria-hidden
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            bottom: '46%',
            height: 1,
            background: 'var(--rl-color-line)',
            opacity: 0.5,
          }}
        />
      </div>
    </section>
  );
}
