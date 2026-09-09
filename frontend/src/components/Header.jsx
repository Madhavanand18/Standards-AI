import React, { useState, useRef } from 'react';
import AccountMenu from './AccountMenu';

export default function Header({
  activeTab,
  setActiveTab,
  systemHealth,
  onOpenSettings,
  onOpenAbout,
}) {
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const accountBtnRef = useRef(null);

  const toggleAccountMenu = () => {
    setAccountMenuOpen((prev) => !prev);
  };

  return (
    <header className="global-header" role="banner">
      <div className="header-inner">
        {/* Left: Product Identity */}
        <button
          type="button"
          className="header-brand"
          onClick={() => setActiveTab('home')}
          title="Go to Standards-AI Home"
        >
          <div className="brand-emblem" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              <line x1="9" y1="7" x2="15" y2="7"></line>
              <line x1="9" y1="11" x2="13" y2="11"></line>
            </svg>
          </div>
          <div className="brand-info">
            <span className="brand-title">Standards-AI</span>
            <span className="brand-tagline">Indian Standards Recommendation Engine</span>
          </div>
        </button>

        {/* Center: Navigation */}
        <nav className="header-nav" role="navigation" aria-label="Main Navigation">
          <button
            type="button"
            className={`nav-link ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
            aria-current={activeTab === 'home' ? 'page' : undefined}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <span>Home</span>
          </button>

          <button
            type="button"
            className={`nav-link ${activeTab === 'pdf-analyzer' ? 'active' : ''}`}
            onClick={() => setActiveTab('pdf-analyzer')}
            aria-current={activeTab === 'pdf-analyzer' ? 'page' : undefined}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
            </svg>
            <span>PDF Analyzer</span>
          </button>

          <button
            type="button"
            className={`nav-link ${activeTab === 'future' ? 'active' : ''}`}
            onClick={() => setActiveTab('future')}
            aria-current={activeTab === 'future' ? 'page' : undefined}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            <span>Future / Roadmap</span>
            <span className="nav-badge">Roadmap</span>
          </button>
        </nav>

        {/* Right: Minimal Status & Interactive Account Control */}
        <div className="header-right">
          <div
            className="header-status-indicator"
            title={systemHealth ? `System Online · ${systemHealth.standards_in_db || 10} verified standards indexed in registry` : 'System Online · Grounded BIS Engine'}
          >
            <span className="status-dot-green" aria-hidden="true"></span>
            <span>Online</span>
          </div>

          <div className="account-container" style={{ position: 'relative' }}>
            <button
              ref={accountBtnRef}
              type="button"
              className={`account-avatar-btn ${accountMenuOpen ? 'active' : ''}`}
              onClick={toggleAccountMenu}
              aria-expanded={accountMenuOpen}
              aria-haspopup="menu"
              aria-label="Open User Account Menu"
              title="User Account & Settings"
            >
              <span>U</span>
            </button>

            <AccountMenu
              isOpen={accountMenuOpen}
              onClose={() => setAccountMenuOpen(false)}
              onOpenSettings={onOpenSettings}
              onOpenAbout={onOpenAbout}
              anchorRef={accountBtnRef}
            />
          </div>
        </div>
      </div>
    </header>
  );
}
