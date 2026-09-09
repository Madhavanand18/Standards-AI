import React, { useEffect, useRef } from 'react';

export default function AccountMenu({
  isOpen,
  onClose,
  onOpenSettings,
  onOpenAbout,
  anchorRef,
}) {
  const menuRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(e.target) &&
        anchorRef?.current &&
        !anchorRef.current.contains(e.target)
      ) {
        onClose();
      }
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
        anchorRef?.current?.focus();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose, anchorRef]);

  if (!isOpen) return null;

  return (
    <div
      ref={menuRef}
      className="account-popover"
      role="menu"
      aria-label="User Account Menu"
    >
      {/* User Header */}
      <div className="account-popover-header">
        <div className="account-avatar-large" aria-hidden="true">
          <span>U</span>
        </div>
        <div className="account-user-meta">
          <div className="account-user-name">Procurement User</div>
          <div className="account-session-badge">Local Prototype</div>
        </div>
      </div>

      {/* Account Info Box */}
      <div className="account-info-box">
        <div className="account-status-row">
          <span className="account-status-dot" aria-hidden="true"></span>
          <span className="account-status-text">Evaluation Session Active</span>
        </div>
        <p className="account-note">
          Full search, PDF extraction, and compliance verification features are enabled without requiring sign-in.
        </p>
      </div>

      {/* Menu Actions */}
      <div className="account-actions-list">
        <button
          type="button"
          className="account-menu-item"
          role="menuitem"
          onClick={() => {
            onClose();
            onOpenSettings();
          }}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          <span>Application Settings</span>
        </button>

        <button
          type="button"
          className="account-menu-item"
          role="menuitem"
          onClick={() => {
            onClose();
            onOpenAbout();
          }}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span>About Standards-AI</span>
        </button>

        <a
          href="https://standards.bis.gov.in"
          target="_blank"
          rel="noopener noreferrer"
          className="account-menu-item"
          role="menuitem"
          onClick={onClose}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
          <span>Official BIS Portal ↗</span>
        </a>

        <div
          className="account-menu-item item-disabled"
          role="menuitem"
          aria-disabled="true"
          title="Single Sign-On is not required for this prototype and will be available in future releases."
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <div className="disabled-item-text">
            <span>Sign In</span>
            <span className="badge-coming-soon">Coming Soon</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="account-popover-footer">
        <button
          type="button"
          className="account-close-link"
          onClick={onClose}
        >
          Close Menu
        </button>
      </div>
    </div>
  );
}
