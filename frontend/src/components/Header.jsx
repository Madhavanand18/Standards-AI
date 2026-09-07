import React from 'react';

export default function Header({ systemHealth }) {
  return (
    <header className="header">
      <div className="header-badge">
        <span className="status-dot"></span>
        <span>SIH26108 · BIS Recommendation Engine MVP</span>
      </div>
      <h1 className="header-title">Indian Standards Retrieval</h1>
      <p className="header-subtitle">
        Intelligent semantic matching of public procurement specifications against
        authoritative Bureau of Indian Standards (BIS) specifications.
      </p>
      {systemHealth && (
        <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: '#64748b' }}>
          <span>Database: {systemHealth.standards_in_db} standards</span>
          <span style={{ margin: '0 0.5rem' }}>·</span>
          <span>Vectors: {systemHealth.points_indexed} indexed</span>
          <span style={{ margin: '0 0.5rem' }}>·</span>
          <span>Engine: Local 384-d Multilingual</span>
        </div>
      )}
    </header>
  );
}
