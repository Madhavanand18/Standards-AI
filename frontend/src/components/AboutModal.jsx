import React, { useEffect } from 'react';

export default function AboutModal({ isOpen, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="about-dialog-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="modal-header-title-group">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <h2 id="about-dialog-title" className="modal-title">About Standards-AI</h2>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close About Dialog"
          >
            &times;
          </button>
        </div>

        <div className="modal-body">
          <div className="about-brand-card">
            <div className="about-emblem" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                <line x1="9" y1="7" x2="15" y2="7"></line>
                <line x1="9" y1="11" x2="13" y2="11"></line>
              </svg>
            </div>
            <div>
              <h3 className="about-name">Standards-AI</h3>
              <p className="about-tagline">Public Procurement Technical Intelligence & Recommendation Engine</p>
            </div>
          </div>

          <div className="about-section">
            <h4 className="about-section-heading">Core Objective</h4>
            <p className="about-text">
              Standards-AI assists public procurement authorities, tender specification drafters, and engineering contractors in instantly discovering applicable Indian Standards (IS), mandatory Quality Control Orders (QCOs), and official BIS certification requirements.
            </p>
          </div>

          <div className="about-section">
            <h4 className="about-section-heading">Key Technical Pillars</h4>
            <ul className="about-features-list">
              <li>
                <strong>Dense Semantic Search:</strong> Local multilingual neural embeddings match nuanced natural language tender clauses in English, Hindi, and Hinglish.
              </li>
              <li>
                <strong>Official Grounding:</strong> Strictly references verified Bureau of Indian Standards (BIS) documents, gazette notifications, and published amendments.
              </li>
              <li>
                <strong>Quality Control Orders (QCO):</strong> Flags statutory government notifications requiring compulsory ISI certification for public works and procurement.
              </li>
              <li>
                <strong>Lifecycle Intelligence:</strong> Alerts users if an Indian Standard is active, reaffirmed, superseded by a newer edition, or withdrawn.
              </li>
              <li>
                <strong>Direct PDF Workflow:</strong> Extracts procurement specifications directly from uploaded tender tender documents and routes them seamlessly into the search workflow.
              </li>
            </ul>
          </div>

          <div className="about-section">
            <h4 className="about-section-heading">Design Standard</h4>
            <p className="about-text">
              Built adhering to UX4G (Government of India Digital Service Design Standards) and classic, clean search interface principles: high contrast, zero clutter, generous whitespace, and restrained accessibility.
            </p>
          </div>
        </div>

        <div className="modal-footer">
          <a
            href="https://standards.bis.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="modal-btn-secondary"
          >
            <span>Visit BIS Standards Portal ↗</span>
          </a>
          <button
            type="button"
            className="modal-btn-primary"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
