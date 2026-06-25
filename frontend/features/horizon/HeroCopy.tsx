/**
 * HeroCopy — the Verdict's voice on the Horizon. Data-derived (city name and
 * the most underpriced locality) so it reads as authored copy today and works
 * for any future city with no rewrite — the templated-headline scale seam.
 */
export interface HeroCopyProps {
  cityName: string;
  underpricedName: string;
}

export function HeroCopy({ cityName, underpricedName }: HeroCopyProps) {
  return (
    <div style={{ maxWidth: 760 }}>
      <h1
        style={{
          margin: 0,
          fontFamily: 'var(--rl-font-serif)',
          fontWeight: 'var(--rl-font-weight-regular)',
          fontSize: 'clamp(36px, 6vw, 88px)',
          lineHeight: 1.04,
          letterSpacing: '-0.02em',
          color: 'var(--rl-color-text-hi)',
        }}
      >
        The expensive-looking half of {cityName} is overpriced.
      </h1>
      <p
        style={{
          margin: '20px 0 0',
          fontFamily: 'var(--rl-font-ui)',
          fontSize: 'var(--rl-font-size-18)',
          lineHeight: 1.5,
          color: 'var(--rl-color-text-lo)',
          maxWidth: 560,
        }}
      >
        {underpricedName} is worth more than it rents for — and the metro is
        coming there first.
      </p>
    </div>
  );
}
