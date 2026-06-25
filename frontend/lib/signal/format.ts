/**
 * Number formatting for the data display. Every figure on screen passes
 * through here so currency, percent, and sign rendering stay consistent.
 *
 * The minus sign is the typographic U+2212 (−), not the hyphen-minus, to match
 * the design and align in tabular mono columns.
 */

const MINUS = '−';

const inr = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

/** 50000 -> "₹50,000" (Indian digit grouping, no decimals). */
export function formatRent(value: number): string {
  return inr.format(value);
}

/** 14.88 -> "+14.9%", -23.5 -> "−23.5%", 0 -> "0.0%". */
export function formatSignedPct(value: number, digits = 1): string {
  const rounded = Number(value.toFixed(digits));
  const sign = rounded > 0 ? '+' : rounded < 0 ? MINUS : '';
  return `${sign}${Math.abs(rounded).toFixed(digits)}%`;
}

/** 73.9 -> "73.9%" (unsigned). */
export function formatPct(value: number, digits = 1): string {
  return `${value.toFixed(digits)}%`;
}
