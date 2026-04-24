import { useState } from "react";

function Section({ title, children }) {
  return (
    <div className="section">
      <h2 className="section-title">{title}</h2>
      {children}
    </div>
  );
}

function BulletList({ items }) {
  return (
    <ul className="bullet-list">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}

function ArticlesList({ articles }) {
  return (
    <ul className="articles-list">
      {articles.map((a, i) => (
        <li key={i} className="article-item">
          <div className="article-header">
            <a href={a.url} target="_blank" rel="noopener noreferrer" className="article-link">
              {a.title}
            </a>
            <span className="source-date">
              {new Date(a.publishedAt).toLocaleDateString("en-GB", {
                day: "numeric",
                month: "short",
                year: "numeric",
              })}
            </span>
          </div>
          {a.description && (
            <p className="article-description">{a.description}</p>
          )}
        </li>
      ))}
    </ul>
  );
}

export default function BriefingCard({ briefing, company, timestamp }) {
  const [articlesOpen, setArticlesOpen] = useState(false);
  const articles = briefing.articles ?? [];

  return (
    <div className="briefing-card">
      <div className="briefing-header">
        <h1 className="briefing-company">{company}</h1>
        <span className="briefing-timestamp">{timestamp}</span>
      </div>

      <Section title="Summary">
        <p className="summary-text">{briefing.summary}</p>
      </Section>

      <Section title="Key Themes">
        <BulletList items={briefing.key_themes} />
      </Section>

      <Section title="Risks">
        <BulletList items={briefing.risks} />
      </Section>

      <Section title="Opportunities">
        <BulletList items={briefing.opportunities} />
      </Section>

      <Section title="Talking Points">
        <BulletList items={briefing.talking_points} />
      </Section>

      {articles.length > 0 && (
        <div className="section articles-section">
          <button
            className="articles-toggle"
            onClick={() => setArticlesOpen((o) => !o)}
            aria-expanded={articlesOpen}
          >
            <span className="section-title" style={{ margin: 0 }}>
              Source Articles ({articles.length})
            </span>
            <span className="articles-toggle-icon">{articlesOpen ? "▲" : "▼"}</span>
          </button>
          {articlesOpen && <ArticlesList articles={articles} />}
        </div>
      )}
    </div>
  );
}
