import { NumberFlowValue } from '@/features/number/NumberFlowValue';
import { signalColor } from '@/lib/signal/scale';

/**
 * The Spread — the Dossier hero. Asking and fair rent on one axis anchored at
 * the fair-value datum (center). A colored segment grows from center toward
 * the asking side, its length proportional to the residual; the signed % is
 * the largest object on the surface.
 */
const MAX_PCT = 40; // axis half-range; clamps extreme residuals into view
const HALF_EXTENT = 40; // % of track width each side of center

function clampLabel(pos: number): number {
  return Math.max(10, Math.min(90, pos));
}

export interface SpreadBarProps {
  askingRent: number;
  fairRent: number;
  residualPct: number;
}

export function SpreadBar({ askingRent, fairRent, residualPct }: SpreadBarProps) {
  const color = signalColor(residualPct);
  const clamped = Math.max(-MAX_PCT, Math.min(MAX_PCT, residualPct));
  const center = 50;
  const endPos = center + (clamped / MAX_PCT) * HALF_EXTENT;
  const fillLeft = Math.min(center, endPos);
  const fillWidth = Math.abs(endPos - center);

  return (
    <section aria-label="Fair-value spread">
      <div
        style={{
          fontFamily: 'var(--rl-font-mono)',
          fontSize: 'var(--rl-font-size-64)',
          fontWeight: 'var(--rl-font-weight-medium)',
          lineHeight: 1,
          color,
        }}
      >
        <NumberFlowValue
          value={residualPct}
          kind="signedPct"
          aria-label={`${residualPct.toFixed(1)} percent versus fair value`}
        />
      </div>
      <p
        style={{
          margin: '8px 0 28px',
          fontSize: 'var(--rl-font-size-13)',
          color: 'var(--rl-color-text-lo)',
        }}
      >
        median asking rent vs modeled fair value
      </p>

      <div
        style={{
          position: 'relative',
          height: 12,
          borderRadius: 999,
          background: 'var(--rl-color-surface-2)',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: 0,
            bottom: 0,
            left: `${fillLeft}%`,
            width: `${fillWidth}%`,
            borderRadius: 999,
            background: color,
            opacity: 0.9,
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: -4,
            bottom: -4,
            left: `${center}%`,
            width: 2,
            transform: 'translateX(-50%)',
            background: 'var(--rl-color-line)',
          }}
          aria-hidden
        />
      </div>

      <div style={{ position: 'relative', height: 44, marginTop: 10 }}>
        <Endpoint
          left={clampLabel(endPos)}
          name="Asking"
          value={askingRent}
          accent={color}
        />
        <Endpoint left={clampLabel(center)} name="Fair value" value={fairRent} />
      </div>
    </section>
  );
}

function Endpoint({
  left,
  name,
  value,
  accent,
}: {
  left: number;
  name: string;
  value: number;
  accent?: string;
}) {
  return (
    <div
      style={{
        position: 'absolute',
        left: `${left}%`,
        transform: 'translateX(-50%)',
        textAlign: 'center',
        whiteSpace: 'nowrap',
      }}
    >
      <div style={{ fontSize: 'var(--rl-font-size-12)', color: 'var(--rl-color-text-lo)' }}>
        {name}
      </div>
      <div
        style={{
          fontFamily: 'var(--rl-font-mono)',
          fontSize: 'var(--rl-font-size-15)',
          color: accent ?? 'var(--rl-color-text-hi)',
        }}
      >
        <NumberFlowValue value={value} kind="rent" />
      </div>
    </div>
  );
}
