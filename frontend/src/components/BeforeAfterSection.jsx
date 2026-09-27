import React, { useState } from 'react';

const BEFORE_STEPS = [
  {
    step: '01',
    title: 'Read procurement requirement',
    channel: 'Tender notices, NITs, BOQ schedules, paper files',
    description: 'Procurement officers and technical staff read through lengthy tender schedules, indents, or bills of quantities to identify required goods or works.',
    challenge: 'Requirements are often written using trade jargon, colloquial names, or informal descriptions buried across unstructured clauses.',
    example: 'Officer reviews tender indent for "Supply of 25 kVA outdoor oil-immersed distribution transformers".',
  },
  {
    step: '02',
    title: 'Identify technical specifications',
    channel: 'Engineering drawings, requisition indents, manual checklists',
    description: 'Technical evaluators manually extract critical operating parameters, material grades, duty ratings, and testing requirements.',
    challenge: 'High risk of overlooking sub-clauses, electrical ratings (voltage ratios, losses), or specific environmental tolerances.',
    example: 'Officer extracts: 25 kVA, 11 kV/433 V, copper winding, energy efficiency level 2, outdoor mounting.',
  },
  {
    step: '03',
    title: 'Search standards sources manually',
    channel: 'Multiple website search forms, BIS portal, general web search, legacy files',
    description: 'Officers search across disparate portals, departmental library copies, or general web engines to find applicable standard numbers.',
    challenge: 'Strict dependency on exact standard keywords; queries fail when formal BIS standard titles differ from commercial trade terminology.',
    example: 'Searching "distribution transformer" yields hundreds of general results without clear applicability distinctions.',
  },
  {
    step: '04',
    title: 'Check applicability',
    channel: 'Standard scope clauses, candidate standard PDFs, handbook indices',
    description: 'Evaluator reads through scope and definitions of candidate Indian Standards to determine whether the standard matches the exact product scope.',
    challenge: 'Time-consuming manual reading through overlapping standard scopes (e.g., power transformers vs. distribution transformers).',
    example: 'Officer compares IS 2026 (power transformers) vs IS 1180 (distribution transformers) to confirm correct applicability.',
  },
  {
    step: '05',
    title: 'Check versions and amendments',
    channel: 'BIS gazette notifications, monthly bulletins, amendment sheets',
    description: 'Officer manually verifies whether the candidate standard edition is active, reaffirmed, superseded, or withdrawn, and looks for published amendments.',
    challenge: 'Superseded editions or unnoted amendments are frequently referenced, creating audit objections or legal procurement disputes.',
    example: 'Verifying if IS 1180 (Part 1):1989 is superseded by IS 1180 (Part 1):2014, and checking Amendments 1 through 4.',
  },
  {
    step: '06',
    title: 'Verify compliance/QCO information',
    channel: 'Ministry gazette notifications (DPIIT, Ministry of Power, etc.), departmental circulars',
    description: 'Evaluator searches through separate Ministry notifications to check if mandatory Quality Control Orders (QCO) require compulsory ISI certification.',
    challenge: 'Statutory orders are scattered across multiple ministry portals with varying implementation dates and exemption provisions.',
    example: 'Locating Central Government QCO gazette notifying distribution transformers under compulsory BIS certification.',
  },
  {
    step: '07',
    title: 'Compare and validate results',
    channel: 'Ad-hoc spreadsheets, evaluation committee notes, manual justification memos',
    description: 'Officer cross-checks specifications against bid offerings, writes compliance justification notes, and compiles documentation for committee approval.',
    challenge: 'Dispersed, manual audit trail without standardized citations, leading to lengthy committee review cycles.',
    example: 'Officer compiles tender documentation referencing IS 1180 Part 1 with manual notes on QCO compliance.',
  },
];

