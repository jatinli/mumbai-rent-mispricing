import type { Metadata, Viewport } from 'next';
import { Fraunces } from 'next/font/google';
import { GeistSans } from 'geist/font/sans';
import { GeistMono } from 'geist/font/mono';
import '@/styles/globals.css';

/**
 * Three type voices, self-hosted and subset by Next's font pipeline:
 *   - Fraunces (display serif) → --rl-font-fraunces
 *   - Geist Sans (UI)          → --font-geist-sans
 *   - Geist Mono (numbers)     → --font-geist-mono
 * The token font stacks (lib/tokens) reference these variables.
 */
const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--rl-font-fraunces',
  display: 'swap',
  weight: ['400', '500'],
});

export const metadata: Metadata = {
  title: 'RentLens — Mumbai rental fair value',
  description:
    'A fair-value lens on Mumbai rent. See which localities trade above or below what their fundamentals justify.',
};

export const viewport: Viewport = {
  themeColor: '#0a0b0f',
  colorScheme: 'dark',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${GeistSans.variable} ${GeistMono.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
