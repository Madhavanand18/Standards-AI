import React, { useState } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

export default function DocumentUpload({ onAnalyzeText }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [extractionResult, setExtractionResult] = useState(null);
  const [activePage, setActivePage] = useState(1);
  const [copied, setCopied] = useState(false);
  const [analyzeScope, setAnalyzeScope] = useState('all'); // 'all' or 'page'

  const handleFileSelection = (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Only PDF documents (.pdf) are supported.');
      setSelectedFile(null);
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      setUploadError('Document exceeds 20 MB limit.');
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
    setUploadError(null);
    setExtractionResult(null);
    setActivePage(1);
    setAnalyzeScope('all');
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    handleFileSelection(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    handleFileSelection(file);
  };

  const handleExtract = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload error (HTTP ${res.status})`);
      }

      const data = await res.json();
      setExtractionResult(data);
      setActivePage(1);
      setAnalyzeScope('all');
    } catch (err) {
      console.error('PDF extraction failed:', err);
      setUploadError(err.message || 'Failed to upload and extract tender document.');
      setExtractionResult(null);
    } finally {
      setUploading(false);
    }
  };

  const activePageData =
    extractionResult?.pages?.find((p) => p.page_number === activePage) ||
    extractionResult?.pages?.[0];

  const handleCopyText = () => {
    const textToCopy =
      analyzeScope === 'page'
        ? activePageData?.cleaned_text || extractionResult?.extracted_text || ''
        : extractionResult?.extracted_text ||
          extractionResult?.pages?.map((p) => p.cleaned_text).filter(Boolean).join('\n\n') ||
          '';

    if (!textToCopy) return;

    navigator.clipboard
      .writeText(textToCopy)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
  };

  const handleTriggerAnalyze = () => {
    if (!extractionResult || !onAnalyzeText) return;

    // Collect text based on user selection
    let textToAnalyze = '';
    if (analyzeScope === 'page' && activePageData?.cleaned_text) {
      textToAnalyze = activePageData.cleaned_text;
    } else {
      textToAnalyze =
        extractionResult.extracted_text ||
        extractionResult.pages?.map((p) => p.cleaned_text).filter(Boolean).join('\n\n') ||
        '';
    }

    if (!textToAnalyze.trim()) {
      setUploadError('No extractable text found to analyze.');
      return;
    }

    // Call top-level handler to switch to Home, populate search query, and trigger search
    onAnalyzeText(textToAnalyze.trim());
  };

  const totalWords = extractionResult?.pages
    ? extractionResult.pages.reduce((sum, p) => sum + (p.word_count || 0), 0)
    : 0;

  return (
    <div className="pdf-analyzer-page">
      {/* Page Header */}
      <div className="page-intro-header">
        <h1 className="page-intro-title">Tender Document Analyzer</h1>
        <p className="page-intro-subtitle">
          Upload technical specifications, tender schedules, or Bills of Quantities (PDF up to 20 MB).
          Extracts page-by-page specification text and routes it directly to the Standards-AI search engine.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div
        className={`pdf-upload-dropzone ${isDragging ? 'dropzone-active' : ''}`}
        role="region"
        aria-label="PDF Document Upload"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="dropzone-content">
          <div className="dropzone-icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="12" y1="18" x2="12" y2="12"></line>
              <polyline points="9 15 12 12 15 15"></polyline>
            </svg>
          </div>

          <div className="dropzone-prompt">Select or Drag a Procurement Tender PDF</div>
          <div className="dropzone-sub">Supports multi-page technical specification PDFs up to 20 MB</div>

          <input
            type="file"
            id="tender-pdf-file-input"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            className="file-hidden-input"
          />

          <label htmlFor="tender-pdf-file-input" className="file-choose-btn">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <span>{selectedFile ? 'Change Selected PDF' : 'Select PDF File'}</span>
          </label>

          {selectedFile && (
            <div className="selected-file-chip">
              <span>📄 {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
            </div>
          )}

          <button
            type="button"
            className="extract-action-btn"
            onClick={handleExtract}
            disabled={!selectedFile || uploading}
          >
            {uploading ? (
              <>
                <span className="spinner spinner-white" aria-hidden="true"></span>
                <span>Extracting Document Text...</span>
              </>
            ) : (
              <>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <polyline points="4 17 10 11 4 5"></polyline>
                  <line x1="12" y1="19" x2="20" y2="19"></line>
                </svg>
                <span>Extract Text From PDF</span>
              </>
            )}
          </button>
        </div>
      </div>

      {uploadError && (
        <div className="error-banner" role="alert">
          <strong>Notice: </strong> {uploadError}
        </div>
      )}

      {/* Extracted Document Viewer */}
      {extractionResult && (
        <div className="extracted-doc-container">
          <div className="extracted-doc-header">
            <div className="doc-info-left">
              <span className="std-num-pill" style={{ fontSize: '0.75rem' }}>
                {extractionResult.status || 'EXTRACTED'}
              </span>
              <span className="doc-filename">{extractionResult.filename}</span>
              <span className="doc-meta-badge">
                {extractionResult.page_count} Page{extractionResult.page_count === 1 ? '' : 's'} · {totalWords || extractionResult.total_words || 0} Words · {(extractionResult.file_size / 1024).toFixed(1)} KB
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Doc ID: {extractionResult.document_id ? extractionResult.document_id.slice(0, 8) : 'local'}...
            </span>
          </div>

          {/* Page Navigator Tabs */}
          {extractionResult.pages && extractionResult.pages.length > 1 && (
            <div className="page-tabs-bar" role="tablist" aria-label="Extracted Pages">
              {extractionResult.pages.map((p) => (
                <button
                  key={p.page_number}
                  type="button"
                  className={`page-tab-btn ${p.page_number === activePage ? 'active' : ''}`}
                  onClick={() => setActivePage(p.page_number)}
                  role="tab"
                  aria-selected={p.page_number === activePage}
                >
                  Page {p.page_number}
                  {!p.has_text && ' (empty)'}
                </button>
              ))}
            </div>
          )}

          {/* Extracted Text Box */}
          <div className="extracted-text-wrapper">
            <div className="text-meta-row">
              <span>
                {activePageData
                  ? `Viewing Page ${activePageData.page_number} (${activePageData.character_count} Characters · ${activePageData.word_count} Words)`
                  : 'Document Text'}
              </span>

              <button
                type="button"
                className={`copy-btn ${copied ? 'copied' : ''}`}
                onClick={handleCopyText}
                title="Copy text to clipboard"
              >
                {copied ? (
                  <>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                    <span>Copied ✓</span>
                  </>
                ) : (
                  <>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    <span>Copy Text</span>
                  </>
                )}
              </button>
            </div>

            {activePageData && activePageData.has_text ? (
              <pre className="extracted-text-pre">{activePageData.cleaned_text}</pre>
            ) : (
              <div className="state-desc" style={{ fontStyle: 'italic', padding: '1rem 0' }}>
                No text content extracted on this page (likely image-based or blank).
              </div>
            )}
          </div>

          {/* Analyze Action Bar: Seamless Redirect to Home Search */}
          <div className="analyze-action-bar">
            <div className="analyze-action-info">
              <strong style={{ fontSize: '0.9rem', color: 'var(--text-main)', display: 'block', marginBottom: '2px' }}>
                Analyze Extracted Requirements on Home Search
              </strong>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Routes extracted technical specification text to the main recommendation engine and automatically searches applicable Indian Standards.
              </p>
            </div>

            <div className="analyze-action-controls">
              {extractionResult.pages && extractionResult.pages.length > 1 && (
                <div className="scope-toggle-group">
                  <button
                    type="button"
                    className={`scope-toggle-btn ${analyzeScope === 'all' ? 'active' : ''}`}
                    onClick={() => setAnalyzeScope('all')}
                  >
                    Full Tender Document
                  </button>
                  <button
                    type="button"
                    className={`scope-toggle-btn ${analyzeScope === 'page' ? 'active' : ''}`}
                    onClick={() => setAnalyzeScope('page')}
                  >
                    Page {activePage} Only
                  </button>
                </div>
              )}

              <button
                type="button"
                className="analyze-tender-btn"
                onClick={handleTriggerAnalyze}
                title="Send extracted text to Home page and search immediately"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                <span>Analyze on Home Page &rarr;</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
