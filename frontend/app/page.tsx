/**
 * Home route — placeholder shell.
 *
 * The Horizon landing (skylines + the Line + Verdict copy) is built in M2 and
 * replaces this placeholder. It exists now only so the static export has a
 * buildable root route during M0/M1.
 */
export default function HomePage() {
  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <p style={{ fontSize: 15, opacity: 0.6 }}>RentLens</p>
    </main>
  );
}
