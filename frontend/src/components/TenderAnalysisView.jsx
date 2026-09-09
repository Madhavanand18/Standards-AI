import React, { useState } from 'react';
import ResultCard from './ResultCard';

/**
 * TenderAnalysisView — Run 6 UI
 *
 * Displays the full tender intelligence result:
 *   - Extraction summary (status, count, warnings)
 *   - Per-requirement cards with:
 *       - Source page badge, category, confidence
 *       - Original text (verbatim, expandable)
 *       - Normalized search query used
 *       - Technical parameters table
 *       - Explicit IS references (tagged "In Tender")
 *       - BIS recommendations from the existing engine (via ResultCard)
 *
 * Keeps the "Explicitly referenced in tender" vs "Semantically recommended" distinction clear.
 */

const CATEGORY_COLORS = {
  MATERIAL:       { bg: '#1e3a5f', border: '#3b82f6', text: '#93c5fd' },
  DIMENSIONAL:    { bg: '#1e3a2f', border: '#22c55e', text: '#86efac' },
  GRADE:          { bg: '#3b1f5f', border: '#a855f7', text: '#d8b4fe' },
  PERFORMANCE:    { bg: '#3b2a00', border: '#f59e0b', text: '#fcd34d' },
  ELECTRICAL:     { bg: '#1a2e50', border: '#60a5fa', text: '#bfdbfe' },
  MECHANICAL:     { bg: '#2d1a1a', border: '#f87171', text: '#fca5a5' },
  CHEMICAL:       { bg: '#1a2d1a', border: '#4ade80', text: '#bbf7d0' },
  SAFETY:         { bg: '#3b1a00', border: '#fb923c', text: '#fed7aa' },
  TESTING:        { bg: '#1a1a3b', border: '#818cf8', text: '#c7d2fe' },
  INSPECTION:     { bg: '#2a1a3b', border: '#c084fc', text: '#e9d5ff' },
  QUALITY:        { bg: '#001f3b', border: '#38bdf8', text: '#bae6fd' },
  INSTALLATION:   { bg: '#1f2a1a', border: '#86efac', text: '#dcfce7' },
  PACKING_MARKING:{ bg: '#2a1f00', border: '#d4a017', text: '#fef08a' },
  ENVIRONMENTAL:  { bg: '#0f2a0f', border: '#4ade80', text: '#bbf7d0' },
  OTHER:          { bg: '#1a1a2e', border: '#6b7280', text: '#9ca3af' },
};

function ConfidencePill({ confidence }) {
  const pct = Math.round(confidence * 100);
  const color = pct >= 80 ? '#22c55e' : pct >= 55 ? '#f59e0b' : '#ef4444';
  return (
    <span style={{
      fontSize: '0.7rem', fontWeight: 600, padding: '2px 8px',
      borderRadius: '99px', border: `1px solid ${color}`, color,
      background: `${color}18`, letterSpacing: '0.02em',
    }}>
      {pct}% confidence
    </span>
  );
}

