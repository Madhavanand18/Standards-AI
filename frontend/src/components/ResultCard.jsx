import React, { useState } from 'react';

const TYPE_LABELS = {
  normative_reference: 'Normative Reference',
  design_code: 'Design Code',
  related_product: 'Related Product',
  safety: 'Safety',
  test_method: 'Test Method',
  terminology: 'Terminology',
};

const getStatusBadgeData = (standard) => {
  const lc = standard.lifecycle;
  const rawStatus = (lc?.lifecycle_status || standard.status || 'UNKNOWN').toUpperCase();
  const amendmentCount = lc?.amendment_count ?? (lc?.amendments ? lc.amendments.length : 0);

  if (rawStatus === 'ACTIVE') {
    if (amendmentCount > 0) {
      return {
        label: 'Active + Amendments',
        classModifier: 'status-active-amended',
        tone: 'active',
        isWarning: false,
      };
    }
    return {
      label: 'Active',
      classModifier: 'status-active',
      tone: 'active',
      isWarning: false,
    };
  }
  if (rawStatus === 'SUPERSEDED') {
    return {
      label: 'Superseded',
      classModifier: 'status-superseded',
      tone: 'superseded',
      isWarning: true,
      warningTitle: 'Superseded Standard Notice',
      warningText: lc?.superseded_by
        ? `This standard has been superseded by ${lc.superseded_by}. (Informational reference for procurement specifications; verify applicable revision).`
        : 'This standard is recorded as superseded by a newer revision. (Informational reference for procurement specifications; verify applicable revision).',
    };
  }
  if (rawStatus === 'WITHDRAWN') {
    return {
      label: 'Withdrawn',
      classModifier: 'status-withdrawn',
      tone: 'withdrawn',
      isWarning: true,
      warningTitle: 'Withdrawn Standard Notice',
      warningText: 'This standard is designated as withdrawn in the BIS repository. (Informational reference for procurement specifications; verify current requirements).',
    };
  }
  return {
    label: rawStatus === 'UNKNOWN' ? 'Unknown' : rawStatus,
    classModifier: 'status-unknown',
    tone: 'unknown',
    isWarning: false,
  };
};

