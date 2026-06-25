import Link from 'next/link';

/**
 * The Confidence — honesty as a feature. States the sample size and the candid
 * limit: the locality signal is strong, the metro-distance effect is not yet
 * significant. Links to the method page.
 */
export function ConfidenceNote({ n }: { n: number }) {
  return (
    <section
      aria-label="Confidence"
      style={{
        borderTop: '1px solid var(--rl-color-hairline)',
        paddingTop: 18,
      }}
    >
      <p
        style={{
          margin: 0,
          fontSize: 'var(--rl-font-size-13)',
          lineHeight: 1.7,
          color: 'var(--rl-color-text-lo)',
        }}
      >
        Estimated from {n} priced listings in this locality. The locality-level
        mispricing is statistically strong; the effect of distance to an
        under-construction station is not yet significant — read it as
        opportunity, not proof.{' '}
        <Link href="/method" style={{ color: 'var(--rl-color-brand)' }}>
          How we know
        </Link>
        .
      </p>
    </section>
  );
}
