export default function NotFound() {
  return (
    <div style={{ display: "grid", placeItems: "center", minHeight: "60vh", padding: 24 }}>
      <h2>Page Not Found</h2>
      <p style={{ color: "var(--muted)", marginTop: 8 }}>The requested page could not be found.</p>
    </div>
  );
}

