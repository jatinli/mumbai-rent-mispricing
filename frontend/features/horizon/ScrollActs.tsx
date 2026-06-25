'use client';

/**
 * The landing's scroll Acts after the Horizon: the Verdict, the Overlap, and
 * the Honest Edge + CTA. Reveals are scroll-linked via framer-motion whileInView
 * (reduced-motion aware through MotionConfig). Lenis smoothing is deferred to
 * M4 polish; native scroll drives these today.
 */
import { motion } from 'framer-motion';
import Link from 'next/link';

import { NumberFlowValue } from '@/features/number/NumberFlowValue';
import { signalColor } from '@/lib/signal/scale';

export interface ScrollActsProps {
  underpriced: {
    name: string;
    residualPct: number;
    medianRent: number;
    fairRent: number;
    pctOverpriced: number;
    nCandidates: number | null;
  };
}

const reveal = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-12%' },
  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as const },
};

const actStyle: React.CSSProperties = {
  minHeight: '78vh',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  maxWidth: 760,
  margin: '0 auto',
  padding: '0 24px',
};

export function ScrollActs({ underpriced }: ScrollActsProps) {
  const color = signalColor(underpriced.residualPct);
  const pctBelow = Math.round(100 - underpriced.pctOverpriced);

  return (
    <>
      <motion.section {...reveal} style={actStyle} aria-label="The verdict">
        <div style={{ fontSize: 'var(--rl-font-size-18)', color: 'var(--rl-color-text-lo)' }}>
          {underpriced.name}
        </div>
        <div
          style={{
            fontFamily: 'var(--rl-font-mono)',
            fontSize: 'clamp(72px, 14vw, 168px)',
            lineHeight: 1,
            fontWeight: 'var(--rl-font-weight-medium)',
            color,
          }}
        >
          <NumberFlowValue value={underpriced.residualPct} kind="signedPct" />
        </div>
        <p
          style={{
            margin: '16px 0 24px',
            fontFamily: 'var(--rl-font-serif)',
            fontSize: 'var(--rl-font-size-28)',
            lineHeight: 1.2,
            color: 'var(--rl-color-text-hi)',
          }}
        >
          The market is underpricing {underpriced.name}.
        </p>
        <div
          style={{
            fontFamily: 'var(--rl-font-mono)',
            fontSize: 'var(--rl-font-size-15)',
            color: 'var(--rl-color-text-lo)',
            display: 'flex',
            flexWrap: 'wrap',
            gap: 14,
          }}
        >
          <span>
            Asks <NumberFlowValue value={underpriced.medianRent} kind="rent" />
          </span>
          <span aria-hidden>·</span>
          <span>
            Worth <NumberFlowValue value={underpriced.fairRent} kind="rent" />
          </span>
          <span aria-hidden>·</span>
          <span>{pctBelow}% of listings below the line</span>
        </div>
      </motion.section>

      <motion.section {...reveal} style={actStyle} aria-label="The overlap">
        <p
          style={{
            margin: 0,
            fontFamily: 'var(--rl-font-serif)',
            fontSize: 'clamp(24px, 4vw, 44px)',
            lineHeight: 1.25,
            color: 'var(--rl-color-text-hi)',
          }}
        >
          {underpriced.nCandidates ?? 0} of these undervalued flats sit within
          2.5&nbsp;km of a station that doesn&apos;t exist yet.
        </p>
      </motion.section>

      <motion.section {...reveal} style={actStyle} aria-label="The honest edge">
        <p
          style={{
            margin: '0 0 28px',
            fontFamily: 'var(--rl-font-serif)',
            fontSize: 'clamp(22px, 3.4vw, 36px)',
            lineHeight: 1.3,
            color: 'var(--rl-color-text-hi)',
          }}
        >
          We can prove {underpriced.name} is underpriced. We can&apos;t yet prove
          the metro will fix it. That&apos;s the opening.
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginBottom: 32 }}>
          <Chip label="Locality effect" value="strong" />
          <Chip label="Metro effect" value="not yet" />
        </div>
        <Link
          href="/map"
          style={{
            alignSelf: 'flex-start',
            fontFamily: 'var(--rl-font-ui)',
            fontSize: 'var(--rl-font-size-18)',
            color: 'var(--rl-color-brand)',
            borderBottom: '1px solid var(--rl-color-brand)',
            paddingBottom: 2,
          }}
        >
          Enter the map →
        </Link>
      </motion.section>
    </>
  );
}

function Chip({ label, value }: { label: string; value: string }) {
  return (
    <span
      style={{
        display: 'inline-flex',
        gap: 8,
        padding: '6px 12px',
        borderRadius: 999,
        border: '1px solid var(--rl-color-hairline)',
        fontFamily: 'var(--rl-font-mono)',
        fontSize: 'var(--rl-font-size-12)',
        color: 'var(--rl-color-text-lo)',
      }}
    >
      <span>{label}</span>
      <span style={{ color: 'var(--rl-color-text-hi)' }}>{value}</span>
    </span>
  );
}
