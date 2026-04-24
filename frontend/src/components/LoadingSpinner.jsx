export default function LoadingSpinner() {
  return (
    <div className="spinner-wrapper">
      <div className="spinner" />
      <p className="spinner-label">Fetching news and generating briefing…</p>
    </div>
  );
}
