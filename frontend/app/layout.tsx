import type { Metadata, Viewport } from 'next';
import '@/styles/globals.css';

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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
