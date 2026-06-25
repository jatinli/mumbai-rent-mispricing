import { ImageResponse } from 'next/og';

import { getContract } from '@/lib/contract/data-source';
import { signalColor } from '@/lib/signal/scale';
import { formatSignedPct } from '@/lib/signal/format';
import { tokens } from '@/lib/tokens/tokens';
import { verdictRuling } from '@/features/verdict/VerdictHeadline';

export const dynamic = 'force-static';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export async function generateStaticParams() {
  const { localities } = await getContract();
  return localities.map((l) => ({ locality: l.slug }));
}

/**
 * The Verdict card — the share artifact. One locality, one giant signed number,
 * one ruling, the Line. Satori does not resolve CSS variables, so colors come
 * from raw token hex.
 */
export default async function Image({
  params,
}: {
  params: Promise<{ locality: string }>;
}) {
  const { locality: slug } = await params;
  const { localities, meta } = await getContract();
  const loc = localities.find((l) => l.slug === slug);
  const color = loc ? signalColor(loc.residualPct) : tokens.color.textLo;

  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          background: tokens.color.ink,
          color: tokens.color.textHi,
          padding: 72,
        }}
      >
        <div style={{ display: 'flex', fontSize: 28, letterSpacing: 4, color: tokens.color.textLo }}>
          RENTLENS
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', fontSize: 44, color: tokens.color.textHi }}>
            {loc ? loc.name : 'Mumbai'}
          </div>
          <div style={{ display: 'flex', fontSize: 200, lineHeight: 1.05, color }}>
            {loc ? formatSignedPct(loc.residualPct) : '—'}
          </div>
          <div style={{ display: 'flex', height: 2, background: tokens.color.line, margin: '12px 0 20px' }} />
          <div style={{ display: 'flex', fontSize: 40, color: tokens.color.textHi }}>
            {loc ? verdictRuling(loc) : 'Mumbai rental fair value'}
          </div>
        </div>

        <div style={{ display: 'flex', fontSize: 24, color: tokens.color.textLo }}>
          {meta.sources.join(', ')} · n={meta.nListings} · {meta.scrapeDate ?? ''}
        </div>
      </div>
    ),
    size,
  );
}
