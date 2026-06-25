import { signalLabel, type SignalTone } from '@/lib/signal/scale';

/**
 * VerdictBadge — the Underpriced / Overpriced / Fair pill, colored on the
 * signal axis. Token-driven via color-mix so the translucent fill and border
 * track the signal ramp without hardcoded hex.
 */
const TONE_VAR: Record<SignalTone, string> = {
  underpriced: 'var(--rl-signal-under-3)',
  overpriced: 'var(--rl-signal-over-3)',
  fair: 'var(--rl-signal-fair)',
};

export function VerdictBadge({ tone }: { tone: SignalTone }) {
  const color = TONE_VAR[tone];
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '4px 12px',
        borderRadius: 999,
        fontFamily: 'var(--rl-font-ui)',
        fontSize: 'var(--rl-font-size-12)',
        fontWeight: 'var(--rl-font-weight-medium)',
        letterSpacing: '0.04em',
        color,
        background: `color-mix(in srgb, ${color} 12%, transparent)`,
        border: `1px solid color-mix(in srgb, ${color} 45%, transparent)`,
      }}
    >
      {signalLabel(tone)}
    </span>
  );
}
