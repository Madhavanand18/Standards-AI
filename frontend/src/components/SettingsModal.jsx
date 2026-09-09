import React, { useEffect } from 'react';

export default function SettingsModal({ isOpen, onClose, limit, setLimit, systemHealth }) {
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
        aria-labelledby="settings-dialog-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="modal-header-title-group">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            <h2 id="settings-dialog-title" className="modal-title">Application Settings</h2>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close Settings Dialog"
          >
            &times;
          </button>
        </div>

        <div className="modal-body">
          {/* Prototype Notice */}
          <div className="settings-notice-banner">
            <span className="settings-notice-badge">Prototype Mode</span>
            <p className="settings-notice-text">
              Settings reflect active local evaluation defaults. Administrative preferences and cloud syncing will become configurable upon enterprise deployment.
            </p>
          </div>

          {/* Active Configuration */}
          <div className="settings-section">
            <h3 className="settings-section-title">Search & Retrieval Preferences</h3>

            <div className="setting-item">
              <div className="setting-label-group">
                <label htmlFor="settings-result-limit" className="setting-label">Default Results Limit</label>
                <span className="setting-help">Maximum number of candidate standards to return per query.</span>
              </div>
              <select
                id="settings-result-limit"
                className="setting-select"
                value={limit || 10}
                onChange={(e) => setLimit(Number(e.target.value))}
              >
                <option value={5}>Top 5 Standards</option>
                <option value={10}>Top 10 Standards</option>
                <option value={15}>Top 15 Standards</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-label-group">
                <span className="setting-label">Multilingual Normalization</span>
                <span className="setting-help">Normalizes English, Hindi (Devanagari), and Hinglish technical terms.</span>
              </div>
              <span className="setting-status-pill pill-active">Active (Default)</span>
            </div>

            <div className="setting-item">
              <div className="setting-label-group">
                <span className="setting-label">Relevance Threshold Scoring</span>
                <span className="setting-help">Combines dense cosine similarity with BIS domain metadata scoring.</span>
              </div>
              <span className="setting-status-pill pill-active">Active (Default)</span>
            </div>
          </div>

          {/* System & API Status */}
          <div className="settings-section">
            <h3 className="settings-section-title">Local Environment Connectivity</h3>

            <div className="setting-item">
              <div className="setting-label-group">
                <span className="setting-label">API Gateway</span>
                <span className="setting-code">http://localhost:8000/api/v1</span>
              </div>
              <span className="setting-status-pill pill-active">
                {systemHealth?.status === 'HEALTHY' ? 'Connected' : 'Online'}
              </span>
            </div>

            <div className="setting-item">
              <div className="setting-label-group">
                <span className="setting-label">Indexed Standards in SQLite</span>
                <span className="setting-help">Seed repository of verified Bureau of Indian Standards records.</span>
              </div>
              <span className="setting-value-badge">
                {systemHealth?.standards_in_db ? `${systemHealth.standards_in_db} records` : '10 canonical'}
              </span>
            </div>

            <div className="setting-item">
              <div className="setting-label-group">
                <span className="setting-label">Vector Store</span>
                <span className="setting-help">In-memory Qdrant dense vector index.</span>
              </div>
              <span className="setting-value-badge">Qdrant Active</span>
            </div>
          </div>

          {/* Upcoming / Disabled Settings */}
          <div className="settings-section">
            <h3 className="settings-section-title">Enterprise Settings (Scheduled)</h3>

            <div className="setting-item disabled">
              <div className="setting-label-group">
                <span className="setting-label">Single Sign-On (Gov.in / Parichay SSO)</span>
                <span className="setting-help">Departmental procurement officer authentication.</span>
              </div>
              <span className="setting-status-pill pill-planned">Planned</span>
            </div>

            <div className="setting-item disabled">
              <div className="setting-label-group">
                <span className="setting-label">Email Alerts for Gazette QCOs</span>
                <span className="setting-help">Automatic notifications when new Quality Control Orders are published.</span>
              </div>
              <span className="setting-status-pill pill-planned">Planned</span>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button
            type="button"
            className="modal-btn-primary"
            onClick={onClose}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
