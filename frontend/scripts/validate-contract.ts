/**
 * Build-time contract validation (runs on `prebuild`).
 *
 * Parses every contract file through its Zod schema and runs light
 * cross-checks. Any drift fails the build with a non-zero exit, enforcing the
 * "contract is stable" guarantee before a single page is generated.
 */
import { loadRawContract } from '../lib/contract/load';

try {
  const c = loadRawContract();

  const localityNames = new Set(c.localities.map((l) => l.locality));
  const orphanArbitrage = c.arbitrage.filter(
    (a) => !localityNames.has(a.locality),
  );
  if (orphanArbitrage.length > 0) {
    throw new Error(
      `arbitrage_summary references unknown localities: ${orphanArbitrage
        .map((a) => a.locality)
        .join(', ')}`,
    );
  }

  console.log(
    `contract OK: ${c.localities.length} localities, ` +
      `${c.arbitrage.length} arbitrage rows, ${c.transit.length} stations, ` +
      `n_listings=${c.meta.n_listings}`,
  );
} catch (err) {
  console.error('contract validation FAILED:');
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
}
