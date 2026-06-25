/**
 * DataSource — the seam between the UI and where the contract comes from.
 *
 * v1 ships StaticDataSource (reads the committed JSON at build time). The
 * interface is the dormant seam for the future: a live API becomes an
 * HttpDataSource implementing the same `getContract()`, with no component
 * changes. Components depend on `getContract()`, never on the loader directly.
 */
import { loadContract, type ContractData } from './normalize';

export interface DataSource {
  getContract(): Promise<ContractData>;
}

/** Reads the committed aggregates-only JSON from disk. Build/server-only. */
export class StaticDataSource implements DataSource {
  async getContract(): Promise<ContractData> {
    return loadContract();
  }
}

export const dataSource: DataSource = new StaticDataSource();

export function getContract(): Promise<ContractData> {
  return dataSource.getContract();
}

export type { ContractData } from './normalize';