const AFTER_STEPS = [
  {
    step: '01',
    title: 'Enter procurement requirement',
    channel: 'Single unified search bar or PDF tender document upload',
    description: 'Officer enters technical requirements as natural language, colloquial descriptions, or uploads tender NIT / BOQ schedules directly.',
    advantage: 'Accepts English, Hindi, and romanized Hinglish; handles free-form text or extracted document clauses without pre-formatting.',
    example: 'Officer enters "25 kVA 11kV outdoor copper wound distribution transformer" or uploads tender schedule PDF.',
  },
  {
    step: '02',
    title: 'Understand/extract the specification',
    channel: 'Domain-specific semantic parser and technical clause analyzer',
    description: 'The engine parses engineering parameters, material grades, duty ratings, and contextual technical constraints automatically.',
    advantage: 'Preserves critical numbers, voltage ratios, and grade designations while filtering out administrative tender boilerplate.',
    example: 'Parser recognizes equipment type (distribution transformer), rating (25 kVA), and voltage class (11 kV / 433 V).',
  },
  {
    step: '03',
    title: 'Find applicable Indian Standards',
    channel: 'Dense multilingual semantic retrieval grounded in BIS records',
    description: 'Retrieves relevant Indian Standards from the official Bureau of Indian Standards catalogue based on verified scope coverage and semantic relevance.',
    advantage: 'Discovers authoritative standards even when procurement descriptions use informal terms differing from official BIS titles.',
    example: 'Surfaces IS 1180 (Part 1):2014 "Outdoor Type Oil Immersed Distribution Transformers Up to and Including 2500 kVA".',
  },
  {
    step: '04',
    title: 'Review applicability and lifecycle information',
    channel: 'Integrated BIS lifecycle registry & amendment tracking',
    description: 'Instantly view active edition year, reaffirmation status, published amendments, and proactive alerts against superseded editions.',
    advantage: 'Eliminates the risk of referencing obsolete standards by providing real-time lifecycle status flags and amendment notices.',
    example: 'Displays status as "Active (Reaffirmed 2021)", edition year 2014, and details Amendments 1, 2, 3, and 4.',
  },
  {
    step: '05',
    title: 'Review compliance/QCO evidence',
    channel: 'Official Quality Control Order (QCO) regulatory linkage',
    description: 'Surfaces statutory Quality Control Orders issued by responsible Ministries, identifying mandatory ISI marking requirements.',
    advantage: 'Direct statutory citations provide immediate legal clarity on compulsory certification before tender finalization.',
    example: 'Highlights Ministry Quality Control Order mandating compulsory ISI certification for transformers up to 2500 kVA.',
  },
  {
    step: '06',
    title: 'Make an informed procurement decision',
    channel: 'Consolidated verification record with direct BIS portal link',
    description: 'Officer reviews verified standard scope, lifecycle status, and statutory compliance evidence with direct verification links to the official BIS portal.',
    advantage: 'Produces an authoritative, audit-ready verification trail suitable for Technical Evaluation Committee records.',
    example: 'Officer references IS 1180 (Part 1):2014 with verified QCO compliance backing in tender NIT specifications.',
  },
];

const COMPARISON_DIMENSIONS = [
  {
    dimension: 'Discovery Approach',
    before: 'Keyword & exact-title search across multiple websites and legacy records; fails on terminology variations.',
    after: 'Multilingual semantic retrieval matching engineering intent across official BIS catalogue scopes.',
  },
  {
    dimension: 'Document Analysis',
    before: 'Manual reading of multi-page tender PDFs, NITs, and BOQs to locate and transcribe technical clauses.',
    after: 'Direct PDF upload and automatic clause extraction preserving ratings, grades, and dimensions.',
  },
  {
    dimension: 'Lifecycle & Revisions',
    before: 'Separate manual cross-checks against gazette notices; high risk of specifying superseded standards.',
    after: 'Integrated lifecycle status (Active / Superseded / Reaffirmed) with published amendment notices.',
  },
  {
    dimension: 'Statutory Compliance (QCO)',
    before: 'Manual tracking of scattered Ministry gazette orders to check if mandatory ISI certification applies.',
    after: 'Direct linkage to statutory Quality Control Orders (QCO) and mandatory licensing mandates.',
  },
  {
    dimension: 'Audit Trail & Verification',
    before: 'Fragmented spreadsheets, handwritten notes, and unverified web bookmarks.',
    after: 'Authoritative citations with direct links to the official BIS portal (standards.bis.gov.in).',
  },
];

