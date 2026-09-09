import React from 'react';

const ECOSYSTEM_ITEMS = [
  {
    badge: 'BIS',
    title: 'Bureau of Indian Standards',
    desc: 'National Standards Body of India',
  },
  {
    badge: 'IS',
    title: 'Indian Standards',
    desc: 'Authoritative Technical Specifications',
  },
  {
    badge: 'ISI Mark',
    title: 'Product Certification Scheme',
    desc: 'Mandatory / Voluntary Conformity',
  },
  {
    badge: 'QCO',
    title: 'Quality Control Orders',
    desc: 'Statutory Ministry Compulsory Orders',
  },
  {
    badge: 'Hallmark',
    title: 'Precious Metals Scheme',
    desc: 'Assay & Purity Verification',
  },
  {
    badge: 'NBC',
    title: 'National Building Code',
    desc: 'Structural & Safety Guidelines',
  },
];

export default function HeroSection() {
  return (
    <section className="hero-section" aria-labelledby="hero-main-title">
      <div className="hero-grid">
        {/* Left Column: Heading, Description & Service Authority */}
        <div className="hero-content">
          <div className="hero-eyebrow-wrap">
            <span className="hero-kicker">
              <span className="kicker-flag-strip" aria-hidden="true">
                <span className="strip-saffron"></span>
                <span className="strip-white"></span>
                <span className="strip-green"></span>
              </span>
              <span>INDIAN STANDARDS · PROCUREMENT</span>
            </span>
          </div>

          <h1 id="hero-main-title" className="hero-title">
            Find the Indian Standards that apply to your requirement.
          </h1>

          <p className="hero-subtitle">
            Turn procurement specifications, tender requirements, and product descriptions
            into relevant Indian Standards, compliance context, and supporting evidence.
          </p>

          <div className="hero-trust-bar">
            <div className="trust-item">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <span>Authoritative BIS Grounding</span>
            </div>
            <div className="trust-item">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <span>Statutory QCO Tracking</span>
            </div>
            <div className="trust-item">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <span>Multilingual (Hindi / English)</span>
            </div>
          </div>
        </div>

        {/* Right Column: UX4G Service Demonstration / Standards Match Example Panel */}
        <div className="hero-example-panel" aria-label="Service Demonstration Illustration">
          <div className="example-panel-header">
            <div className="example-header-left">
              <span className="example-tag">EXAMPLE WORKFLOW</span>
              <span className="example-title">Procurement Specification Matching</span>
            </div>
            <span className="example-badge">Demonstration</span>
          </div>

          <div className="example-panel-body">
            {/* Step 1: Procurement Requirement */}
            <div className="example-block">
              <div className="example-block-label">
                <span className="block-step-num">1</span>
                <span>PROCUREMENT REQUIREMENT</span>
              </div>
              <div className="example-clause-box">
                <p className="example-clause-text">
                  &ldquo;12 mm Fe 500 TMT reinforcement steel bars for RCC construction with mandatory ISI marking.&rdquo;
                </p>
                <div className="example-clause-meta">
                  <span>Source: Civil Works Tender Specification</span>
                </div>
              </div>
            </div>

            <div className="example-arrow-divider" aria-hidden="true">
              <div className="arrow-line"></div>
              <span className="arrow-label">Matched against official BIS catalogue</span>
              <div className="arrow-line"></div>
            </div>

            {/* Step 2: Matched Standards */}
            <div className="example-block">
              <div className="example-block-label">
                <span className="block-step-num">2</span>
                <span>APPLICABLE INDIAN STANDARDS</span>
              </div>

              <div className="example-results-list">
                <div className="example-result-item">
                  <div className="example-res-top">
                    <span className="example-std-num">IS 1786:2008</span>
                    <span className="example-status-active">Active</span>
                    <span className="example-qco-pill">Mandatory QCO</span>
                  </div>
                  <div className="example-res-title">
                    High strength deformed steel bars and wires for concrete reinforcement
                  </div>
                </div>

                <div className="example-result-item">
                  <div className="example-res-top">
                    <span className="example-std-num">IS 456:2000</span>
                    <span className="example-status-active">Active</span>
                    <span className="example-normative-pill">Design Code</span>
                  </div>
                  <div className="example-res-title">
                    Plain and reinforced concrete — Code of practice
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="example-panel-footer">
            <span className="example-note">
              * Illustrative service demonstration. Enter your specific requirement below to query live records.
            </span>
          </div>
        </div>
      </div>

      {/* Restrained Horizontal Standards Ecosystem Visual */}
      <div className="ecosystem-track-wrapper" aria-label="Indian Standards Ecosystem">
        <div className="ecosystem-track">
          {ECOSYSTEM_ITEMS.map((item, idx) => (
            <div key={idx} className="ecosystem-item" title={`${item.title} — ${item.desc}`}>
              <span className="ecosystem-item-badge">{item.badge}</span>
              <span className="ecosystem-item-title">{item.title}</span>
              <span className="ecosystem-item-desc">· {item.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
