import { TheLine } from '@/features/line/TheLine';
import { PeakTag } from '@/features/skyline/PeakTag';
import { SkylineField, SKYLINE_LINE_Y } from '@/features/skyline/SkylineField';
import type { LocalityVM } from '@/lib/contract/normalize';

/**
 * HorizonStage — the three skylines against one shared Line. Localities arrive
 * residual-sorted (most overpriced left, the submerged underpriced one right).
 * The Line overlays the skyline block at the same SKYLINE_LINE_Y the towers are
 * measured against, so a single datum reads across all three.
 */
export interface HorizonStageProps {
  localities: LocalityVM[];
}

export function HorizonStage({ localities }: HorizonStageProps) {
  return (
    <div style={{ width: '100%' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          height: 52,
          marginBottom: 8,
        }}
      >
        {localities.map((l) => (
          <div key={l.slug} style={{ flex: 1 }}>
            <PeakTag name={l.name} residualPct={l.residualPct} />
          </div>
        ))}
      </div>

      <div style={{ position: 'relative', height: 'clamp(220px, 32vh, 320px)' }}>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', gap: 18 }}>
          {localities.map((l) => (
            <div key={l.slug} style={{ flex: 1, height: '100%' }}>
              <SkylineField name={l.name} pctOverpriced={l.pctOverpriced} />
            </div>
          ))}
        </div>
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: `${SKYLINE_LINE_Y}%`,
          }}
        >
          <TheLine thickness={1.5} durationMs={1100} />
        </div>
      </div>
    </div>
  );
}
