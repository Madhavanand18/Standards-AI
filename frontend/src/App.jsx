import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';
import WorkflowSection from './components/WorkflowSection';
import DocumentUpload from './components/DocumentUpload';
import FuturePage from './components/FuturePage';
import Footer from './components/Footer';
import SettingsModal from './components/SettingsModal';
import AboutModal from './components/AboutModal';

const API_BASE = 'http://localhost:8000/api/v1';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(10);
  const [searchedQuery, setSearchedQuery] = useState('');
  const [results, setResults] = useState([]);
  const [totalMatches, setTotalMatches] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [auditDisclaimer, setAuditDisclaimer] = useState('');
  const [systemHealth, setSystemHealth] = useState(null);

  // UX & Flow state
  const [isFromDoc, setIsFromDoc] = useState(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [aboutModalOpen, setAboutModalOpen] = useState(false);

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

  const handleSearch = async (searchQuery, customLimit) => {
    const q = (searchQuery !== undefined ? searchQuery : query).trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    setSearchedQuery(q);

    const activeLimit = customLimit || limit;

    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: q, limit: activeLimit }),
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

  // PDF Analyzer -> Home Page Workflow Handler
  const handleAnalyzeFromDoc = (extractedText) => {
    const text = (extractedText || '').trim();
    if (!text) return;

    setQuery(text);
    setIsFromDoc(true);
    setActiveTab('home');

    // Smoothly scroll to search area
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Automatically execute the search
    handleSearch(text, limit);
  };

  const handleClearQuery = () => {
    setQuery('');
    setIsFromDoc(false);
    setSearchedQuery('');
    setResults([]);
  };

  return (
    <div className="app-shell">
      {/* Global Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemHealth={systemHealth}
        onOpenSettings={() => setSettingsModalOpen(true)}
        onOpenAbout={() => setAboutModalOpen(true)}
      />

      <main className="main-content" role="main">
        {/* ── 1. HOME TAB: SPECIFICATION SEARCH & RESULTS ── */}
        {activeTab === 'home' && (
          <>
            <HeroSection />

            <SearchBar
              query={query}
              setQuery={(val) => {
                setQuery(val);
                if (!val) setIsFromDoc(false);
              }}
              onSearch={handleSearch}
              loading={loading}
              limit={limit}
              setLimit={setLimit}
              isFromDoc={isFromDoc}
              onClearQuery={handleClearQuery}
            />

            {error && (
              <div className="error-banner" role="alert">
                <strong>Search Error: </strong> {error}
              </div>
            )}

            {loading && (
              <div className="state-box" aria-live="polite">
                <div className="spinner"></div>
                <div className="state-title">Searching Indian Standards Database</div>
                <div className="state-desc">
                  Performing dense multilingual semantic search and metadata scoring over official BIS standards.
                </div>
              </div>
            )}

            {!loading && searchedQuery && results.length > 0 && (
              <section className="results-container" aria-label="Search Results">
                <div className="results-top-bar">
                  <h2 className="results-count-title">
                    Found {totalMatches || results.length} Potentially Applicable Standard{(totalMatches || results.length) !== 1 ? 's' : ''}
                  </h2>
                  <span className="results-verified-badge">
                    ✓ Grounded in Authoritative BIS Scope
                  </span>
                </div>

                {results.map((standard, index) => (
                  <ResultCard
                    key={standard.standard_number || index}
                    standard={standard}
                    rank={index + 1}
                  />
                ))}

                {auditDisclaimer && (
                  <div className="audit-disclaimer-card" role="note">
                    <div className="audit-title">Procurement Compliance & Verification Notice</div>
                    <p className="audit-text">{auditDisclaimer}</p>
                  </div>
                )}
              </section>
            )}

            {!loading && searchedQuery && results.length === 0 && !error && (
              <div className="state-box" role="status">
                <div className="state-icon">🔍</div>
                <div className="state-title">No Indian Standards Matched This Specification</div>
                <div className="state-desc">
                  Try refining the technical keywords, specifying material grades (e.g., Fe 500, IS 1786), or entering alternative procurement descriptions.
                </div>
              </div>
            )}

            {!searchedQuery && !loading && (
              <WorkflowSection />
            )}
          </>
        )}

        {/* ── 2. TENDER DOCUMENT ANALYZER TAB ── */}
        {activeTab === 'pdf-analyzer' && (
          <DocumentUpload onAnalyzeText={handleAnalyzeFromDoc} />
        )}

        {/* ── 3. FUTURE CAPABILITIES & ROADMAP TAB ── */}
        {activeTab === 'future' && <FuturePage />}
      </main>

      {/* Global Minimal Footer */}
      <Footer />

      {/* ── MODALS ── */}
      <SettingsModal
        isOpen={settingsModalOpen}
        onClose={() => setSettingsModalOpen(false)}
        limit={limit}
        setLimit={setLimit}
        systemHealth={systemHealth}
      />

      <AboutModal
        isOpen={aboutModalOpen}
        onClose={() => setAboutModalOpen(false)}
      />
    </div>
  );
}
