import React from 'react';

const ACTIVE_CAPABILITIES = [
  {
    title: 'Multilingual Semantic Retrieval',
    desc: 'Dense semantic retrieval across Indian Standards scopes and specifications. Understands procurement terminology in English, Hindi (Devanagari), and Hinglish while maintaining exact engineering identifiers (IS numbers, grades, dimensions).',
    status: 'Operational in Prototype',
    authority: 'Core Retrieval Engine',
  },
  {
    title: 'Tender Document Extraction & Direct Routing',
    desc: 'Parses procurement specifications, tender schedules, and Bills of Quantities directly from PDF documents (up to 20 MB) and routes them into the central recommendation engine in a continuous workflow.',
    status: 'Operational in Prototype',
    authority: 'Document Parser',
  },
  {
    title: 'Statutory QCO Compliance Intelligence',
    desc: 'Identifies compulsory Quality Control Orders (QCO) issued by Government Ministries, detailing enforcement dates, referenced editions, transition clauses, and links to Gazette notifications.',
    status: 'Operational in Prototype',
    authority: 'Gazette Tracking',
  },
  {
    title: 'Lifecycle & Superseded Edition Tracking',
    desc: 'Validates official BIS statuses (Active, Reaffirmed, Superseded, Withdrawn), identifies published amendments, and flags warning notices before procurement officers issue purchase orders.',
    status: 'Operational in Prototype',
    authority: 'BIS Registry',
  },
];

const ROADMAP_ITEMS = [
  {
    phase: 'Phase 1 · Next Release',
    title: 'Standards Comparison & Clause Diffing',
    desc: 'Side-by-side technical clause and tolerance comparison across standard editions, superseded revisions, and allied codes to instantly isolate grade differences.',
    status: 'Planned',
  },
  {
    phase: 'Phase 2 · Scheduled',
    title: 'Procurement Workspace & Compliance Dossiers',
    desc: 'Organize standards recommendations into structured project dossiers for specific tender packages, generating exportable compliance matrices for bid documentation.',
    status: 'Planned',
  },
  {
    phase: 'Phase 3 · Scheduled',
    title: 'Automated Gazette QCO Alerts & Subscriptions',
    desc: 'Department-level notification alerts when new Gazette Quality Control Orders or amendments are notified by ministries affecting active procurement schedules.',
    status: 'Planned',
  },
  {
    phase: 'Phase 4 · Future',
    title: 'Multi-Volume Tender BOQ Cross-referencing',
    desc: 'Batch processing of multi-hundred page tender volumes with automated reconciliation between Bills of Quantities (BOQ) line items and technical specification schedules.',
    status: 'Planned',
  },
];

export default function FuturePage() {
  return (
    <div className="roadmap-page-container">
      {/* Page Header */}
      <div className="roadmap-page-header">
        <span className="panel-eyebrow">NATIONAL PROCUREMENT PLATFORM ROADMAP</span>
        <h1 className="roadmap-page-title">Service Capabilities & Development Roadmap</h1>
        <p className="roadmap-page-subtitle">
          Transparent public documentation distinguishing verified operational capabilities in the
          current prototype from scheduled enterprise features under the national procurement expansion plan.
        </p>
      </div>

      {/* Section 1: Operational Prototype Capabilities (Structured UX4G List) */}
      <div className="roadmap-block">
        <div className="roadmap-block-header">
          <div className="block-header-title-group">
            <span className="status-dot-green" aria-hidden="true"></span>
            <h2 className="block-title">Currently Operational in Prototype (Run 8B/10)</h2>
          </div>
          <span className="block-badge badge-operational">4 Verified Modules</span>
        </div>

        <div className="roadmap-list">
          {ACTIVE_CAPABILITIES.map((item, idx) => (
            <div key={idx} className="roadmap-list-item item-operational">
              <div className="item-left-col">
                <span className="item-authority-pill">{item.authority}</span>
                <span className="item-status-tag tag-operational">✓ {item.status}</span>
              </div>
              <div className="item-main-col">
                <h3 className="item-title">{item.title}</h3>
                <p className="item-desc">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 2: Planned Enterprise Capabilities (Structured UX4G Timeline) */}
      <div className="roadmap-block" style={{ marginTop: 'var(--space-2xl)' }}>
        <div className="roadmap-block-header">
          <div className="block-header-title-group">
            <span className="status-dot-blue" aria-hidden="true"></span>
            <h2 className="block-title">Planned Enterprise Capabilities (Scheduled Roadmap)</h2>
          </div>
          <span className="block-badge badge-planned">Future Releases</span>
        </div>

        <div className="roadmap-timeline">
          {ROADMAP_ITEMS.map((item, idx) => (
            <div key={idx} className="timeline-entry">
              <div className="timeline-marker" aria-hidden="true">
                <span className="timeline-node"></span>
                {idx < ROADMAP_ITEMS.length - 1 && <span className="timeline-line"></span>}
              </div>
              <div className="timeline-body">
                <div className="timeline-top">
                  <span className="timeline-phase">{item.phase}</span>
                  <span className="item-status-tag tag-planned">Scheduled</span>
                </div>
                <h3 className="timeline-title">{item.title}</h3>
                <p className="timeline-desc">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