export default function ResultCard({ standard, rank: _rank }) {
  const [expanded, setExpanded] = useState(false);
  const [showAmendments, setShowAmendments] = useState(false);

  const scorePct = Math.round(standard.similarity_score * 100);
  const relevanceLabel = standard.relevance_label || (scorePct >= 60 ? 'High' : scorePct >= 40 ? 'Medium' : 'Low');

  const relationships = standard.relationships || [];
  const groupedRelationships = (standard.grouped_relationships && Object.keys(standard.grouped_relationships).length > 0)
    ? standard.grouped_relationships
    : relationships.reduce((acc, rel) => {
        const typeKey = (rel.relationship_type || 'other').toLowerCase();
        if (!acc[typeKey]) acc[typeKey] = [];
        acc[typeKey].push(rel);
        return acc;
      }, {});

  const statusInfo = getStatusBadgeData(standard);
  const lc = standard.lifecycle;
  const bisUrl = lc?.source_url || standard.source_url;

  // Determine latest amendment if available
  const amendments = lc?.amendments || [];
  const latestAmendment = amendments.length > 0
    ? [...amendments].sort((a, b) => (b.amendment_number || 0) - (a.amendment_number || 0))[0]
    : null;

  return (
    <div className="result-card" id={`standard-${standard.standard_number.replace(/[^a-zA-Z0-9]/g, '-')}`}>

      <div className="result-card-top">
        <div className="standard-badge-group">
          <span className="standard-num-badge">{standard.standard_number}</span>
          <span className={`status-badge ${statusInfo.classModifier}`}>
            {statusInfo.label}
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

      {/* Lifecycle & Version Intelligence Section */}
      <div className="lifecycle-section">
        <div className="lifecycle-header">
          <div className="lifecycle-header-left">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <strong>BIS Lifecycle & Version Intelligence</strong>
          </div>
          <span className="lifecycle-header-tag">Grounded BIS Data</span>
        </div>

        {statusInfo.isWarning && (
          <div className={`lifecycle-warning-box warning-${statusInfo.tone}`}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: '2px' }}>
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <div>
              <div className="lifecycle-warning-title">{statusInfo.warningTitle}</div>
              <div className="lifecycle-warning-text">{statusInfo.warningText}</div>
            </div>
          </div>
        )}

        <div className="lifecycle-grid">
          <div className="lifecycle-grid-item">
            <span className="lifecycle-label">Lifecycle Status</span>
            <span className={`lifecycle-value status-text-${statusInfo.tone}`}>
              {statusInfo.label}
            </span>
          </div>

          {(lc?.edition || standard.edition) && (
            <div className="lifecycle-grid-item">
              <span className="lifecycle-label">Edition / Version</span>
              <span className="lifecycle-value">{lc?.edition || standard.edition}</span>
            </div>
          )}

          {(lc?.year_of_publication || standard.year_of_publication) && (
            <div className="lifecycle-grid-item">
              <span className="lifecycle-label">Publication Year</span>
              <span className="lifecycle-value">{lc?.year_of_publication || standard.year_of_publication}</span>
            </div>
          )}

          {lc?.reaffirmed_year && (
            <div className="lifecycle-grid-item">
              <span className="lifecycle-label">Reaffirmed Year</span>
              <span className="lifecycle-value highlight-emerald">{lc.reaffirmed_year}</span>
            </div>
          )}

          {lc?.reviewed_year && (
            <div className="lifecycle-grid-item">
              <span className="lifecycle-label">Reviewed Year</span>
              <span className="lifecycle-value highlight-cyan">{lc.reviewed_year}</span>
            </div>
          )}

          <div className="lifecycle-grid-item">
            <span className="lifecycle-label">Amendments</span>
            <span className="lifecycle-value">
              {lc?.amendment_count ?? amendments.length} {((lc?.amendment_count ?? amendments.length) === 1) ? 'Amendment' : 'Amendments'}
            </span>
          </div>

          {latestAmendment && (
            <div className="lifecycle-grid-item">
              <span className="lifecycle-label">Latest Amendment</span>
              <span className="lifecycle-value">
                No. {latestAmendment.amendment_number} {latestAmendment.year ? `(${latestAmendment.year})` : ''}
              </span>
            </div>
          )}

          {lc?.superseded_by && (
            <div className="lifecycle-grid-item superseded-highlight-item">
              <span className="lifecycle-label">Superseded By</span>
              <span className="lifecycle-value highlight-amber">{lc.superseded_by}</span>
            </div>
          )}

          {lc?.supersedes && (
            <div className="lifecycle-grid-item">
              <span className="lifecycle-label">Supersedes</span>
              <span className="lifecycle-value">{lc.supersedes}</span>
            </div>
          )}
        </div>

        {amendments.length > 0 && (
          <div className="amendments-section">
            <button
              type="button"
              className="amendments-toggle-btn"
              onClick={() => setShowAmendments(!showAmendments)}
            >
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ transform: showAmendments ? 'rotate(90deg)' : 'none', transition: 'transform 0.15s' }}
              >
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
              <span>{showAmendments ? 'Hide Amendment History' : `View Verified Amendment History (${amendments.length})`}</span>
            </button>

            {showAmendments && (
              <div className="amendments-list">
                {amendments.map((a, idx) => (
                  <div key={a.amendment_number || idx} className="amendment-card">
                    <div className="amendment-top">
                      <span className="amendment-badge">Amendment No. {a.amendment_number}</span>
                      {a.year && <span className="amendment-year">Year {a.year}</span>}
                      {a.verification_date && <span className="amendment-vdate">Verified {a.verification_date}</span>}
                    </div>
                    {a.description && (
                      <p className="amendment-desc">{a.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

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

      {relationships.length > 0 && (
        <div className="related-standards-section">
          <div className="related-standards-header">
            <div className="related-header-left">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
              </svg>
              <strong>Related BIS Standards ({relationships.length})</strong>
            </div>
            <span className="related-header-tag">Deterministic Normative Links</span>
          </div>

          <div className="related-groups-list">
            {Object.entries(groupedRelationships).map(([typeKey, items]) => (
              <div key={typeKey} className="related-type-group">
                <div className="related-type-header">
                  <span className={`rel-type-badge rel-type-${typeKey}`}>
                    {TYPE_LABELS[typeKey] || typeKey.replace(/_/g, ' ')}
                  </span>
                  <span className="rel-count-badge">{items.length}</span>
                </div>

                <div className="related-items-container">
                  {items.map((rel, idx) => {
                    const target = rel.target_standard || {};
                    return (
                      <div key={rel.relationship_id || idx} className="related-item-card">
                        <div className="related-item-top">
                          <span className="related-std-num">{target.standard_number}</span>
                          <span className="related-std-title">{target.title}</span>
                        </div>
                        {(rel.evidence_text || rel.description) && (
                          <div className="related-evidence-text">
                            <span className="evidence-label">Evidence / Citation:</span> {rel.evidence_text || rel.description}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="result-footer">
        <div className="evidence-note">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span>{standard.source_evidence_note || (lc?.verification_note) || "Official BIS Standard Specification"}</span>
        </div>

        {bisUrl && (
          <a
            href={bisUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="source-link"
            title="Verify standard and requirements on official BIS Standards Portal (standards.bis.gov.in)"
          >
            <span>Verify on Official BIS Standards Portal</span>
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
