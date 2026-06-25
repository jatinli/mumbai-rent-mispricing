/**
 * RentLens frontend — Next.js configuration.
 *
 * Static export (`output: 'export'`) per the build spec: the site ships as
 * static assets to docs/ via GitHub Pages, with no server. Images are left
 * unoptimized because the static export has no image optimization server, and
 * the product uses SVG/canvas for its visuals rather than raster images.
 */

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
