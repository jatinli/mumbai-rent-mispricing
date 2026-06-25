import { NumberFlowValue } from '@/features/number/NumberFlowValue';
import { signalColor } from '@/lib/signal/scale';

/**
 * PeakTag — the small label above a skyline: locality name and its signed
 * residual, the figure odometer-rolling in the signal color.
 */
export interface PeakTagProps {
  name: string;
  residualPct: number;
}

export function PeakTag({ name, residualPct }: PeakTagProps) {
  return (
    <div style={{ textAlign: 'center', lineHeight: 1.2 }}>
      <div
        style={{
          fontFamily: 'var(--rl-font-ui)',
          fontSize: 'var(--rl-font-size-13)',
          color: 'var(--rl-color-text-hi)',
        }}
      >
        {name}
      </div>
      <div
        style={{
          fontFamily: 'var(--rl-font-mono)',
          fontSize: 'var(--rl-font-size-15)',
          color: signalColor(residualPct),
        }}
      >
        <NumberFlowValue value={residualPct} kind="signedPct" />
      </div>
    </div>
  );
}
