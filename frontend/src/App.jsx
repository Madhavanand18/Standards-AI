import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';

const API_BASE = 'http://localhost:8000/api/v1';

export default function App() {
  const [query, setQuery] = useState('');
  const [searchedQuery, setSearchedQuery] = useState('');
  const [results, setResults] = useState([]);
  const [totalMatches, setTotalMatches] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [auditDisclaimer, setAuditDisclaimer] = useState('');
  const [systemHealth, setSystemHealth] = useState(null);

  // Fetch system health on mount
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setSystemHealth(data))
      .catch((err) => {
        console.warn('Backend offline or health check failed:', err);
      });
  }, []);

  const handleSearch = async (searchQuery) => {
    const q = (searchQuery || query).trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    setSearchedQuery(q);

    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: q, limit: 10 }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Search error (HTTP ${res.status})`);
      }

      const data = await res.json();
      setResults(data.results || []);
      setTotalMatches(data.total_matches || (data.results ? data.results.length : 0));
      setAuditDisclaimer(data.audit_disclaimer || '');
    } catch (err) {
      console.error('Search request failed:', err);
      setError(
        err.message || 'Unable to connect to the backend server. Please verify FastAPI is running at http://localhost:8000.'
      );
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header systemHealth={systemHealth} />

      <SearchBar
        query={query}
        setQuery={setQuery}
        onSearch={handleSearch}
        loading={loading}
      />

      {error && (
        <div className="error-banner" role="alert">
          <strong>Search Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="loading-box">
          <div className="spinner"></div>
          <p>Running local dense multilingual semantic search over BIS database...</p>
        </div>
      )}

      {!loading && searchedQuery && results.length > 0 && (
        <section className="results-section">
          <div className="results-header">
            <h2 className="results-count">
              Found {results.length} Potentially Applicable Standard{results.length > 1 ? 's' : ''}
            </h2>
            <span className="anti-hallucination-badge">
              ✓ Grounded in Verified BIS Scope
            </span>
          </div>

          <div className="results-list">
            {results.map((standard, index) => (
              <ResultCard
                key={standard.standard_number || index}
                standard={standard}
                rank={index + 1}
              />
            ))}
          </div>

          {auditDisclaimer && (
            <div className="audit-disclaimer-box">
              <div className="audit-disclaimer-title">Procurement Audit & Compliance Notice</div>
              <p>{auditDisclaimer}</p>
            </div>
          )}
        </section>
      )}

      {!loading && searchedQuery && results.length === 0 && !error && (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>No Indian Standards matched this specification</h3>
          <p>Try refining the technical keywords or specifying the material/grade directly.</p>
        </div>
      )}

      {!searchedQuery && !loading && (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>Ready for Technical Specification Input</h3>
          <p>Enter a procurement item description above or click one of the sample tender queries to retrieve applicable Indian Standards.</p>
        </div>
      )}
    </div>
  );
}
