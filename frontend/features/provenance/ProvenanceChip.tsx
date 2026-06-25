/**
 * ProvenanceChip — the Bloomberg-style credibility mark: source, sample size,
 * and scrape date, rendered as an identity badge rather than fine print. The
 * date is freshness-aware in spirit (the dormant live-API seam); today it shows
 * the static scrape date.
 */
const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
];

function formatScrapeDate(iso: string | null): string | null {
  if (!iso) return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
  if (!m) return iso;
  const [, year, month, day] = m;
  const monthName = MONTHS[Number(month) - 1] ?? month;
  return `${Number(day)} ${monthName} ${year}`;
}

export interface ProvenanceChipProps {
  sources: string[];
  nListings: number;
  scrapeDate: string | null;
}

export function ProvenanceChip({ sources, nListings, scrapeDate }: ProvenanceChipProps) {
  const parts = [
    sources.join(' · '),
    `n=${nListings}`,
    formatScrapeDate(scrapeDate),
  ].filter(Boolean);

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '5px 12px',
        borderRadius: 999,
        border: '1px solid var(--rl-color-hairline)',
        background: 'var(--rl-color-surface)',
        fontFamily: 'var(--rl-font-mono)',
        fontSize: 'var(--rl-font-size-12)',
        letterSpacing: '0.02em',
        color: 'var(--rl-color-text-lo)',
        whiteSpace: 'nowrap',
      }}
    >
      {parts.join('  ·  ')}
    </span>
  );
}
