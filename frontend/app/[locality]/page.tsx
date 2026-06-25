import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

import { DossierPanel } from '@/features/dossier/DossierPanel';
import { getContract } from '@/lib/contract/data-source';

interface PageProps {
  params: Promise<{ locality: string }>;
}

export async function generateStaticParams() {
  const { localities } = await getContract();
  return localities.map((l) => ({ locality: l.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locality: slug } = await params;
  const { localities, meta } = await getContract();
  const loc = localities.find((l) => l.slug === slug);
  if (!loc) return {};
  return {
    title: `${loc.name} — RentLens`,
    description: `${loc.name} in ${meta.displayName}: ${loc.residualPct > 0 ? 'above' : 'below'} fair value by ${Math.abs(loc.residualPct).toFixed(1)}%.`,
  };
}

export default async function LocalityPage({ params }: PageProps) {
  const { locality: slug } = await params;
  const { localities, transit, meta } = await getContract();
  const loc = localities.find((l) => l.slug === slug);
  if (!loc) notFound();

  const ucStationCount = transit.filter(
    (t) => t.status === 'under_construction',
  ).length;

  return <DossierPanel locality={loc} meta={meta} ucStationCount={ucStationCount} />;
}
