import React, { useState } from 'react';

export default function ResultCard({ standard, rank }) {
  const [expanded, setExpanded] = useState(false);

  const scorePct = Math.round(standard.similarity_score * 100);
  const relevanceLabel = standard.relevance_label || (scorePct >= 60 ? 'High' : scorePct >= 40 ? 'Medium' : 'Low');

  return (
    <div className="result-card" id={`standard-${standard.standard_number.replace(/[^a-zA-Z0-9]/g, '-')}`}>
      <div className="result-card-top">
        <div className="standard-badge-group">
          <span className="standard-num-badge">{standard.standard_number}</span>
          <span className={`status-badge ${standard.status === 'ACTIVE' ? 'status-active' : ''}`}>
            {standard.status || 'ACTIVE'}
          </span>
          {standard.category && (
            <span className="category-badge">{standard.category}</span>
          )}
          {standard.department && (
            <span className="category-badge" style={{ color: '#93c5fd' }}>{standard.department}</span>
          )}
        </div>

        <div className="score-badge-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className={`relevance-badge relevance-${relevanceLabel.toLowerCase()}`}>
            {relevanceLabel} Relevance
          </span>
          <div className="score-badge" title="Combined 75% semantic vector + 25% BIS metadata relevance score">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            <span>{scorePct}% Match</span>
          </div>
        </div>
      </div>

      <h2 className="result-title">{standard.title}</h2>

      {standard.explanation && (
        <div className="why-standard-box">
          <div className="why-standard-header">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <strong>Why this standard?</strong>
          </div>
          <p className="why-standard-text">{standard.explanation}</p>
        </div>
      )}

      <div className="result-scope">
        <strong style={{ color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.35rem' }}>
          Official Scope & Applicability:
        </strong>
        <p>
          {expanded ? standard.scope : (standard.scope_snippet || standard.scope)}
        </p>
        {standard.scope && standard.scope.length > 280 && (
          <button
            type="button"
            style={{
              background: 'none',
              border: 'none',
              color: '#60a5fa',
              cursor: 'pointer',
              fontSize: '0.82rem',
              marginTop: '0.4rem',
              padding: 0,
              textDecoration: 'underline'
            }}
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Show Less' : 'Show Full Scope'}
          </button>
        )}
      </div>

      <div className="result-footer">
        <div className="evidence-note">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span>{standard.source_evidence_note || "Official BIS Standard Specification"}</span>
        </div>

        {standard.source_url && (
          <a
            href={standard.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-link"
            title="Search reference on official BIS portal"
          >
            <span>BIS Reference Link</span>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}
