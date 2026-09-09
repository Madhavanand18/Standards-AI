import React, { useState } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

export default function DocumentUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [activePage, setActivePage] = useState(1);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Only PDF files (.pdf) are supported in this phase.');
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setError(null);
      setResult(null);
      setActivePage(1);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload failed with status HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      setActivePage(1);
    } catch (err) {
      console.error('Document upload failed:', err);
      setError(err.message || 'Failed to upload and extract document.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const activePageData = result?.pages?.find((p) => p.page_number === activePage) || result?.pages?.[0];

  return (
    <div className="doc-upload-card" id="doc-upload-section">
      <div className="doc-upload-header">
        <div className="doc-upload-title-group">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#60a5fa' }}>
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          <div>
            <h2 className="doc-upload-title">Tender & Specification PDF Ingestion</h2>
            <p className="doc-upload-desc">
              Upload procurement tender documents or technical specifications (up to 20 MB). Deterministically extracts text preserving page boundaries and technical identifiers.
            </p>
          </div>
        </div>
        <span className="doc-upload-badge">Run 6A Foundation</span>
      </div>

      <div className="doc-upload-controls">
        <div className="file-input-wrapper">
          <input
            type="file"
            id="tender-pdf-input"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            className="hidden-file-input"
          />
          <label htmlFor="tender-pdf-input" className="file-select-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <span>{selectedFile ? 'Change PDF File' : 'Select Tender PDF'}</span>
          </label>
          <span className="selected-filename">
            {selectedFile ? `${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)` : 'No PDF selected'}
          </span>
        </div>

        <button
          type="button"
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          className="extract-btn"
        >
          {loading ? (
            <>
              <span className="btn-spinner"></span>
              <span>Extracting Document...</span>
            </>
          ) : (
            <>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="4 17 10 11 4 5"></polyline>
                <line x1="12" y1="19" x2="20" y2="19"></line>
              </svg>
              <span>Extract Text Page-by-Page</span>
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="error-banner" role="alert" style={{ marginTop: '1rem' }}>
          <strong>Extraction Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="extraction-result-box">
          <div className="extraction-summary-top">
            <div className="summary-left">
              <span className={`status-badge status-doc-${result.status.toLowerCase()}`}>
                Status: {result.status}
              </span>
              <span className="summary-file-info">
                <strong>{result.filename}</strong> — {result.page_count} Page{result.page_count === 1 ? '' : 's'} ({(result.file_size / 1024).toFixed(1)} KB)
              </span>
            </div>
            <span className="summary-doc-id">ID: {result.document_id.slice(0, 8)}...</span>
          </div>

          {result.warnings && result.warnings.length > 0 && (
            <div className="extraction-warnings-box">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#fbbf24', flexShrink: 0, marginTop: '2px' }}>
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <div>
                <strong>Extraction Warnings:</strong>
                <ul style={{ paddingLeft: '1.2rem', marginTop: '0.25rem' }}>
                  {result.warnings.map((w, idx) => (
                    <li key={idx}>{w}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {result.metadata?.detected_sections?.length > 0 && (
            <div className="detected-sections-row">
              <span className="detected-label">Detected Tender Sections:</span>
              <div className="detected-badges-list">
                {result.metadata.detected_sections.map((sec, idx) => (
                  <span key={idx} className="detected-section-badge">{sec}</span>
                ))}
              </div>
            </div>
          )}

          <div className="page-preview-container">
            <div className="page-nav-bar">
              <span className="page-nav-label">
                Inspecting Page {activePage} of {result.page_count}:
              </span>
              <div className="page-btn-group">
                {result.pages?.map((p) => (
                  <button
                    key={p.page_number}
                    type="button"
                    className={`page-num-btn ${p.page_number === activePage ? 'active' : ''}`}
                    onClick={() => setActivePage(p.page_number)}
                  >
                    Page {p.page_number}
                    {!p.has_text && ' (empty)'}
                  </button>
                ))}
              </div>
            </div>

            {activePageData ? (
              <div className="page-text-card">
                <div className="page-text-header">
                  <span className="page-char-count">
                    {activePageData.character_count} Characters • {activePageData.word_count} Words
                  </span>
                  {activePageData.detected_headings?.length > 0 && (
                    <span className="page-headings-tag">
                      Headings: {activePageData.detected_headings.join(', ')}
                    </span>
                  )}
                </div>

                {activePageData.has_text ? (
                  <pre className="extracted-text-content">
                    {activePageData.cleaned_text}
                  </pre>
                ) : (
                  <div className="empty-page-notice">
                    <em>No extractable text found on page {activePage}. (Possible image or blank page).</em>
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-page-notice">No page data available.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
