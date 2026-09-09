import React from 'react';

const ECOSYSTEM_ITEMS = [
  {
    badge: 'BIS',
    title: 'Bureau of Indian Standards',
    desc: 'National Standards Body of India',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10"></circle>
        <polygon points="12 6 15 14 9 14"></polygon>
      </svg>
    ),
  },
  {
    badge: 'IS',
    title: 'Indian Standards',
    desc: 'Authoritative Technical Specifications',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
      </svg>
    ),
  },
  {
    badge: 'ISI Mark',
    title: 'Product Certification Scheme',
    desc: 'Conformity & Quality Certification',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
      </svg>
    ),
  },
  {
    badge: 'Hallmark',
    title: 'Precious Metals Certification',
    desc: 'Purity & Assay Verification',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
      </svg>
    ),
  },
  {
    badge: 'QCO',
    title: 'Quality Control Orders',
    desc: 'Government Compulsory Orders',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        <polyline points="9 12 11 14 15 10"></polyline>
      </svg>
    ),
  },
  {
    badge: 'NBC',
    title: 'National Building Code',
    desc: 'Infrastructure & Safety Guidelines',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="3" y1="9" x2="21" y2="9"></line>
        <line x1="9" y1="21" x2="9" y2="9"></line>
      </svg>
    ),
  },
];

export default function HeroSection() {
  return (
    <section className="hero-section" aria-labelledby="hero-main-title">
      <div className="hero-kicker">
        <span>Public Procurement Technical Intelligence</span>
      </div>

      <h1 id="hero-main-title" className="hero-title">
        Indian Standards Recommendation Engine
      </h1>

      <p className="hero-subtitle">
        Identify applicable Indian Standards from procurement specifications using semantic search
        and verified Bureau of Indian Standards (BIS) information.
      </p>

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
