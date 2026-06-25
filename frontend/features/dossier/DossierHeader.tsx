import { TheLine } from '@/features/line/TheLine';
import { VerdictBadge } from '@/features/verdict/VerdictBadge';
import type { LocalityVM } from '@/lib/contract/normalize';

/**
 * Dossier header — the locality name in serif, the verdict badge, and the Line
 * rule beneath. The Line is the same motif drawn on every surface.
 */
export interface DossierHeaderProps {
  locality: LocalityVM;
  cityName: string;
}

export function DossierHeader({ locality, cityName }: DossierHeaderProps) {
  return (
    <header>
      <div
        style={{
          fontSize: 'var(--rl-font-size-12)',
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
          color: 'var(--rl-color-text-lo)',
          marginBottom: 10,
        }}
      >
        {cityName} · fair-value lens
      </div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 16,
          marginBottom: 16,
        }}
      >
        <h1
          style={{
            margin: 0,
            fontFamily: 'var(--rl-font-serif)',
            fontWeight: 'var(--rl-font-weight-regular)',
            fontSize: 'var(--rl-font-size-40)',
            lineHeight: 1.1,
            color: 'var(--rl-color-text-hi)',
          }}
        >
          {locality.name}
        </h1>
        <VerdictBadge tone={locality.tone} />
      </div>
      <TheLine thickness={1.5} />
    </header>
  );
}
