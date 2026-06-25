/**
 * SkylineField — one locality rendered as a stylized skyline against the Line.
 *
 * The shared fair-value Line sits at `LINE_Y` (drawn by HorizonStage, not here).
 * Each tower rises from the base; the share of towers whose tops break above
 * the Line equals the real pct_overpriced, so an overpriced locality rises in
 * ember and an underpriced one sits submerged in jade. Deterministic per-tower
 * noise gives the ridge its shape (pure server SVG, no animation here).
 */
const TOWERS = 9;
const LINE_Y = 55; // viewBox units from top (must match HorizonStage overlay)
const BASE_Y = 100;

/** Deterministic [0,1) noise from a tower index and a locality seed. */
function noise(i: number, seed: number): number {
  const x = Math.sin((i + 1) * 12.9898 + seed * 78.233) * 43758.5453;
  return x - Math.floor(x);
}

function seedFromName(name: string): number {
  let s = 0;
  for (let i = 0; i < name.length; i += 1) s = (s + name.charCodeAt(i) * (i + 1)) % 997;
  return s;
}

export interface SkylineFieldProps {
  name: string;
  pctOverpriced: number;
}

export function SkylineField({ name, pctOverpriced }: SkylineFieldProps) {
  const seed = seedFromName(name);
  const noises = Array.from({ length: TOWERS }, (_, i) => noise(i, seed));
  const aboveCount = Math.round((pctOverpriced / 100) * TOWERS);

  const sorted = [...noises].sort((a, b) => b - a);
  const threshold = aboveCount > 0 ? sorted[aboveCount - 1]! : Infinity;

  const gap = 2;
  const colW = (100 - gap * (TOWERS - 1)) / TOWERS;

  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      aria-hidden
      style={{ display: 'block', overflow: 'visible' }}
    >
      {noises.map((nv, i) => {
        const isAbove = aboveCount > 0 && nv >= threshold;
        const h = isAbove ? 46 + nv * 38 : 14 + nv * 30;
        const x = i * (colW + gap);
        const y = BASE_Y - h;
        return (
          <rect
            key={i}
            x={x}
            y={y}
            width={colW}
            height={h}
            rx={0.8}
            fill={isAbove ? 'var(--rl-signal-over-2)' : 'var(--rl-signal-under-3)'}
            opacity={0.9}
          />
        );
      })}
    </svg>
  );
}

export const SKYLINE_LINE_Y = LINE_Y;
