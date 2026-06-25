/**
 * RentLens design tokens — the single source of truth.
 *
 * These values are the frozen v1 design system. Two consumers read them:
 *   1. CSS, via `toCssVariables()` → `styles/tokens.css` (the token build step).
 *   2. JS/canvas/SVG/deck.gl, which import the `tokens` object directly because
 *      they cannot read CSS custom properties at runtime.
 *
 * Keep this file the only place the raw values live. Do not hardcode hex/sizes
 * elsewhere — import from here (or use the generated CSS variables).
 */

export const tokens = {
  /** Instrument shell — the dark canvas everything sits on. */
  color: {
    ink: '#0A0B0F',
    surface: '#13151C',
    surface2: '#1C1F29',
    hairline: '#2A2E3A',
    textHi: '#ECEEF3',
    textLo: '#8A91A0',
    /** The fair-value datum. Neutral by design — deviations carry the color. */
    line: '#E8EAF2',
    /** Interactive / brand accent. */
    brand: '#7C6BFF',
  },

  /**
   * The signal axis: deviation from fair value, as a 7-stop diverging ramp.
   * Underpriced intensifies toward the iconic jade (#2BD9A8); overpriced
   * intensifies toward deep ember (#F2542D). Consumed by `signalColor()`.
   */
  signal: {
    under3: '#2BD9A8', // < -20%  (deepest underpricing — the hero jade)
    under2: '#25C497', // -20..-10%
    under1: '#1FA887', // -10..-5%
    fair: '#6B7280', //   -5..+5%
    over1: '#FF9A7B', //   +5..+10%
    over2: '#FF7A59', //  +10..+20%
    over3: '#F2542D', //  > +20%   (deepest overpricing)
  },

  /** Transit identities. Under-construction lines are the "future" violets. */
  transit: {
    operational: '#4F8BFF',
    rail: '#5A6275',
    uc4: '#8B7BFF', // Metro Line 4 (under construction)
    uc6: '#C77DFF', // Metro Line 6 (under construction)
  },

  /**
   * Three voices: serif (narrative), grotesk (UI), mono (every number).
   * Families resolve to font-loader CSS variables set on <html> in the root
   * layout: Fraunces via next/font/google, Geist Sans/Mono via the geist pkg.
   */
  font: {
    serif: "var(--rl-font-fraunces), Georgia, 'Times New Roman', serif",
    ui: 'var(--font-geist-sans), system-ui, -apple-system, sans-serif',
    mono: "var(--font-geist-mono), ui-monospace, 'SFMono-Regular', monospace",
  },

  /** Type scale (px). Hero headline clamps separately in component styles. */
  fontSize: {
    '12': '12px',
    '13': '13px',
    '15': '15px',
    '18': '18px',
    '22': '22px',
    '28': '28px',
    '40': '40px',
    '64': '64px',
    '96': '96px',
  },

  /** Two weights only. */
  fontWeight: {
    regular: '400',
    medium: '500',
  },

  /** 4px base spacing scale, keyed by px value. */
  space: {
    '4': '4px',
    '8': '8px',
    '12': '12px',
    '16': '16px',
    '24': '24px',
    '32': '32px',
    '48': '48px',
    '64': '64px',
  },

  radius: {
    md: '8px',
    lg: '12px',
    xl: '16px',
  },

  /** Motion durations + the one reveal easing. Springs live in lib/motion. */
  motion: {
    durFast: '240ms',
    durBase: '420ms',
    durSlow: '1200ms',
    easeReveal: 'cubic-bezier(0.22, 1, 0.36, 1)',
  },

  /** Layer order: map < panel < line < nav. */
  z: {
    map: '0',
    panel: '30',
    line: '40',
    nav: '50',
  },
} as const;

export type Tokens = typeof tokens;

const CSS_PREFIX = '--rl';

/**
 * Project the token object into a flat `{ '--rl-...': value }` map for CSS.
 * Names follow `--rl-<section>-<key>` in kebab case, e.g. `--rl-color-text-hi`.
 */
export function toCssVariables(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [section, group] of Object.entries(tokens)) {
    for (const [key, value] of Object.entries(group as Record<string, string>)) {
      out[`${CSS_PREFIX}-${kebab(section)}-${kebab(key)}`] = value;
    }
  }
  return out;
}

function kebab(s: string): string {
  return s.replace(/([a-z])([A-Z0-9])/g, '$1-$2').toLowerCase();
}
