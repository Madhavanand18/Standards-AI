import React from 'react';

const QUICK_QUERIES = [
  "12 mm TMT reinforcement bars for RCC construction",
  "Hot rolled structural steel plates for bridge fabrication",
  "PVC insulated copper cables for 450/750V internal wiring",
  "High density polyethylene HDPE pipes for potable water supply",
  "Industrial safety helmets for construction workers",
  "Common burnt clay building bricks for masonry walls",
  "Design concrete mix proportioning guidelines"
];

export default function SearchBar({ query, setQuery, onSearch, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !loading) {
        onSearch(query);
      }
    }
  };

  return (
    <div className="search-card">
      <label htmlFor="procurement-query" className="search-label">
        Technical Specification / Requirement Description
      </label>
      <div className="search-input-wrapper">
        <textarea
          id="procurement-query"
          className="search-textarea"
          rows={3}
          placeholder="Enter procurement item description, material specifications, or tender clause (e.g. '12 mm TMT reinforcement bars for RCC construction')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <div className="search-actions">
          <span className="char-count">{query.length} characters</span>
          <button
            id="search-btn"
            className="search-btn"
            onClick={() => onSearch(query)}
            disabled={loading || !query.trim()}
          >
            {loading ? (
              <>
                <div
                  style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: '#fff',
                    borderRadius: '50%',
                    animation: 'spin 0.6s linear infinite'
                  }}
                />
                <span>Searching Standards...</span>
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                <span>Find Applicable Standards</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div className="quick-queries">
        <div className="quick-queries-label">Sample Tender Specifications (Click to test):</div>
        <div className="chips-container">
          {QUICK_QUERIES.map((item, idx) => (
            <button
              key={idx}
              className="chip"
              type="button"
              onClick={() => {
                setQuery(item);
                onSearch(item);
              }}
              disabled={loading}
            >
              {item}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