export default function BeforeAfterSection() {
  const [viewMode, setViewMode] = useState('side-by-side'); // 'side-by-side' | 'before' | 'after'
  const [showExamples, setShowExamples] = useState(false);
  const [selectedBeforeStep, setSelectedBeforeStep] = useState(null);
  const [selectedAfterStep, setSelectedAfterStep] = useState(null);
  const [activeTab, setActiveTab] = useState('flow'); // 'flow' | 'matrix'

  const toggleBeforeStep = (idx) => {
    setSelectedBeforeStep((prev) => (prev === idx ? null : idx));
  };

  const toggleAfterStep = (idx) => {
    setSelectedAfterStep((prev) => (prev === idx ? null : idx));
  };

  return (
    <section className="section-panel before-after-panel" aria-labelledby="workflow-comparison-heading">
      {/* ── Section Header ── */}
      <div className="panel-header-row">
        <div>
          <span className="panel-eyebrow">WORKFLOW TRANSFORMATION</span>
          <h2 id="workflow-comparison-heading" className="panel-heading">
            From Manual Search to Standards Intelligence
          </h2>
        </div>
        <span className="panel-caption">
          How Standards-AI streamlines procurement discovery and statutory compliance
        </span>
      </div>

      {/* ── Subtitle / Intro Description ── */}
      <div className="ba-intro-bar">
        <p className="ba-intro-text">
          Public procurement requires technical officers to identify applicable Indian Standards, confirm active editions, and verify statutory Quality Control Orders (QCO). Compare the traditional multi-source manual process against the unified Standards-AI discovery workflow.
        </p>
      </div>

      {/* ── Interactive Toolbar ── */}
      <div className="ba-toolbar" role="toolbar" aria-label="Workflow view controls">
        <div className="ba-segmented-control" role="tablist" aria-label="Comparison View Mode">
          <button
            type="button"
            role="tab"
            aria-selected={viewMode === 'side-by-side'}
            className={`ba-control-btn ${viewMode === 'side-by-side' ? 'active' : ''}`}
            onClick={() => setViewMode('side-by-side')}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="3" width="8" height="18" rx="1"></rect>
              <rect x="13" y="3" width="8" height="18" rx="1"></rect>
            </svg>
            <span>Side-by-Side</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={viewMode === 'before'}
            className={`ba-control-btn ${viewMode === 'before' ? 'active' : ''}`}
            onClick={() => setViewMode('before')}
          >
            <span className="ba-dot ba-dot-neutral" aria-hidden="true"></span>
            <span>Traditional Manual (Before)</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={viewMode === 'after'}
            className={`ba-control-btn ${viewMode === 'after' ? 'active' : ''}`}
            onClick={() => setViewMode('after')}
          >
            <span className="ba-dot ba-dot-primary" aria-hidden="true"></span>
            <span>With Standards-AI (After)</span>
          </button>
        </div>

        <div className="ba-view-subnav">
          <button
            type="button"
            className={`ba-toggle-pill ${showExamples ? 'active' : ''}`}
            onClick={() => setShowExamples((v) => !v)}
            aria-pressed={showExamples}
            title="Toggle illustrative procurement example across all steps"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>{showExamples ? 'Hide Examples' : 'Show Illustrative Example'}</span>
          </button>

          <div className="ba-tab-divider" aria-hidden="true"></div>

          <div className="ba-mini-tabs" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'flow'}
              className={`ba-mini-tab ${activeTab === 'flow' ? 'active' : ''}`}
              onClick={() => setActiveTab('flow')}
            >
              Step Workflow
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'matrix'}
              className={`ba-mini-tab ${activeTab === 'matrix' ? 'active' : ''}`}
              onClick={() => setActiveTab('matrix')}
            >
              Key Differences
            </button>
          </div>
        </div>
      </div>

      {/* ── TAB CONTENT 1: WORKFLOW STEPS ── */}
      {activeTab === 'flow' && (
        <div className="ba-comparison-wrapper">
          {/* ── BEFORE COLUMN ── */}
          {(viewMode === 'side-by-side' || viewMode === 'before') && (
            <div className={`ba-column ba-column-before ${viewMode === 'before' ? 'ba-column-full' : ''}`}>
              <div className="ba-column-header">
                <div className="ba-col-title-group">
                  <span className="ba-pill ba-pill-neutral">TRADITIONAL PROCESS</span>
                  <h3 className="ba-col-heading">Manual Procurement Discovery</h3>
                </div>
                <div className="ba-col-meta">
                  <span className="ba-step-count-badge">7 Sequential Steps</span>
                </div>
              </div>

              <div className="ba-steps-container" role="list">
                {BEFORE_STEPS.map((item, idx) => {
                  const isExpanded = selectedBeforeStep === idx;
                  return (
                    <div
                      key={item.step}
                      role="listitem"
                      className={`ba-step-card ba-step-card-before ${isExpanded ? 'is-expanded' : ''}`}
                      onClick={() => toggleBeforeStep(idx)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          toggleBeforeStep(idx);
                        }
                      }}
                      tabIndex={0}
                      aria-expanded={isExpanded}
                    >
                      <div className="ba-step-top">
                        <span className="ba-step-number ba-num-neutral">{item.step}</span>
                        <div className="ba-step-title-wrap">
                          <h4 className="ba-step-title">{item.title}</h4>
                          <span className="ba-step-channel">{item.channel}</span>
                        </div>
                        <span className="ba-expand-icon" aria-hidden="true">
                          {isExpanded ? '−' : '+'}
                        </span>
                      </div>

                      <p className="ba-step-desc">{item.description}</p>

                      {/* Highlighted Friction / Challenge */}
                      <div className="ba-challenge-box">
                        <span className="ba-challenge-label">Manual Friction:</span>
                        <span className="ba-challenge-text">{item.challenge}</span>
                      </div>

                      {/* Illustrative Example (Collapsible / Toggleable) */}
                      {(showExamples || isExpanded) && (
                        <div className="ba-example-box" role="note">
                          <span className="ba-example-tag">Example:</span>
                          <span className="ba-example-text">{item.example}</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── AFTER COLUMN ── */}
          {(viewMode === 'side-by-side' || viewMode === 'after') && (
            <div className={`ba-column ba-column-after ${viewMode === 'after' ? 'ba-column-full' : ''}`}>
              <div className="ba-column-header ba-header-after">
                <div className="ba-col-title-group">
                  <span className="ba-pill ba-pill-primary">WITH STANDARDS-AI</span>
                  <h3 className="ba-col-heading">Assisted Standards Intelligence</h3>
                </div>
                <div className="ba-col-meta">
                  <span className="ba-step-count-badge ba-badge-primary">6 Streamlined Steps</span>
                </div>
              </div>

              <div className="ba-steps-container" role="list">
                {AFTER_STEPS.map((item, idx) => {
                  const isExpanded = selectedAfterStep === idx;
                  return (
                    <div
                      key={item.step}
                      role="listitem"
                      className={`ba-step-card ba-step-card-after ${isExpanded ? 'is-expanded' : ''}`}
                      onClick={() => toggleAfterStep(idx)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          toggleAfterStep(idx);
                        }
                      }}
                      tabIndex={0}
                      aria-expanded={isExpanded}
                    >
                      <div className="ba-step-top">
                        <span className="ba-step-number ba-num-primary">{item.step}</span>
                        <div className="ba-step-title-wrap">
                          <h4 className="ba-step-title">{item.title}</h4>
                          <span className="ba-step-channel ba-channel-primary">{item.channel}</span>
                        </div>
                        <span className="ba-expand-icon" aria-hidden="true">
                          {isExpanded ? '−' : '+'}
                        </span>
                      </div>

                      <p className="ba-step-desc">{item.description}</p>

                      {/* Highlighted Standards-AI Advantage */}
                      <div className="ba-advantage-box">
                        <span className="ba-advantage-label">Intelligence Advantage:</span>
                        <span className="ba-advantage-text">{item.advantage}</span>
                      </div>

                      {/* Illustrative Example (Collapsible / Toggleable) */}
                      {(showExamples || isExpanded) && (
                        <div className="ba-example-box ba-example-box-after" role="note">
                          <span className="ba-example-tag ba-example-tag-after">Example:</span>
                          <span className="ba-example-text">{item.example}</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── TAB CONTENT 2: KEY DIFFERENCES MATRIX ── */}
      {activeTab === 'matrix' && (
        <div className="ba-matrix-wrapper">
          <div className="ba-matrix-table" role="table" aria-label="Key Differences Matrix">
            <div className="ba-matrix-row ba-matrix-header-row" role="row">
              <div className="ba-matrix-cell ba-cell-dim" role="columnheader">Procurement Dimension</div>
              <div className="ba-matrix-cell ba-cell-before" role="columnheader">Traditional Manual Process</div>
              <div className="ba-matrix-cell ba-cell-after" role="columnheader">With Standards-AI</div>
            </div>

            {COMPARISON_DIMENSIONS.map((row, idx) => (
              <div key={idx} className="ba-matrix-row" role="row">
                <div className="ba-matrix-cell ba-cell-dim" role="rowheader">
                  <strong>{row.dimension}</strong>
                </div>
                <div className="ba-matrix-cell ba-cell-before" role="cell">
                  <div className="ba-matrix-cell-content">
                    <span className="ba-status-tag ba-tag-friction">Manual Research</span>
                    <p>{row.before}</p>
                  </div>
                </div>
                <div className="ba-matrix-cell ba-cell-after" role="cell">
                  <div className="ba-matrix-cell-content">
                    <span className="ba-status-tag ba-tag-assist">Automated Assistance</span>
                    <p>{row.after}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Walkthrough Interactive Example Card ── */}
      <div className="ba-example-banner">
        <div className="ba-example-banner-header">
          <span className="ba-badge-example">Illustrative Example</span>
          <h4 className="ba-example-title">Procurement of 25 kVA Outdoor Distribution Transformers</h4>
        </div>
        <div className="ba-example-grid">
          <div className="ba-example-col">
            <span className="ba-example-col-label">Traditional Manual Flow:</span>
            <p className="ba-example-col-text">
              Officer searches "distribution transformer" on search engines, encounters obsolete references to IS 2026 and superseded 1989 editions, manually checks 4 separate amendment circulars, and navigates independent Ministry gazette portals to check mandatory ISI certification rules.
            </p>
          </div>
          <div className="ba-example-divider" aria-hidden="true"></div>
          <div className="ba-example-col">
            <span className="ba-example-col-label ba-col-label-after">Standards-AI Flow:</span>
            <p className="ba-example-col-text">
              Officer enters item description or uploads tender BOQ schedule. Standards-AI parses ratings (25 kVA, 11 kV), retrieves IS 1180 (Part 1):2014, flags active status (Reaffirmed 2021) with published Amendments 1–4, surfaces the statutory Ministry QCO mandate, and provides direct links to the official BIS portal.
            </p>
          </div>
        </div>
      </div>

      {/* ── Mandatory Illustrative Disclaimer Notice ── */}
      <div className="ba-disclaimer-card" role="note">
        <div className="ba-disclaimer-icon" aria-hidden="true">ℹ</div>
        <p className="ba-disclaimer-text">
          <strong>Illustrative Workflow Notice:</strong> This comparison illustrates a representative public procurement discovery and verification workflow. Actual workflow steps, administrative review procedures, and effort vary depending on procurement category, tender complexity, and statutory documentation requirements.
        </p>
      </div>
    </section>
  );
}