function RequirementCard({ reqRec, index: _index }) {
  const [showOriginal, setShowOriginal] = useState(false);
  const [showRecs, setShowRecs] = useState(true);

  const req = reqRec.requirement;
  const recs = reqRec.recommendations || [];
  const catStyle = CATEGORY_COLORS[req.category] || CATEGORY_COLORS.OTHER;
  const hasExplicitRefs = req.explicitly_referenced_standards?.length > 0;
  const hasParams = req.technical_parameters?.length > 0;
  const hasRecs = recs.length > 0;

  return (
    <div style={{
      background: 'rgba(15,23,42,0.85)',
      border: '1px solid rgba(71,85,105,0.5)',
      borderRadius: '14px',
      marginBottom: '1.5rem',
      overflow: 'hidden',
    }}>
      {/* ── Header ── */}
      <div style={{
        padding: '1rem 1.25rem 0.75rem',
        borderBottom: '1px solid rgba(71,85,105,0.3)',
        background: 'rgba(15,23,42,0.95)',
      }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center', marginBottom: '0.5rem' }}>
          {/* Requirement number */}
          <span style={{
            fontSize: '0.7rem', fontWeight: 700, color: '#64748b',
            background: 'rgba(100,116,139,0.1)', border: '1px solid rgba(100,116,139,0.3)',
            borderRadius: '6px', padding: '2px 8px', fontFamily: 'monospace',
          }}>
            {req.requirement_id}
          </span>

          {/* Category badge */}
          <span style={{
            fontSize: '0.7rem', fontWeight: 600, letterSpacing: '0.05em',
            textTransform: 'uppercase', padding: '2px 8px', borderRadius: '6px',
            background: catStyle.bg, border: `1px solid ${catStyle.border}`, color: catStyle.text,
          }}>
            {req.category}
          </span>

          {/* Source page badge */}
          {req.source_pages?.length > 0 && (
            <span style={{
              fontSize: '0.7rem', fontWeight: 600, color: '#38bdf8',
              background: 'rgba(56,189,248,0.1)', border: '1px solid rgba(56,189,248,0.3)',
              borderRadius: '6px', padding: '2px 8px',
            }}>
              📄 Page {req.source_pages.join(', ')}
            </span>
          )}

          {/* Mandatory language */}
          {req.mandatory_language && (
            <span style={{
              fontSize: '0.7rem', fontWeight: 600, color: '#fbbf24',
              background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.3)',
              borderRadius: '6px', padding: '2px 8px',
            }}>
              MANDATORY
            </span>
          )}

          {/* Confidence */}
          <ConfidencePill confidence={req.extraction_confidence} />
        </div>

        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: '#f1f5f9' }}>
          {req.title}
        </h3>

        {req.source_section && (
          <p style={{ margin: '0.3rem 0 0', fontSize: '0.75rem', color: '#64748b' }}>
            Section: {req.source_section}
          </p>
        )}
      </div>

      <div style={{ padding: '1rem 1.25rem' }}>
        {/* ── Normalized text (BIS query) ── */}
        <div style={{ marginBottom: '0.9rem' }}>
          <span style={{ fontSize: '0.7rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Search Query Sent to BIS Engine
          </span>
          <p style={{
            margin: '0.25rem 0 0', fontSize: '0.875rem', color: '#94a3b8',
            fontStyle: 'italic', lineHeight: 1.5,
          }}>
            {req.normalized_text}
          </p>
        </div>

        {/* ── Explicit IS references ── */}
        {hasExplicitRefs && (
          <div style={{ marginBottom: '0.9rem' }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Explicitly Referenced in Tender
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.3rem' }}>
              {req.explicitly_referenced_standards.map((ref, i) => (
                <span key={i} style={{
                  fontSize: '0.78rem', fontWeight: 700, color: '#fbbf24',
                  background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.4)',
                  borderRadius: '6px', padding: '3px 10px',
                }}>
                  📋 {ref} <span style={{ fontWeight: 400, color: '#9ca3af', fontSize: '0.68rem' }}>— stated in tender</span>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ── Technical parameters ── */}
        {hasParams && (
          <div style={{ marginBottom: '0.9rem' }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Extracted Technical Parameters
            </span>
            <div style={{
              display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.35rem',
            }}>
              {req.technical_parameters.map((p, i) => (
                <span key={i} style={{
                  fontSize: '0.78rem', color: '#e2e8f0',
                  background: 'rgba(51,65,85,0.7)', border: '1px solid rgba(71,85,105,0.5)',
                  borderRadius: '6px', padding: '3px 10px',
                }}>
                  <span style={{ color: '#94a3b8', fontWeight: 600 }}>{p.name}: </span>
                  <span style={{ fontWeight: 700 }}>{p.value}</span>
                  {p.unit && <span style={{ color: '#64748b' }}> {p.unit}</span>}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ── Original text (collapsible) ── */}
        <div style={{ marginBottom: '0.9rem' }}>
          <button
            type="button"
            onClick={() => setShowOriginal(v => !v)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
              fontSize: '0.7rem', fontWeight: 600, color: '#64748b',
              textTransform: 'uppercase', letterSpacing: '0.05em',
              display: 'flex', alignItems: 'center', gap: '0.3rem',
            }}
          >
            <span>{showOriginal ? '▼' : '▶'}</span>
            Original Source Text (verbatim from tender)
          </button>
          {showOriginal && (
            <pre style={{
              marginTop: '0.4rem', padding: '0.75rem 1rem',
              background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(71,85,105,0.3)',
              borderRadius: '8px', fontSize: '0.8rem', color: '#cbd5e1',
              whiteSpace: 'pre-wrap', lineHeight: 1.6, fontFamily: 'monospace',
              maxHeight: '180px', overflowY: 'auto',
            }}>
              {req.original_text}
            </pre>
          )}
        </div>

        {/* ── Recommendation warnings ── */}
        {reqRec.recommendation_warnings?.length > 0 && (
          <div style={{
            padding: '0.5rem 0.75rem', background: 'rgba(251,191,36,0.08)',
            border: '1px solid rgba(251,191,36,0.25)', borderRadius: '8px',
            marginBottom: '0.9rem', fontSize: '0.78rem', color: '#fbbf24',
          }}>
            {reqRec.recommendation_warnings.map((w, i) => <div key={i}>⚠ {w}</div>)}
          </div>
        )}

        {/* ── BIS Recommendations ── */}
        <div>
          <button
            type="button"
            onClick={() => setShowRecs(v => !v)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
              display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem',
            }}
          >
            <span style={{
              fontSize: '0.7rem', fontWeight: 600, color: '#64748b',
              textTransform: 'uppercase', letterSpacing: '0.05em',
            }}>
              {showRecs ? '▼' : '▶'} BIS Standard Recommendations
            </span>
            <span style={{
              fontSize: '0.7rem', fontWeight: 700, padding: '1px 8px', borderRadius: '99px',
              background: hasRecs ? 'rgba(34,197,94,0.15)' : 'rgba(100,116,139,0.15)',
              border: `1px solid ${hasRecs ? 'rgba(34,197,94,0.4)' : 'rgba(100,116,139,0.3)'}`,
              color: hasRecs ? '#4ade80' : '#9ca3af',
            }}>
              {recs.length} standard{recs.length !== 1 ? 's' : ''}
            </span>
            <span style={{ fontSize: '0.65rem', color: '#475569', fontStyle: 'italic' }}>
              (semantically recommended by BIS engine)
            </span>
          </button>

          {showRecs && (
            hasRecs ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {recs.map((std, i) => (
                  <ResultCard key={std.standard_number || i} standard={std} rank={i + 1} />
                ))}
              </div>
            ) : (
              <div style={{
                padding: '0.75rem 1rem',
                background: 'rgba(71,85,105,0.1)', border: '1px solid rgba(71,85,105,0.2)',
                borderRadius: '8px', fontSize: '0.82rem', color: '#64748b',
              }}>
                No BIS standards met the relevance threshold for this requirement.
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default function TenderAnalysisView({ analysisResult }) {
  if (!analysisResult) return null;

  const {
    filename,
    extraction_status,
    extraction_warnings = [],
    analysis_warnings = [],
    requirement_count,
    requirements = [],
    anti_hallucination_note,
  } = analysisResult;

  const allWarnings = [...new Set([...extraction_warnings, ...analysis_warnings])];
  const isFailed = extraction_status === 'FAILED';
  const isNoReqs = extraction_status === 'NO_REQUIREMENTS';

  return (
    <div id="tender-analysis-view" style={{ marginTop: '1.5rem' }}>
      {/* ── Analysis Header ── */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,70,0.95) 100%)',
        border: '1px solid rgba(99,102,241,0.35)',
        borderRadius: '14px',
        padding: '1.25rem 1.5rem',
        marginBottom: '1.25rem',
      }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#f1f5f9' }}>
            Tender Intelligence Result
          </h2>
          <span style={{
            fontSize: '0.7rem', fontWeight: 700,
            padding: '3px 10px', borderRadius: '99px',
            background: isFailed ? 'rgba(239,68,68,0.15)' : isNoReqs ? 'rgba(251,191,36,0.15)' : 'rgba(34,197,94,0.15)',
            border: `1px solid ${isFailed ? 'rgba(239,68,68,0.4)' : isNoReqs ? 'rgba(251,191,36,0.4)' : 'rgba(34,197,94,0.4)'}`,
            color: isFailed ? '#f87171' : isNoReqs ? '#fbbf24' : '#4ade80',
            letterSpacing: '0.05em',
          }}>
            {extraction_status}
          </span>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.82rem', color: '#94a3b8' }}>
          <span>
            <strong style={{ color: '#e2e8f0' }}>{filename}</strong>
          </span>
          {!isFailed && !isNoReqs && (
            <span>
              <strong style={{ color: '#818cf8' }}>{requirement_count}</strong> technical requirement{requirement_count !== 1 ? 's' : ''} identified
            </span>
          )}
        </div>
      </div>

      {/* ── Warnings ── */}
      {allWarnings.length > 0 && (
        <div style={{
          background: 'rgba(251,191,36,0.07)', border: '1px solid rgba(251,191,36,0.25)',
          borderRadius: '10px', padding: '0.75rem 1rem', marginBottom: '1.25rem',
          fontSize: '0.8rem', color: '#fcd34d',
        }}>
          <strong>⚠ Extraction Warnings:</strong>
          <ul style={{ margin: '0.35rem 0 0', paddingLeft: '1.2rem' }}>
            {allWarnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}

      {/* ── Failure / No Requirements state ── */}
      {(isFailed || isNoReqs) && (
        <div style={{
          background: 'rgba(15,23,42,0.85)', border: '1px solid rgba(71,85,105,0.3)',
          borderRadius: '12px', padding: '2rem', textAlign: 'center',
          color: '#64748b', marginBottom: '1rem',
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>
            {isFailed ? '❌' : '📋'}
          </div>
          <p style={{ margin: 0, fontSize: '0.9rem' }}>
            {isFailed
              ? 'Requirement extraction failed. Check the warnings above for details.'
              : 'No technical procurement requirements were identified in this document. Only technical/specification content is extracted.'}
          </p>
        </div>
      )}

      {/* ── Requirement → Standard traceability ── */}
      {requirements.length > 0 && (
        <div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.75rem',
            marginBottom: '1rem', fontSize: '0.8rem', color: '#64748b',
          }}>
            <span style={{ color: '#94a3b8', fontWeight: 600 }}>Traceability:</span>
            <span>PDF Page</span>
            <span>→</span>
            <span>Technical Requirement</span>
            <span>→</span>
            <span>BIS Standard Recommendations</span>
            <span>→</span>
            <span>Lifecycle / Compliance</span>
          </div>

          {requirements.map((reqRec, i) => (
            <RequirementCard key={reqRec.requirement.requirement_id || i} reqRec={reqRec} index={i} />
          ))}
        </div>
      )}

      {/* ── Anti-hallucination notice ── */}
      {anti_hallucination_note && (
        <div style={{
          background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(71,85,105,0.2)',
          borderRadius: '10px', padding: '0.75rem 1rem', marginTop: '0.75rem',
          fontSize: '0.72rem', color: '#475569', lineHeight: 1.5,
        }}>
          <strong style={{ color: '#64748b' }}>🔒 Anti-Hallucination Notice: </strong>
          {anti_hallucination_note}
        </div>
      )}
    </div>
  );
}
