export default function SearchBar({ value, onChange, onSubmit, loading, disabled }) {
  function handleSubmit(e) {
    e.preventDefault();
    if (value.trim() && !disabled) onSubmit();
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        className="search-input"
        placeholder="Enter company name (e.g. Apple, Volkswagen)"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={loading}
      />
      <button className="search-btn" type="submit" disabled={disabled || !value.trim()}>
        {loading ? "Generating…" : "Generate Briefing"}
      </button>
    </form>
  );
}
