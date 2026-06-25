'use client';

/**
 * NumberFlowValue — the odometer used for every figure in the product.
 *
 * Wraps @number-flow/react with the mono/tabular type and the four display
 * kinds the contract needs (rent, signed %, unsigned %, count). NumberFlow
 * respects prefers-reduced-motion by default, so the reduced-motion path is
 * handled by the library.
 */
import NumberFlow from '@number-flow/react';
import type { ComponentProps, CSSProperties } from 'react';

export type NumberKind = 'rent' | 'signedPct' | 'pct' | 'int';

type NumberFlowFormat = NonNullable<ComponentProps<typeof NumberFlow>['format']>;

interface KindConfig {
  locales?: string;
  format: NumberFlowFormat;
  suffix?: string;
}

const KINDS: Record<NumberKind, KindConfig> = {
  rent: {
    locales: 'en-IN',
    format: { style: 'currency', currency: 'INR', maximumFractionDigits: 0 },
  },
  signedPct: {
    format: {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
      signDisplay: 'exceptZero',
    },
    suffix: '%',
  },
  pct: {
    format: { minimumFractionDigits: 1, maximumFractionDigits: 1 },
    suffix: '%',
  },
  int: {
    format: { maximumFractionDigits: 0 },
  },
};

export interface NumberFlowValueProps {
  value: number;
  kind?: NumberKind;
  className?: string;
  style?: CSSProperties;
  'aria-label'?: string;
}

export function NumberFlowValue({
  value,
  kind = 'int',
  className,
  style,
  'aria-label': ariaLabel,
}: NumberFlowValueProps) {
  const cfg = KINDS[kind];
  return (
    <NumberFlow
      value={value}
      locales={cfg.locales}
      format={cfg.format}
      suffix={cfg.suffix}
      className={className}
      aria-label={ariaLabel}
      style={{
        fontFamily: 'var(--rl-font-mono)',
        fontVariantNumeric: 'tabular-nums',
        ...style,
      }}
    />
  );
}
