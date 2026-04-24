import { useState } from "react";
import "./App.css";
import BriefingCard from "./components/BriefingCard";
import ErrorMessage from "./components/ErrorMessage";
import FilterPanel from "./components/FilterPanel";
import LoadingSpinner from "./components/LoadingSpinner";
import SearchBar from "./components/SearchBar";
import { generateBriefing } from "./services/api";

const DEFAULT_FILTERS = { fromDate: "", toDate: "", sortBy: "relevancy", domains: [] };

function getDateError(filters) {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 30);
  const cutoffStr = cutoff.toISOString().split("T")[0];
  if (filters.fromDate && filters.fromDate < cutoffStr) {
    return `The News API Free plan only covers the last 30 days. "From" must be on or after ${cutoffStr}.`;
  }
  if (filters.toDate && filters.toDate < cutoffStr) {
    return `Free plan only covers the last 30 days. "To" must be on or after ${cutoffStr}.`;
  }
  return null;
}

export default function App() {
  const [company, setCompany] = useState("");
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [briefing, setBriefing] = useState(null);
  const [queriedCompany, setQueriedCompany] = useState("");
  const [timestamp, setTimestamp] = useState("");

  const dateError = getDateError(filters);

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    setBriefing(null);

    try {
      const data = await generateBriefing(company.trim(), filters);
      setQueriedCompany(company.trim());
      setTimestamp(new Date().toLocaleString());
      setBriefing(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <span className="header-logo">▮</span>
          <span className="header-title">Bain Briefing Tool</span>
        </div>
      </header>

      <main className="app-main">
        <h1 className="page-title">Company News Briefing</h1>
        <p className="page-subtitle">
          Enter a company name to generate a pre-meeting briefing from recent news.
        </p>

        <SearchBar
          value={company}
          onChange={setCompany}
          onSubmit={handleSubmit}
          loading={loading}
          disabled={loading || !!dateError}
        />

        <FilterPanel filters={filters} onChange={setFilters} disabled={loading} dateError={dateError} />

        {error && <ErrorMessage message={error} />}
        {loading && <LoadingSpinner />}
        {briefing && (
          <BriefingCard
            briefing={briefing}
            company={queriedCompany}
            timestamp={timestamp}
          />
        )}
      </main>
    </div>
  );
}
