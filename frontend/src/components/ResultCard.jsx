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
        tooltip: 'Standard is active and in force, with published BIS amendments.',
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
  const [showEvents, setShowEvents] = useState(false);

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
      {/* ── LEVEL 1: SCANNABLE HEADER & ESSENTIAL COMPLIANCE STATUS ── */}
      <div className="card-level1">
        <div className="card-top-badges">
          <div className="badge-cluster-left">
            <span className="std-num-pill">{standard.standard_number}</span>

            <span className={`status-pill ${statusInfo.className}`} title={statusInfo.tooltip}>
              {statusInfo.label}
            </span>

            {certStatus === 'MANDATORY' && (
              <span
                className="compliance-summary-pill comp-mandatory"
                title="Mandatory Certification: Product requires compulsory ISI Mark under Quality Control Order"
              >
                Mandatory Certification
              </span>
            )}

            {certStatus === 'VOLUNTARY' && (
              <span
                className="compliance-summary-pill comp-voluntary"
                title="Voluntary Certification: Available for quality assurance under standard BIS scheme"
              >
                Voluntary Certification
              </span>
            )}

            {qcoStatus === 'APPLICABLE' && certStatus !== 'MANDATORY' && (
              <span
                className="compliance-summary-pill comp-mandatory"
                title="Quality Control Order (QCO) — indicates product is subject to statutory quality enforcement"
              >
                QCO Applicable
              </span>
            )}

            {standard.category && (
              <span className="category-pill">{standard.category}</span>
            )}
          </div>

          <div className="badge-cluster-right">
            <span className={`relevance-pill rel-${relevanceLabel.toLowerCase()}`}>
              {relevanceLabel} Relevance
            </span>
            <span className="score-match-pct">{scorePct}% Match</span>
          </div>
        </div>

        <h3 id={`title-${(standard.standard_number || 'std').replace(/[^a-zA-Z0-9]/g, '-')}`} className="card-title">
          {standard.title}
        </h3>

        {/* Match Context Snippet */}
        <p className="card-match-summary">
          <span className="match-summary-prefix">Match Context: </span>
          {standard.explanation
            ? standard.explanation
            : standard.scope_snippet
            ? standard.scope_snippet
            : standard.scope
            ? standard.scope.length > 180
              ? `${standard.scope.slice(0, 180)}...`
              : standard.scope
            : 'Authoritative Indian Standard specification matched on technical procurement keywords.'}
        </p>

        {/* Level 1 Action Bar */}
        <div className="card-level1-actions">
          <button
            type="button"
            className="view-details-toggle-btn"
            onClick={() => setExpanded(!expanded)}
            aria-expanded={expanded}
            aria-controls={`details-${(standard.standard_number || 'std').replace(/[^a-zA-Z0-9]/g, '-')}`}
          >
            <span>{expanded ? 'Hide Details' : 'View Details'}</span>
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
              title="Verify authoritative record on official BIS Standards Portal (standards.bis.gov.in)"
            >
              <span>Verify on BIS Portal</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
          )}
        </div>
      </div>

      {/* ── LEVEL 2: PROGRESSIVE DISCLOSURE (STRUCTURED SECTIONS) ── */}
      {expanded && (
        <div
          id={`details-${(standard.standard_number || 'std').replace(/[^a-zA-Z0-9]/g, '-')}`}
          className="card-level2-details"
        >
          {/* Section 1: Why this standard? */}
          {standard.explanation && (
            <div className="detail-section-box">
              <div className="detail-section-header">
                <div className="detail-section-title-group">
                  <svg className="detail-section-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                  </svg>
                  <span>Why This Standard Was Recommended</span>
                </div>
                <span className="detail-section-tag">Semantic Match Intelligence</span>
              </div>
              <p className="detail-text">{standard.explanation}</p>
            </div>
          )}

          {/* Section 2: Lifecycle & Version Intelligence */}
          <div className="detail-section-box">
            <div className="detail-section-header">
              <div className="detail-section-title-group">
                <svg className="detail-section-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span>Lifecycle & Version Intelligence</span>
              </div>
              <span className="detail-section-tag">Grounded BIS Record</span>
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
                  <span className="kv-value" title="Reaffirmation confirms the standard was re-evaluated and remains valid without revisions.">
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
                  <span>{showAmendments ? 'Hide Amendment History' : `View Verified Amendment History (${amendments.length})`}</span>
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

          {/* Section 3: Procurement Compliance & QCO Intelligence */}
          <div className="detail-section-box">
            <div className="detail-section-header">
              <div className="detail-section-title-group">
                <svg className="detail-section-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  <polyline points="9 12 11 14 15 10"></polyline>
                </svg>
                <span>Procurement Compliance & Quality Control Orders (QCO)</span>
              </div>
              <span className="detail-section-tag">Gazette & Regulatory Data</span>
            </div>

            {/* Plain-Language Explainer for QCO */}
            <div className="term-explainer-banner">
              <strong>Quality Control Order (QCO)</strong> — statutory order issued by Central Ministries making BIS compliance and ISI Mark certification mandatory for public procurement, manufacturing, and import.
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
                  <span className="kv-label">QCO Order Reference</span>
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
                  <span className="kv-label">Version Transition & Applicability Clause</span>
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
                  <span>View Gazette Notification</span>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                </a>
              </div>
            )}

            {/* Regulatory Milestone Timeline Toggle */}
            {comp?.events && comp.events.length > 0 && (
              <div style={{ marginTop: '0.75rem' }}>
                <button
                  type="button"
                  className="sub-accordion-btn"
                  onClick={() => setShowEvents(!showEvents)}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ transform: showEvents ? 'rotate(90deg)' : 'none', transition: 'transform 150ms ease' }}>
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                  <span>{showEvents ? 'Hide Regulatory Timeline' : `View Regulatory Milestone Timeline (${comp.events.length})`}</span>
                </button>

                {showEvents && (
                  <div className="sub-accordion-list">
                    {comp.events.map((ev, idx) => (
                      <div key={ev.id || idx} className="sub-item-card">
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '2px' }}>
                          <span className="std-num-pill" style={{ fontSize: '0.68rem', padding: '1px 6px' }}>{ev.event_type || 'EVENT'}</span>
                          <strong>{ev.title}</strong>
                          {ev.event_date && <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>· {ev.event_date}</span>}
                        </div>
                        {ev.description && <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{ev.description}</p>}
                        {ev.source_url && (
                          <a href={ev.source_url} target="_blank" rel="noopener noreferrer" className="bis-verify-link" style={{ padding: 0, marginTop: '4px', fontSize: '0.75rem' }}>
                            <span>View Source Document ↗</span>
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div className="notice-box notice-info" style={{ marginTop: '0.75rem' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: '2px' }} aria-hidden="true">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              <span>
                Procurement Aid Notice: Sourced from Gazette notifications and BIS registries. Serves as an evidence-backed procurement aid; verify official tender specifications for mandatory compliance clauses.
              </span>
            </div>
          </div>

          {/* Section 4: Official Scope & Applicability */}
          <div className="detail-section-box">
            <div className="detail-section-header">
              <div className="detail-section-title-group">
                <svg className="detail-section-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span>Official Scope & Technical Applicability</span>
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
                <span>{showFullScope ? 'Show Less' : 'Show Full Scope'}</span>
              </button>
            )}
          </div>

          {/* Section 5: Related BIS Standards */}
          {rawRelationships.length > 0 && (
            <div className="detail-section-box">
              <div className="detail-section-header">
                <div className="detail-section-title-group">
                  <svg className="detail-section-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                  </svg>
                  <span>Related BIS Standards ({rawRelationships.length})</span>
                </div>
                <span className="detail-section-tag">Deterministic Normative Links</span>
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

          {/* Section 6: Evidence & Official Source */}
          <div className="detail-section-box">
            <div className="detail-section-header">
              <div className="detail-section-title-group">
                <svg className="detail-section-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>Evidence & Official Source</span>
              </div>
              <span className="detail-section-tag">Verifiable Sources</span>
            </div>

            <div className="evidence-row">
              <span className="evidence-source-tag">
                {standard.source_evidence_note || lc?.verification_note || "Official Bureau of Indian Standards Specification"}
              </span>

              {bisUrl && (
                <a
                  href={bisUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bis-verify-link"
                >
                  <span>Open Official Record (standards.bis.gov.in) ↗</span>
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </article>
  );
}
