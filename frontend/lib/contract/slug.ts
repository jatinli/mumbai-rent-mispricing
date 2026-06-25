/**
 * Locality slugs — the one place name<->slug casing is resolved, so route
 * params, deep links, and OG image params all agree.
 *   "Andheri East" -> "andheri-east"
 *   "Mulund"       -> "mulund"
 *   "Powai"        -> "powai"
 */

export function toSlug(name: string): string {
  return name
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');
}

/** Find an item by its locality slug, given an accessor for the name. */
export function findBySlug<T>(
  items: readonly T[],
  slug: string,
  getName: (item: T) => string,
): T | undefined {
  return items.find((item) => toSlug(getName(item)) === slug);
}
