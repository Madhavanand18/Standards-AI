import React from 'react';

const ACTIVE_CAPABILITIES = [
  {
    title: 'Multilingual Semantic Retrieval',
    desc: 'Dense vector search powered by local sentence transformer embeddings. Directly understands procurement specs in English, Hindi (Devanagari), and romanized Hinglish while preserving exact technical identifiers (IS numbers, grades, dimensions).',
    status: 'Available in Prototype',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="2" y1="12" x2="22" y2="12"></line>
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
      </svg>
    ),
  },
  {
    title: 'Tender Document Direct Routing',
    desc: 'Extracts page-by-page specification clauses from procurement PDFs (up to 20 MB) and routes them into the central recommendation engine in a continuous, unified workflow.',
    status: 'Available in Prototype',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
      </svg>
    ),
  },
  {
    title: 'Statutory QCO Compliance Intelligence',
    desc: 'Identifies compulsory Quality Control Orders (QCO) issued by Government Ministries, detailing enforcement dates, referenced standard editions, and links to Gazette notifications.',
    status: 'Available in Prototype',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        <polyline points="9 12 11 14 15 10"></polyline>
      </svg>
    ),
  },
  {
    title: 'Lifecycle Tracking & Superseded Edition Warnings',
    desc: 'Tracks authoritative BIS statuses (Active, Reaffirmed, Superseded, Withdrawn), verified published amendments, and flags warning notices when ordering superseded revisions.',
    status: 'Available in Prototype',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
      </svg>
    ),
  },
];

const ROADMAP_ITEMS = [
  {
    title: 'Standards Comparison & Clause Diff',
    desc: 'Side-by-side technical clause and property comparison across revisions, superseded editions, and related standards to quickly isolate tolerance and grade differences.',
    status: 'Planned',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <line x1="18" y1="20" x2="18" y2="10"></line>
        <line x1="12" y1="20" x2="12" y2="4"></line>
        <line x1="6" y1="20" x2="6" y2="14"></line>
      </svg>
    ),
  },
  {
    title: 'Procurement Workspace & Dossiers',
    desc: 'Organize standards recommendations into structured project dossiers for specific tender packages, with exportable compliance matrices for bid documentation.',
    status: 'Planned',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
      </svg>
    ),
  },
  {
    title: 'Saved Searches & Regulatory Alerts',
    desc: 'Automated monitoring of relevant Indian Standards and notification alerts when new Gazette Quality Control Orders or amendments are published by ministries.',
    status: 'Planned',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
      </svg>
    ),
  },
  {
    title: 'Multi-Volume Tender BOQ Cross-referencing',
    desc: 'Batch processing of multi-hundred page tender volumes with automated cross-referencing between Bills of Quantities (BOQ) and technical specification schedules.',
    status: 'Planned',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
        <polyline points="2 17 12 22 22 17"></polyline>
        <polyline points="2 12 12 17 22 12"></polyline>
      </svg>
    ),
  },
];

export default function FuturePage() {
  return (
    <div className="future-page-container">
      <div className="page-intro-header">
        <h1 className="page-intro-title">Platform Capabilities & Roadmap</h1>
        <p className="page-intro-subtitle">
          Standards-AI is designed as an enterprise technical intelligence platform for public procurement.
          Below is a transparent overview distinguishing live features from scheduled capabilities.
        </p>
      </div>

      {/* Section 1: Active In Current Prototype */}
      <section className="roadmap-section" aria-labelledby="live-features-title">
        <div className="roadmap-section-header">
          <div className="roadmap-title-row">
            <span className="status-dot-green" aria-hidden="true"></span>
            <h2 id="live-features-title" className="roadmap-section-heading">Currently Available in Prototype</h2>
          </div>
          <span className="roadmap-section-sub">Verified & functional in Run 8B</span>
        </div>

        <div className="future-cards-grid">
          {ACTIVE_CAPABILITIES.map((item, idx) => (
            <div key={idx} className="future-card card-active-feature">
              <div className="future-card-icon icon-active">{item.icon}</div>
              <h3 className="future-card-title">{item.title}</h3>
              <p className="future-card-desc">{item.desc}</p>
              <div className="future-card-footer">
                <span className="live-feature-pill">✓ Functional in Prototype</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Section 2: Planned Future Capabilities */}
      <section className="roadmap-section" aria-labelledby="planned-features-title" style={{ marginTop: 'var(--space-2xl)' }}>
        <div className="roadmap-section-header">
          <div className="roadmap-title-row">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary)' }} aria-hidden="true">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            <h2 id="planned-features-title" className="roadmap-section-heading">Planned Enterprise Capabilities</h2>
          </div>
          <span className="roadmap-section-sub">Scheduled for production release</span>
        </div>

        <div className="future-cards-grid">
          {ROADMAP_ITEMS.map((item, idx) => (
            <div key={idx} className="future-card">
              <div className="future-card-icon">{item.icon}</div>
              <h3 className="future-card-title">{item.title}</h3>
              <p className="future-card-desc">{item.desc}</p>
              <div className="future-card-footer">
                <span className="coming-soon-pill">Planned Capability</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
