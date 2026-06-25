import { CarryPanel } from '@/features/dossier/CarryPanel';
import { CompositionStrip } from '@/features/dossier/CompositionStrip';
import { ConfidenceNote } from '@/features/dossier/ConfidenceNote';
import { DossierFooter } from '@/features/dossier/DossierFooter';
import { DossierHeader } from '@/features/dossier/DossierHeader';
import { SpreadBar } from '@/features/dossier/SpreadBar';
import { VerdictHeadline } from '@/features/verdict/VerdictHeadline';
import type { LocalityVM, MetaVM } from '@/lib/contract/normalize';

/**
 * The Dossier — one locality as an object worth studying. A single authored
 * column: verdict -> magnitude -> composition -> opportunity -> honesty.
 */
export interface DossierPanelProps {
  locality: LocalityVM;
  meta: MetaVM;
  ucStationCount: number;
}

export function DossierPanel({ locality, meta, ucStationCount }: DossierPanelProps) {
  return (
    <main
      style={{
        maxWidth: 720,
        margin: '0 auto',
        padding: '64px 24px 96px',
        display: 'flex',
        flexDirection: 'column',
        gap: 40,
      }}
    >
      <DossierHeader locality={locality} cityName={meta.displayName} />
      <VerdictHeadline locality={locality} />
      <SpreadBar
        askingRent={locality.medianRent}
        fairRent={locality.fairRent}
        residualPct={locality.residualPct}
      />
      <CompositionStrip pctOverpriced={locality.pctOverpriced} />
      <CarryPanel arbitrage={locality.arbitrage} ucStationCount={ucStationCount} />
      <ConfidenceNote n={locality.n} />
      <DossierFooter slug={locality.slug} disclaimer={meta.disclaimer} />
    </main>
  );
}
