import React, { useState } from 'react';

const RELATIONSHIP_LABELS = {
  normative_reference: 'Normative Reference',
  design_code: 'Design Code',
  related_product: 'Related Product',
  safety: 'Safety Code',
  test_method: 'Test Method',
  terminology: 'Terminology',
  other: 'Related Standard',
};

const getStatusBadgeData = (standard) => {
  const lc = standard.lifecycle;
  const rawStatus = (lc?.lifecycle_status || standard.status || 'UNKNOWN').toUpperCase();
  const amendmentCount = lc?.amendment_count ?? (lc?.amendments ? lc.amendments.length : 0);

  if (rawStatus === 'ACTIVE') {
    if (amendmentCount > 0) {
      return {
        label: `Active (${amendmentCount} Amend.)`,
        className: 'status-active-amended',
        tooltip: 'Standard is currently valid and in force, with published BIS amendments.',
        isWarning: false,
      };
    }
    return {
      label: 'Active',
      className: 'status-active',
      tooltip: 'Standard is currently valid and in force with the Bureau of Indian Standards.',
      isWarning: false,
    };
  }
  if (rawStatus === 'SUPERSEDED') {
    return {
      label: 'Superseded',
      className: 'status-superseded',
      tooltip: lc?.superseded_by
        ? `This standard has been superseded by ${lc.superseded_by}.`
        : 'This standard is recorded as superseded by a newer edition.',
      isWarning: true,
      warningTitle: 'Superseded Standard Notice',
      warningText: lc?.superseded_by
        ? `This standard has been superseded by ${lc.superseded_by}. Verify which edition is specified in the procurement tender before issuing purchase orders.`
        : 'This standard has been superseded by a newer edition. Verify applicable edition for procurement compliance.',
    };
  }
  if (rawStatus === 'WITHDRAWN') {
    return {
      label: 'Withdrawn',
      className: 'status-withdrawn',
      tooltip: 'This standard has been withdrawn by BIS.',
      isWarning: true,
      warningTitle: 'Withdrawn Standard Notice',
      warningText: 'This standard has been designated as withdrawn by BIS. Consult the procurement authority for an approved replacement.',
    };
  }
  return {
    label: rawStatus === 'UNKNOWN' ? 'Status Unspecified' : rawStatus,
    className: 'status-unknown',
    tooltip: 'Standard status is not explicitly verified in the seed repository.',
    isWarning: false,
  };
};

