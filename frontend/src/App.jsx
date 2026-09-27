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

import { API_BASE } from './config';

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

  // Sarvam AI Indian-Language Translation State (Feature 2)
  const [translationData, setTranslationData] = useState(null);
  const [loadingText, setLoadingText] = useState('Searching Standards...');

  // UX & Flow state
  const [isFromDoc, setIsFromDoc] = useState(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [aboutModalOpen, setAboutModalOpen] = useState(false);

  // Unicode pattern covering 22 official Indian language scripts
  const INDIC_REGEX = /[\u0900-\u0D7F\u0600-\u06FF]/;

  // Fetch system health on mount
  useEffect(() => {
    fetch(`${API_BASE.replace(/\/api\/v1\/?$/, '')}/api/v1/health`)
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
    let finalQuery = q;
    let translationInfo = null;

    // Feature 2: Indian-Language Input via Sarvam AI
    // Rule 1 & 4: English input directly to search, do NOT call Sarvam.
    // Rule 2 & 3: Indian-language input -> Sarvam Translate (at most once per search) -> English requirement.
    if (INDIC_REGEX.test(q)) {
      setLoadingText('Translating Indian language with Sarvam AI...');
      try {
        const transRes = await fetch(`${API_BASE}/translate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: q, source_language_code: 'auto' }),
        });

        if (transRes.ok) {
          const transData = await transRes.json();
          if (transData.is_translated && transData.translated_text) {
            finalQuery = transData.translated_text;
            translationInfo = {
              originalText: q,
              translatedText: transData.translated_text,
              sourceLanguage: transData.source_language_code,
              isTranslated: true,
              error: null,
            };
          } else if (transData.error) {
            translationInfo = {
              originalText: q,
              translatedText: q,
              sourceLanguage: null,
              isTranslated: false,
              error: transData.error,
            };
          }
        } else {
          const errData = await transRes.json().catch(() => ({}));
          translationInfo = {
            originalText: q,
            translatedText: q,
            sourceLanguage: null,
            isTranslated: false,
            error: errData.detail || `Sarvam AI translation unavailable (HTTP ${transRes.status}).`,
          };
        }
      } catch (transErr) {
        console.warn('Sarvam translation error:', transErr);
        translationInfo = {
          originalText: q,
          translatedText: q,
          sourceLanguage: null,
          isTranslated: false,
          error: 'Sarvam AI translation connection failed. Continuing with direct search.',
        };
      }
    } else {
      // Already English input: Sarvam is NOT called!
      translationInfo = null;
    }

    setTranslationData(translationInfo);
    setLoadingText('Searching Indian Standards Database...');

    try {
      const res = await fetch(`${API_BASE.replace(/\/api\/v1\/?$/, '')}/api/v1/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: finalQuery, limit: activeLimit }),
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
        err.message || `Unable to connect to the backend server. Please verify the API is running at ${API_BASE}.`
      );
      setResults([]);
    } finally {
      setLoading(false);
      setLoadingText('Searching Standards...');
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
    setTranslationData(null);
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
              loadingText={loadingText}
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
                <div className="state-title">{loadingText}</div>
                <div className="state-desc">
                  {loadingText.includes('Sarvam')
                    ? 'Connecting to Sarvam AI text translation engine (sarvam-translate:v1) for Indian-language requirement translation.'
                    : 'Performing dense multilingual semantic search and metadata scoring over official BIS standards.'}
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

                {/* Sarvam AI Indian-Language Translation Banner (Feature 2) */}
                {translationData && translationData.isTranslated && (
                  <div className="sarvam-translation-banner" role="region" aria-label="Sarvam AI Translation">
                    <div className="sarvam-banner-header">
                      <span className="sarvam-badge">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                          <path d="M5 8l6 6"></path>
                          <path d="M4 14l6-6 2-3"></path>
                          <path d="M2 5h12"></path>
                          <path d="M7 2h1"></path>
                          <path d="M22 22l-5-10-5 10"></path>
                          <path d="M14 18h6"></path>
                        </svg>
                        Sarvam AI Translation
                      </span>
                      <span className="sarvam-model-tag">sarvam-translate:v1</span>
                      {translationData.sourceLanguage && (
                        <span className="sarvam-lang-tag">Detected Source: {translationData.sourceLanguage}</span>
                      )}
                    </div>
                    <div className="sarvam-banner-content">
                      <div className="sarvam-translated-row">
                        <span className="sarvam-label">Translated Requirement (English):</span>
                        <span className="sarvam-translated-text">"{translationData.translatedText}"</span>
                      </div>
                      <div className="sarvam-original-row">
                        <span className="sarvam-label">Original Indian-Language Input:</span>
                        <span className="sarvam-original-text">"{translationData.originalText}"</span>
                      </div>
                    </div>
                  </div>
                )}

                {translationData && translationData.error && (
                  <div className="sarvam-notice-card" role="status">
                    <span className="sarvam-notice-icon">ℹ️</span>
                    <div className="sarvam-notice-text">
                      <strong>Sarvam AI Translation Notice:</strong> {translationData.error}{' '}
                      <span className="sarvam-notice-subtext">Conducted search directly using original input via multilingual normalization.</span>
                    </div>
                  </div>
                )}

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
              <>
                {translationData && translationData.isTranslated && (
                  <div className="sarvam-translation-banner" role="region" aria-label="Sarvam AI Translation">
                    <div className="sarvam-banner-header">
                      <span className="sarvam-badge">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                          <path d="M5 8l6 6"></path>
                          <path d="M4 14l6-6 2-3"></path>
                          <path d="M2 5h12"></path>
                          <path d="M7 2h1"></path>
                          <path d="M22 22l-5-10-5 10"></path>
                          <path d="M14 18h6"></path>
                        </svg>
                        Sarvam AI Translation
                      </span>
                      <span className="sarvam-model-tag">sarvam-translate:v1</span>
                      {translationData.sourceLanguage && (
                        <span className="sarvam-lang-tag">Detected Source: {translationData.sourceLanguage}</span>
                      )}
                    </div>
                    <div className="sarvam-banner-content">
                      <div className="sarvam-translated-row">
                        <span className="sarvam-label">Translated Requirement (English):</span>
                        <span className="sarvam-translated-text">"{translationData.translatedText}"</span>
                      </div>
                      <div className="sarvam-original-row">
                        <span className="sarvam-label">Original Indian-Language Input:</span>
                        <span className="sarvam-original-text">"{translationData.originalText}"</span>
                      </div>
                    </div>
                  </div>
                )}

                {translationData && translationData.error && (
                  <div className="sarvam-notice-card" role="status">
                    <span className="sarvam-notice-icon">ℹ️</span>
                    <div className="sarvam-notice-text">
                      <strong>Sarvam AI Translation Notice:</strong> {translationData.error}{' '}
                      <span className="sarvam-notice-subtext">Conducted search directly using original input via multilingual normalization.</span>
                    </div>
                  </div>
                )}

                <div className="state-box" role="status">
                  <div className="state-icon">🔍</div>
                  <div className="state-title">No Indian Standards Matched This Specification</div>
                  <div className="state-desc">
                    Try refining the technical keywords, specifying material grades (e.g., Fe 500, IS 1786), or entering alternative procurement descriptions.
                  </div>
                </div>
              </>
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
