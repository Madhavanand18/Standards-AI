import React from 'react';
import BeforeAfterSection from './BeforeAfterSection';

const PROCESS_STEPS = [
  {
    number: '01',
    title: 'Describe your requirement',
    desc: 'Enter item descriptions, material grades, or extract technical specification clauses directly from a tender PDF document.',
  },
  {
    number: '02',
    title: 'Understand the specification',
    desc: 'Parses English, Hindi, and Hinglish technical terminology while preserving critical dimensions, voltages, and grade designations.',
  },
  {
    number: '03',
    title: 'Find applicable standards',
    desc: 'Retrieves relevant Indian Standards from the official Bureau of Indian Standards catalogue based on verified scope coverage.',
  },
  {
    number: '04',
    title: 'Review compliance and evidence',
    desc: 'Surfaces statutory Quality Control Orders (QCO), mandatory ISI mark requirements, edition statuses, and published amendments.',
  },
];

const CAPABILITIES = [
  {
    title: 'Standards Search',
    desc: 'Natural language search across Indian Standards scopes, specifications, and titles to identify authoritative technical codes.',
    badge: 'Core Service',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
    ),
  },
  {
    title: 'Tender / PDF Analysis',
    desc: 'Extracts technical procurement clauses directly from tender schedules, NITs, and BOQ documents (PDF up to 20 MB).',
    badge: 'Document Aid',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
      </svg>
    ),
  },
  {
    title: 'Lifecycle & Amendments',
    desc: 'Identifies active, reaffirmed, superseded, and withdrawn standards editions, with warnings before ordering superseded revisions.',
    badge: 'Registry Data',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
      </svg>
    ),
  },
  {
    title: 'Compliance / QCO',
    desc: 'Highlights statutory Quality Control Orders (QCO) issued by Government Ministries making ISI certification legally compulsory.',
    badge: 'Statutory Orders',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        <polyline points="9 12 11 14 15 10"></polyline>
      </svg>
    ),
  },
  {
    title: 'Evidence & Verification',
    desc: 'Provides authoritative citations and direct verification links to the official BIS portal (standards.bis.gov.in).',
    badge: 'Authoritative',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
        <polyline points="15 3 21 3 21 9"></polyline>
        <line x1="10" y1="14" x2="21" y2="3"></line>
      </svg>
    ),
  },
  {
    title: 'Multilingual Input',
    desc: 'Accepts procurement specifications written in English, Hindi (Devanagari script), and romanized Hinglish.',
    badge: 'Multilingual',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="2" y1="12" x2="22" y2="12"></line>
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
      </svg>
    ),
  },
];

export default function WorkflowSection() {
  return (
    <section className="service-guide-section" aria-label="Procurement Guidance and Verification Workflow">
      {/* ── FEATURE 1: FROM MANUAL SEARCH TO STANDARDS INTELLIGENCE ── */}
      <BeforeAfterSection />

      {/* ── SECTION 1: HOW IT WORKS (UX4G Process Pipeline) ── */}
      <div className="section-panel">
        <div className="panel-header-row">
          <div>
            <span className="panel-eyebrow">PROCESS WORKFLOW</span>
            <h2 id="guide-heading" className="panel-heading">
              How the Standards Recommendation Service Works
            </h2>
          </div>
          <span className="panel-caption">Grounded in official Bureau of Indian Standards records</span>
        </div>

        <div className="process-steps-track">
          {PROCESS_STEPS.map((step, idx) => (
            <div key={idx} className="process-step-item">
              <div className="step-num-bar">
                <span className="step-num-text">{step.number}</span>
                {idx < PROCESS_STEPS.length - 1 && <span className="step-bar-divider" aria-hidden="true"></span>}
              </div>
              <h3 className="step-heading">{step.title}</h3>
              <p className="step-description">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── SECTION 2: CORE PRODUCT CAPABILITIES ── */}
      <div className="section-panel" style={{ marginTop: 'var(--space-xl)' }}>
        <div className="panel-header-row">
          <div>
            <span className="panel-eyebrow">SERVICE CAPABILITIES</span>
            <h2 className="panel-heading">
              Public Procurement Verification Features
            </h2>
          </div>
          <span className="panel-caption">Designed for procurement officers, tender drafters, and contractors</span>
        </div>

        <div className="capabilities-grid">
          {CAPABILITIES.map((cap, idx) => (
            <div key={idx} className="capability-item">
              <div className="cap-top-row">
                <div className="cap-icon-box" aria-hidden="true">
                  {cap.icon}
                </div>
                <span className="cap-badge">{cap.badge}</span>
              </div>
              <h3 className="cap-title">{cap.title}</h3>
              <p className="cap-desc">{cap.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
