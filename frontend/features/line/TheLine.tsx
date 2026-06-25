'use client';

/**
 * TheLine — the product's motif: the pale-luminous fair-value datum.
 *
 * A full-width horizontal rule that draws once, left to right, via SVG
 * pathLength. Reused across the Horizon, the Map, and every Dossier as the
 * single reference everything is measured against. Decorative by default
 * (aria-hidden); pass `aria-hidden={false}` with a label where it conveys
 * meaning on its own.
 */
import { motion, useReducedMotion } from 'framer-motion';

export interface TheLineProps {
  /** Stroke width in px. */
  thickness?: number;
  /** Draw duration in ms (ignored when reduced motion or `drawn`). */
  durationMs?: number;
  /** Render already drawn (skip the entry animation). */
  drawn?: boolean;
  className?: string;
  ariaHidden?: boolean;
}

export function TheLine({
  thickness = 1.5,
  durationMs = 900,
  drawn = false,
  className,
  ariaHidden = true,
}: TheLineProps) {
  const prefersReduced = useReducedMotion();
  const animate = !drawn && !prefersReduced;

  return (
    <svg
      className={className}
      width="100%"
      height={Math.max(thickness, 2)}
      viewBox="0 0 100 1"
      preserveAspectRatio="none"
      aria-hidden={ariaHidden}
      style={{ display: 'block', overflow: 'visible' }}
    >
      <motion.line
        x1={0}
        y1={0.5}
        x2={100}
        y2={0.5}
        stroke="var(--rl-color-line)"
        strokeWidth={thickness}
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
        initial={{ pathLength: animate ? 0 : 1 }}
        animate={{ pathLength: 1 }}
        transition={
          animate
            ? { duration: durationMs / 1000, ease: [0.22, 1, 0.36, 1] }
            : { duration: 0 }
        }
      />
    </svg>
  );
}
