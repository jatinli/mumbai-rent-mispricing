import { HeroCopy } from '@/features/horizon/HeroCopy';
import { HorizonStage } from '@/features/horizon/HorizonStage';
import { ScrollActs } from '@/features/horizon/ScrollActs';
import { ProvenanceChip } from '@/features/provenance/ProvenanceChip';
import { getContract } from '@/lib/contract/data-source';
import { mostUnderpriced } from '@/lib/contract/normalize';

/**
 * The Horizon — the landing. Act 1 is the three skylines against the Line with
 * the Verdict's voice; the scroll Acts follow. Localities arrive residual-sorted
 * from the contract.
 */
export default async function HomePage() {
  const { localities, meta } = await getContract();
  const underpriced = mostUnderpriced(localities) ?? localities[localities.length - 1];

  return (
    <main>
      <section
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          padding: '28px 24px 24px',
        }}
      >
        <header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 16,
          }}
        >
          <span
            style={{
              fontFamily: 'var(--rl-font-mono)',
              fontSize: 'var(--rl-font-size-15)',
              letterSpacing: '0.18em',
              color: 'var(--rl-color-text-hi)',
            }}
          >
            RentLens
          </span>
          <ProvenanceChip
            sources={meta.sources}
            nListings={meta.nListings}
            scrapeDate={meta.scrapeDate}
          />
        </header>

        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            gap: 'clamp(32px, 6vh, 72px)',
            padding: '32px 0',
          }}
        >
          {underpriced && (
            <HeroCopy cityName={meta.displayName} underpricedName={underpriced.name} />
          )}
          <HorizonStage localities={localities} />
        </div>

        <div
          style={{
            textAlign: 'center',
            fontFamily: 'var(--rl-font-ui)',
            fontSize: 'var(--rl-font-size-13)',
            color: 'var(--rl-color-text-lo)',
          }}
        >
          Cross the line ↓
        </div>
      </section>

      {underpriced && (
        <ScrollActs
          underpriced={{
            name: underpriced.name,
            residualPct: underpriced.residualPct,
            medianRent: underpriced.medianRent,
            fairRent: underpriced.fairRent,
            pctOverpriced: underpriced.pctOverpriced,
            nCandidates: underpriced.arbitrage?.nCandidates ?? null,
          }}
        />
      )}
    </main>
  );
}
