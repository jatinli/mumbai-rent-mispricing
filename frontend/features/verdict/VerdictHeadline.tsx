import type { LocalityVM } from '@/lib/contract/normalize';

/**
 * The Verdict ruling — data-derived, never hand-written, so it works for any
 * locality (and any future city) with no copy changes. This is the scale seam
 * the build spec calls out: the headline is a template filled by the data.
 */
export function verdictRuling(locality: LocalityVM): string {
  if (locality.tone === 'underpriced') {
    return `The market is underpricing ${locality.name}.`;
  }
  if (locality.tone === 'overpriced') {
    return `The market is overpricing ${locality.name}.`;
  }
  return `${locality.name} is priced about right.`;
}

export interface VerdictHeadlineProps {
  locality: LocalityVM;
  fontSize?: string;
}

export function VerdictHeadline({
  locality,
  fontSize = 'var(--rl-font-size-28)',
}: VerdictHeadlineProps) {
  return (
    <p
      style={{
        margin: 0,
        fontFamily: 'var(--rl-font-serif)',
        fontWeight: 'var(--rl-font-weight-regular)',
        fontSize,
        lineHeight: 1.2,
        color: 'var(--rl-color-text-hi)',
      }}
    >
      {verdictRuling(locality)}
    </p>
  );
}