export default function ResultCard({ standard, rank: _rank }) {
  const [expanded, setExpanded] = useState(false);
  const [showFullScope, setShowFullScope] = useState(false);
  const [showAmendments, setShowAmendments] = useState(false);

  const lc = standard.lifecycle;
  const comp = standard.compliance;
  const statusInfo = getStatusBadgeData(standard);

  const scorePct = Math.round((standard.similarity_score || 0) * 100);
  const relevanceLabel =
    standard.relevance_label || (scorePct >= 60 ? 'High' : scorePct >= 40 ? 'Medium' : 'Low');

  const bisUrl = lc?.source_url || standard.source_url;
  const amendments = lc?.amendments || [];

  // Grouped relationships
  const rawRelationships = standard.relationships || [];
  const groupedRelationships =
    standard.grouped_relationships && Object.keys(standard.grouped_relationships).length > 0
      ? standard.grouped_relationships
      : rawRelationships.reduce((acc, rel) => {
          const typeKey = (rel.relationship_type || 'other').toLowerCase();
          if (!acc[typeKey]) acc[typeKey] = [];
          acc[typeKey].push(rel);
          return acc;
        }, {});

  // Certification summary
  const certStatus = comp?.certification_status;
  const qcoStatus = comp?.qco_status;

  return (
    <article
      className="universal-result-card"
      id={`standard-${(standard.standard_number || 'std').replace(/[^a-zA-Z0-9]/g, '-')}`}
      aria-labelledby={`title-${(standard.standard_number || 'std').replace(/[^a-zA-Z0-9]/g, '-')}`}
    >
      {/* ── UX4G LEVEL 1: OFFICIAL STANDARD RECORD HEADER ── */}
      <div className="card-level1">
        {/* Row 1: Standard Number & Match Relevance */}
        <div className="record-header-row">
          <div className="record-id-group">
            <span className="std-number-tag">{standard.standard_number}</span>
            {standard.category && (
              <span className="record-category-tag">{standard.category}</span>
            )}
            {(lc?.year_of_publication || standard.year_of_publication) && (
              <span className="record-meta-text">
                Published {lc?.year_of_publication || standard.year_of_publication}
              </span>
            )}
          </div>

          <div className="record-score-group">
            <span className={`relevance-badge rel-${relevanceLabel.toLowerCase()}`}>
              {relevanceLabel} Relevance
            </span>
            <span className="score-text">{scorePct}% Match</span>
          </div>
        </div>

        {/* Row 2: Standard Title */}
        <h3 id={`title-${(standard.standard_number || 'std').replace(/[^a-zA-Z0-9]/g, '-')}`} className="record-title">
          {standard.title}
        </h3>

        {/* Row 3: Status & Compliance Information Bar */}
        <div className="record-status-bar">
          <div className="status-item">
            <span className="status-item-label">Status:</span>
            <span className={`status-pill ${statusInfo.className}`} title={statusInfo.tooltip}>
              {statusInfo.label}
            </span>
          </div>

          {certStatus === 'MANDATORY' && (
            <div className="status-item">
              <span className="status-item-label">Certification:</span>
              <span className="compliance-summary-pill comp-mandatory">
                Mandatory (ISI Mark)
              </span>
            </div>
          )}

          {certStatus === 'VOLUNTARY' && (
            <div className="status-item">
              <span className="status-item-label">Certification:</span>
              <span className="compliance-summary-pill comp-voluntary">
                Voluntary Scheme
              </span>
            </div>
          )}

          {qcoStatus === 'APPLICABLE' && (
            <div className="status-item">
              <span className="status-item-label">QCO Order:</span>
              <span className="compliance-summary-pill comp-mandatory">
                Applicable in Force
              </span>
            </div>
          )}

          {lc?.edition && (
            <div className="status-item">
              <span className="status-item-label">Edition:</span>
              <span className="record-meta-val">{lc.edition}</span>
            </div>
          )}
        </div>

        {/* Row 4: QCO Supporting Explanation Banner */}
        {qcoStatus === 'APPLICABLE' && (
          <div className="term-explainer-banner" role="note">
            <strong>Quality Control Order (QCO) Applicable:</strong> Statutory government order issued under the Bureau of Indian Standards Act, 2016 making compliance and ISI Mark certification mandatory for public procurement and trade.
          </div>
        )}

        {/* Row 5: Match Context Snippet */}
        <div className="record-match-context">
          <span className="context-label">Match Scope Context: </span>
          <span className="context-text">
            {standard.explanation
              ? standard.explanation
              : standard.scope_snippet
              ? standard.scope_snippet
              : standard.scope
              ? standard.scope.length > 200
                ? `${standard.scope.slice(0, 200)}...`
                : standard.scope
              : 'Matched against technical procurement keywords in the official Bureau of Indian Standards scope.'}
          </span>
        </div>

        {/* Row 6: Primary Actions (View Details & BIS Verification Link) */}
        <div className="card-level1-actions">
          <button
            type="button"
            className="view-details-toggle-btn"
            onClick={() => setExpanded(!expanded)}
            aria-expanded={expanded}
            aria-controls={`details-${(standard.standard_number || 'std').replace(/[^a-zA-Z0-9]/g, '-')}`}
          >
            <span>{expanded ? 'Hide Complete Specification' : 'View Full Details & Clauses'}</span>
            <svg
              className={`view-details-chevron ${expanded ? 'expanded' : ''}`}
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>

          {bisUrl && (
            <a
              href={bisUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="bis-verify-link"
              title="Open authoritative standard record on official BIS Portal (standards.bis.gov.in)"
            >
              <span>Verify on BIS Portal (standards.bis.gov.in)</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
          )}
        </div>
      </div>

      {/* ── UX4G LEVEL 2: STRUCTURED REGISTRY DATA ACCORDIONS ── */}
      {expanded && (
        <div
          id={`details-${(standard.standard_number || 'std').replace(/[^a-zA-Z0-9]/g, '-')}`}
          className="card-level2-details"
        >
          {/* Section 1: Why This Standard Was Recommended */}
          {standard.explanation && (
            <div className="detail-section-box">
              <div className="detail-section-header">
                <div className="detail-section-title-group">
                  <span className="section-title-icon" aria-hidden="true">💡</span>
                  <span className="section-title-text">Recommendation Justification</span>
                </div>
                <span className="detail-section-tag">Grounded Match Analysis</span>
              </div>
              <p className="detail-text">{standard.explanation}</p>
            </div>
          )}

          {/* Section 2: Lifecycle & Version Intelligence */}
          <div className="detail-section-box">
            <div className="detail-section-header">
              <div className="detail-section-title-group">
                <span className="section-title-icon" aria-hidden="true">📋</span>
                <span className="section-title-text">Lifecycle & Version Tracking</span>
              </div>
              <span className="detail-section-tag">BIS Official Registry</span>
            </div>

            {statusInfo.isWarning && (
              <div className="notice-box notice-warning">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: '2px' }} aria-hidden="true">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <div>
                  <strong>{statusInfo.warningTitle}: </strong>
                  <span>{statusInfo.warningText}</span>
                </div>
              </div>
            )}

            <div className="detail-kv-grid">
              <div className="kv-item">
                <span className="kv-label">Lifecycle Status</span>
                <span className="kv-value">{statusInfo.label}</span>
              </div>

              {(lc?.edition || standard.edition) && (
                <div className="kv-item">
                  <span className="kv-label">Edition</span>
                  <span className="kv-value">{lc?.edition || standard.edition}</span>
                </div>
              )}

              {(lc?.year_of_publication || standard.year_of_publication) && (
                <div className="kv-item">
                  <span className="kv-label">Publication Year</span>
                  <span className="kv-value">{lc?.year_of_publication || standard.year_of_publication}</span>
                </div>
              )}

              {lc?.reaffirmed_year && (
                <div className="kv-item">
                  <span className="kv-label">Reaffirmed Year</span>
                  <span className="kv-value" title="Reaffirmation confirms the standard was evaluated and remains valid without revision.">
                    {lc.reaffirmed_year} ✓
                  </span>
                </div>
              )}

              {lc?.reviewed_year && (
                <div className="kv-item">
                  <span className="kv-label">Reviewed Year</span>
                  <span className="kv-value">{lc.reviewed_year}</span>
                </div>
              )}

              <div className="kv-item">
                <span className="kv-label">Amendments</span>
                <span className="kv-value">
                  {lc?.amendment_count ?? amendments.length} {(lc?.amendment_count ?? amendments.length) === 1 ? 'Amendment' : 'Amendments'}
                </span>
              </div>

              {lc?.superseded_by && (
                <div className="kv-item" style={{ gridColumn: 'span 2' }}>
                  <span className="kv-label">Superseded By</span>
                  <span className="kv-value" style={{ color: 'var(--warning-text)' }}>{lc.superseded_by}</span>
                </div>
              )}

              {lc?.supersedes && (
                <div className="kv-item" style={{ gridColumn: 'span 2' }}>
                  <span className="kv-label">Supersedes Older Standard</span>
                  <span className="kv-value">{lc.supersedes}</span>
                </div>
              )}
            </div>

            {/* Amendments History Toggle */}
            {amendments.length > 0 && (
              <div style={{ marginTop: '0.75rem' }}>
                <button
                  type="button"
                  className="sub-accordion-btn"
                  onClick={() => setShowAmendments(!showAmendments)}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ transform: showAmendments ? 'rotate(90deg)' : 'none', transition: 'transform 150ms ease' }}>
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                  <span>{showAmendments ? 'Hide Amendment History' : `View Published Amendments (${amendments.length})`}</span>
                </button>

                {showAmendments && (
                  <div className="sub-accordion-list">
                    {amendments.map((a, idx) => (
                      <div key={a.amendment_number || idx} className="sub-item-card">
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '4px' }}>
                          <strong>Amendment No. {a.amendment_number}</strong>
                          {a.year && <span style={{ color: 'var(--text-muted)' }}>({a.year})</span>}
                          {a.verification_date && <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>· Verified {a.verification_date}</span>}
                        </div>
                        {a.description && <p style={{ color: 'var(--text-secondary)' }}>{a.description}</p>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Section 3: Statutory QCO & Procurement Compliance */}
          <div className="detail-section-box">
            <div className="detail-section-header">
              <div className="detail-section-title-group">
                <span className="section-title-icon" aria-hidden="true">⚖️</span>
                <span className="section-title-text">Statutory Quality Control Orders & Compliance</span>
              </div>
              <span className="detail-section-tag">Gazette Notification</span>
            </div>

            <div className="detail-kv-grid">
              <div className="kv-item">
                <span className="kv-label">Certification Scheme</span>
                <span className="kv-value">
                  {comp?.certification_scheme || (comp?.certification_status === 'MANDATORY' ? 'Scheme I (ISI Mark)' : 'Standard BIS Scheme')}
                </span>
              </div>

              <div className="kv-item">
                <span className="kv-label">Certification Status</span>
                <span className="kv-value">
                  {comp?.certification_status === 'MANDATORY' ? 'Mandatory (Compulsory)' :
                   comp?.certification_status === 'VOLUNTARY' ? 'Voluntary' :
                   'Not Formally Identified'}
                </span>
              </div>

              <div className="kv-item">
                <span className="kv-label">QCO Status</span>
                <span className="kv-value">
                  {comp?.qco_status === 'APPLICABLE' ? 'Applicable (In Force)' :
                   comp?.qco_status === 'UPCOMING' ? 'Upcoming Order' :
                   'Not Identified in Dataset'}
                </span>
              </div>

              {comp?.issuing_authority && (
                <div className="kv-item">
                  <span className="kv-label">Issuing Authority</span>
                  <span className="kv-value">{comp.issuing_authority}</span>
                </div>
              )}

              {(comp?.qco_title || comp?.qco_reference) && (
                <div className="kv-item" style={{ gridColumn: 'span 2' }}>
                  <span className="kv-label">QCO Order Title / Reference</span>
                  <span className="kv-value">
                    {comp.qco_title || ''} {comp.qco_reference ? `(${comp.qco_reference})` : ''}
                  </span>
                </div>
              )}

              {comp?.enforcement_date && (
                <div className="kv-item">
                  <span className="kv-label">Enforcement Date</span>
                  <span className="kv-value">{comp.enforcement_date}</span>
                </div>
              )}

              {comp?.referenced_standard_edition && (
                <div className="kv-item">
                  <span className="kv-label">Referenced in Order</span>
                  <span className="kv-value">{comp.referenced_standard_edition}</span>
                </div>
              )}

              {comp?.latest_standard_version && comp.latest_standard_version !== comp.referenced_standard_edition && (
                <div className="kv-item">
                  <span className="kv-label">Latest Standard Version</span>
                  <span className="kv-value" style={{ color: 'var(--primary-text)' }}>{comp.latest_standard_version}</span>
                </div>
              )}

              {comp?.qco_clause_standard_applicability && (
                <div className="kv-item" style={{ gridColumn: 'span 2' }}>
                  <span className="kv-label">Applicability Clause</span>
                  <span className="kv-value" style={{ fontWeight: 400, fontSize: '0.82rem' }}>
                    {comp.qco_clause_standard_applicability}
                  </span>
                </div>
              )}
            </div>

            {/* Evidence Link for QCO */}
            {comp?.evidence_source_url && (
              <div className="evidence-row" style={{ marginTop: '0.75rem' }}>
                <span className="evidence-source-tag">
                  Official Gazette Evidence: {comp.evidence_source_title || 'Ministry Notification'}
                  {comp.last_verified ? ` · Verified ${comp.last_verified}` : ''}
                </span>
                <a
                  href={comp.evidence_source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bis-verify-link"
                >
                  <span>View Gazette Notification ↗</span>
                </a>
              </div>
            )}
          </div>

          {/* Section 4: Official Scope & Applicability */}
          <div className="detail-section-box">
            <div className="detail-section-header">
              <div className="detail-section-title-group">
                <span className="section-title-icon" aria-hidden="true">📖</span>
                <span className="section-title-text">Official Scope & Technical Coverage</span>
              </div>
              <span className="detail-section-tag">Authoritative BIS Scope</span>
            </div>

            <p className="detail-text">
              {showFullScope ? standard.scope : (standard.scope_snippet || standard.scope)}
            </p>

            {standard.scope && standard.scope.length > 280 && (
              <button
                type="button"
                className="sub-accordion-btn"
                onClick={() => setShowFullScope(!showFullScope)}
              >
                <span>{showFullScope ? 'Show Less' : 'Show Complete Technical Scope'}</span>
              </button>
            )}
          </div>

          {/* Section 5: Related BIS Standards */}
          {rawRelationships.length > 0 && (
            <div className="detail-section-box">
              <div className="detail-section-header">
                <div className="detail-section-title-group">
                  <span className="section-title-icon" aria-hidden="true">🔗</span>
                  <span className="section-title-text">Normative References & Allied Standards ({rawRelationships.length})</span>
                </div>
                <span className="detail-section-tag">Normative Links</span>
              </div>

              <div className="related-groups-container">
                {Object.entries(groupedRelationships).map(([typeKey, items]) => (
                  <div key={typeKey} style={{ marginBottom: '8px' }}>
                    <div className="rel-type-heading">
                      {RELATIONSHIP_LABELS[typeKey] || typeKey.replace(/_/g, ' ')} ({items.length})
                    </div>
                    {items.map((rel, idx) => {
                      const target = rel.target_standard || {};
                      return (
                        <div key={rel.relationship_id || idx} className="rel-card-item">
                          <div>
                            <span className="rel-card-num">{target.standard_number}</span>
                            <span className="rel-card-title">{target.title}</span>
                          </div>
                          {(rel.evidence_text || rel.description) && (
                            <div className="rel-card-evidence">
                              <span>Citation / Evidence: </span>{rel.evidence_text || rel.description}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 6: Official Verification Record */}
          <div className="detail-section-box">
            <div className="detail-section-header">
              <div className="detail-section-title-group">
                <span className="section-title-icon" aria-hidden="true">🏛️</span>
                <span className="section-title-text">Authoritative Verification Record</span>
              </div>
              <span className="detail-section-tag">BIS Verified</span>
            </div>

            <div className="evidence-row">
              <span className="evidence-source-tag">
                {standard.source_evidence_note || lc?.verification_note || "Official Bureau of Indian Standards Record"}
              </span>

              {bisUrl && (
                <a
                  href={bisUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bis-verify-link"
                >
                  <span>Open Record on standards.bis.gov.in ↗</span>
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </article>
  );
}
