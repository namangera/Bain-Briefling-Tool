import { useEffect, useRef, useState } from "react";
import { APPROVED_SOURCES } from "../constants/sources";

const SORT_OPTIONS = [
  { value: "relevancy", label: "Most relevant" },
  { value: "publishedAt", label: "Most recent" },
  { value: "popularity", label: "Most popular" },
];

function SourceDropdown({ selected, onChange, disabled }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef(null);
  const searchRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
        setSearch("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (open) searchRef.current?.focus();
  }, [open]);

  function toggle(domain) {
    if (selected.includes(domain)) {
      onChange(selected.filter((d) => d !== domain));
    } else {
      onChange([...selected, domain]);
    }
  }

  const filtered = APPROVED_SOURCES.filter(
    ({ domain, label }) =>
      label.toLowerCase().includes(search.toLowerCase()) ||
      domain.toLowerCase().includes(search.toLowerCase())
  );

  const buttonLabel =
    selected.length === 0
      ? "All sources"
      : selected.length === 1
      ? APPROVED_SOURCES.find((s) => s.domain === selected[0])?.label
      : `${selected.length} sources selected`;

  return (
    <div className="source-dropdown" ref={ref}>
      <button
        type="button"
        className={`source-dropdown-toggle ${selected.length > 0 ? "source-dropdown-toggle--active" : ""}`}
        onClick={() => setOpen((o) => !o)}
        disabled={disabled}
      >
        <span>{buttonLabel}</span>
        <span className="source-dropdown-caret">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="source-dropdown-menu">
          <div className="source-search-wrapper">
            <input
              ref={searchRef}
              type="text"
              className="source-search"
              placeholder="Search sources…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="source-options-list">
            {filtered.length > 0 ? (
              filtered.map(({ domain, label }) => (
                <label key={domain} className="source-option">
                  <input
                    type="checkbox"
                    checked={selected.includes(domain)}
                    onChange={() => toggle(domain)}
                  />
                  <span className="source-option-label">{label}</span>
                  <span className="source-option-domain">{domain}</span>
                </label>
              ))
            ) : (
              <p className="source-no-results">No sources match "{search}"</p>
            )}
          </div>
        </div>
      )}

      {selected.length > 0 && (
        <div className="source-pills">
          {selected.map((domain) => {
            const src = APPROVED_SOURCES.find((s) => s.domain === domain);
            return (
              <span key={domain} className="source-pill">
                {src?.label}
                <button
                  type="button"
                  className="source-pill-remove"
                  onClick={() => toggle(domain)}
                  disabled={disabled}
                  aria-label={`Remove ${src?.label}`}
                >
                  ×
                </button>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function FilterPanel({ filters, onChange, disabled, dateError }) {
  const [open, setOpen] = useState(false);

  const hasActiveFilters =
    filters.fromDate ||
    filters.toDate ||
    filters.domains.length > 0 ||
    filters.sortBy !== "relevancy";

  function handleChange(field, value) {
    onChange({ ...filters, [field]: value });
  }

  function handleClear() {
    onChange({ fromDate: "", toDate: "", sortBy: "relevancy", domains: [] });
  }

  return (
    <div className="filter-panel">
      <button
        type="button"
        className={`filter-toggle ${hasActiveFilters ? "filter-toggle--active" : ""}`}
        onClick={() => setOpen((o) => !o)}
        disabled={disabled}
      >
        <span>{open ? "▲" : "▼"} Filters</span>
        {hasActiveFilters && <span className="filter-badge">●</span>}
      </button>

      {open && (
        <div className="filter-body">
          <div className="filter-row">
            <label className="filter-label">
              From
              <input
                type="date"
                className="filter-input"
                value={filters.fromDate}
                onChange={(e) => handleChange("fromDate", e.target.value)}
                disabled={disabled}
              />
            </label>

            <label className="filter-label">
              To
              <input
                type="date"
                className="filter-input"
                value={filters.toDate}
                onChange={(e) => handleChange("toDate", e.target.value)}
                disabled={disabled}
              />
            </label>

            <label className="filter-label">
              Sort by
              <select
                className="filter-input"
                value={filters.sortBy}
                onChange={(e) => handleChange("sortBy", e.target.value)}
                disabled={disabled}
              >
                {SORT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {dateError && <p className="filter-date-error">{dateError}</p>}

          <div className="filter-label filter-label--full">
            Restrict to sources
            <SourceDropdown
              selected={filters.domains}
              onChange={(val) => handleChange("domains", val)}
              disabled={disabled}
            />
          </div>

          {hasActiveFilters && (
            <button
              type="button"
              className="filter-clear"
              onClick={handleClear}
              disabled={disabled}
            >
              Clear filters
            </button>
          )}
        </div>
      )}
    </div>
  );
}
