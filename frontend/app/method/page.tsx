import type { Metadata } from 'next';
import Link from 'next/link';

import { TheLine } from '@/features/line/TheLine';
import { getContract } from '@/lib/contract/data-source';

export const metadata: Metadata = {
  title: 'How we know — RentLens',
  description:
    'The method behind RentLens: fair value from fundamentals, the mispricing residual, and an honest account of the limits.',
};

export default async function MethodPage() {
  const { meta } = await getContract();

  return (
    <main
      style={{
        maxWidth: 720,
        margin: '0 auto',
        padding: '64px 24px 96px',
        display: 'flex',
        flexDirection: 'column',
        gap: 28,
      }}
    >
      <header>
        <h1
          style={{
            margin: '0 0 16px',
            fontFamily: 'var(--rl-font-serif)',
            fontWeight: 'var(--rl-font-weight-regular)',
            fontSize: 'var(--rl-font-size-40)',
            lineHeight: 1.1,
          }}
        >
          How we know
        </h1>
        <TheLine thickness={1.5} />
      </header>

      <Section title="Fair value">
        Every flat is priced from its fundamentals alone — carpet area, bedrooms,
        bathrooms, furnishing, floor, and distance to transit — by a cross-market
        model that never sees which locality a flat is in. That modeled price is
        the fair-value line. What a flat actually asks, minus that line, is the
        mispricing.
      </Section>

      <Section title="The residual">
        A locality&apos;s headline number is the median of{' '}
        <code style={{ fontFamily: 'var(--rl-font-mono)' }}>
          (asking − fair) / fair
        </code>{' '}
        across its listings. Positive means the market pays above fundamentals;
        negative means it pays below.
      </Section>

      <Section title="What we can and cannot claim">
        The locality-level mispricing is statistically strong. The relationship
        between rent and distance to an under-construction station is{' '}
        <em>not</em> yet significant — so the metro thesis is an opening the
        market has not priced, not a proven cause. Read the carry as opportunity,
        not as a guarantee.
      </Section>

      <Section title="Provenance">
        {meta.nListings} listings from {meta.sources.join(', ')}
        {meta.scrapeDate ? `, ${meta.scrapeDate}` : ''}; transit from
        OpenStreetMap. {meta.disclaimer}
      </Section>

      <Link
        href="/"
        style={{ fontSize: 'var(--rl-font-size-13)', color: 'var(--rl-color-brand)' }}
      >
        ← Back
      </Link>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2
        style={{
          margin: '0 0 8px',
          fontFamily: 'var(--rl-font-ui)',
          fontWeight: 'var(--rl-font-weight-medium)',
          fontSize: 'var(--rl-font-size-18)',
          color: 'var(--rl-color-text-hi)',
        }}
      >
        {title}
      </h2>
      <p
        style={{
          margin: 0,
          fontSize: 'var(--rl-font-size-15)',
          lineHeight: 1.7,
          color: 'var(--rl-color-text-lo)',
        }}
      >
        {children}
      </p>
    </section>
  );
}
