import React from 'react';

export default function Footer() {
  return (
    <footer className="global-footer" role="contentinfo">
      <div className="footer-inner">
        <div className="footer-col-left">
          <div className="footer-brand">
            <span className="footer-brand-title">Standards-AI</span>
            <span className="footer-brand-sep">·</span>
            <span className="footer-brand-desc">AI-powered discovery of applicable Indian Standards</span>
          </div>
          <p className="footer-copyright">
            Prototype Evaluation · Grounded in official Bureau of Indian Standards (BIS) records & Gazette QCOs
          </p>
        </div>

        <div className="footer-col-right">
          <span className="footer-tag">Smart India Hackathon 2026</span>
          <a
            href="https://standards.bis.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
            title="Open official BIS Standards Portal in new tab"
          >
            <span>standards.bis.gov.in ↗</span>
          </a>
        </div>
      </div>
    </footer>
  );
}
