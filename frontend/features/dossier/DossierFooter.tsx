import Link from 'next/link';

/**
 * Dossier footer — the cross-link back to the map and the aggregates-only
 * disclaimer rendered as a badge of integrity, not fine print. (The share /
 * copy-link affordance is added with the share task.)
 */
export interface DossierFooterProps {
  slug: string;
  disclaimer: string;
}

export function DossierFooter({ slug, disclaimer }: DossierFooterProps) {
  return (
    <footer
      style={{
        borderTop: '1px solid var(--rl-color-hairline)',
        paddingTop: 18,
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
      }}
    >
      <Link
        href={{ pathname: '/map', query: { focus: slug } }}
        style={{
          fontSize: 'var(--rl-font-size-13)',
          color: 'var(--rl-color-brand)',
        }}
      >
        See on the map →
      </Link>
      <p
        style={{
          margin: 0,
          fontSize: 'var(--rl-font-size-12)',
          lineHeight: 1.6,
          color: 'var(--rl-color-text-lo)',
          opacity: 0.8,
        }}
      >
        {disclaimer}
      </p>
    </footer>
  );
}
