import React, { useState, useRef, useEffect } from 'react';

const QUICK_QUERIES = [
  "12 mm TMT reinforcement bars for RCC construction",
  "12 mm Fe 500 TMT sariya RCC construction ke liye",
  "12 मिमी Fe 500 TMT सरिया RCC निर्माण के लिए",
  "கட்டுமானத்திற்கான 12 மிமீ டிஎம்டி கம்பிகள்",
  "450/750 V PVC copper cable बिजली wiring ke liye",
  "Hot rolled structural steel plates for bridge fabrication",
  "High density polyethylene HDPE pipes for potable water supply",
  "Industrial safety helmets for construction workers"
];

export default function SearchBar({
  query,
  setQuery,
  onSearch,
  loading,
  loadingText,
  limit,
  setLimit,
  isFromDoc,
  onClearQuery,
}) {
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  const recognitionRef = useRef(null);

  // Feature 3: Browser Web Speech API SpeechRecognition (English en-IN)
  const SpeechRecognition = typeof window !== 'undefined'
    ? (window.SpeechRecognition || window.webkitSpeechRecognition)
    : null;
  const isSpeechSupported = Boolean(SpeechRecognition);

  // Auto-dismiss voice message after 6 seconds
  useEffect(() => {
    if (voiceError) {
      const timer = setTimeout(() => {
        setVoiceError(null);
      }, 6000);
      return () => clearTimeout(timer);
    }
  }, [voiceError]);

  // Clean up recognition if unmounted
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  const startListening = () => {
    if (!isSpeechSupported) {
      setVoiceError('Speech recognition is not supported in this browser. Please use Chrome, Edge, or a compatible browser.');
      return;
    }

    setVoiceError(null);

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-IN'; // English (India) per requirement 3
      recognition.interimResults = false;
      recognition.continuous = false; // Single session per requirement 11
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
        setVoiceError(null);
      };

      recognition.onresult = (event) => {
        let transcript = '';
        if (event.results) {
          for (let i = 0; i < event.results.length; i++) {
            if (event.results[i] && event.results[i][0]) {
              transcript += event.results[i][0].transcript;
            }
          }
        }
        const cleanedTranscript = transcript.trim();
        if (cleanedTranscript) {
          setQuery(cleanedTranscript);
        }
      };

      recognition.onerror = (event) => {
        setIsListening(false);
        const err = event.error;
        if (err === 'not-allowed' || err === 'permission-denied') {
          setVoiceError('Microphone permission denied. Please allow microphone access in your browser settings.');
        } else if (err === 'no-speech') {
          setVoiceError('No speech detected. Please click Voice and speak clearly.');
        } else if (err === 'audio-capture') {
          setVoiceError('No microphone detected. Please check your audio input device.');
        } else if (err === 'network') {
          setVoiceError('Network error during speech recognition. Please check your connection.');
        } else if (err === 'aborted') {
          // User stopped manually; clean reset
          setVoiceError(null);
        } else {
          setVoiceError(`Voice recognition error: ${err}`);
        }
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.warn('SpeechRecognition start failed:', err);
      setIsListening(false);
      setVoiceError('Unable to start speech recognition. Please try again.');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
    }
    setIsListening(false);
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !loading && !isListening) {
        onSearch(query);
      }
    }
  };

  const wordCount = query.trim() ? query.trim().split(/\s+/).length : 0;
  const isLargeText = query.length > 400;
  const INDIC_REGEX = /[\u0900-\u0D7F\u0600-\u06FF]/;
  const isIndic = INDIC_REGEX.test(query);

  return (
    <div className="search-container" role="search" aria-label="Indian Standards Specification Search">
      <div className="search-header-group">
        <div className="search-header-top">
          <h2 className="search-main-heading">Find Applicable Indian Standards</h2>
          {isFromDoc && (
            <span className="source-doc-pill" title="Specification loaded from PDF Tender Document">
              📄 Loaded from Tender Document
            </span>
          )}
        </div>
        <p className="search-subtext">
          Enter technical specifications, item descriptions, material grades, or procurement clauses in English or 22 Indian languages (powered by Sarvam AI).
        </p>
      </div>

      <div className="search-input-area">
        <div className="textarea-wrapper">
          <textarea
            id="procurement-query"
            className={`search-textarea ${isLargeText ? 'large-content' : ''}`}
            rows={3}
            placeholder="Enter procurement requirement (e.g., '12 mm Fe 500 TMT sariya RCC construction ke liye' or 'Hot rolled steel plates')..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            aria-label="Procurement Specification Query"
          />

          {query && !loading && (
            <button
              type="button"
              className="clear-query-btn"
              onClick={onClearQuery ? onClearQuery : () => setQuery('')}
              title="Clear search text"
              aria-label="Clear search input"
            >
              &times;
            </button>
          )}
        </div>

        <div className="search-controls-row">
          <div className="search-controls-left">
            {isIndic ? (
              <span className="multilingual-tag indic-detected" title="Indian-language script detected. Will translate via Sarvam AI (sarvam-translate:v1)">
                <span>🇮🇳 Indian Language · Translates via Sarvam AI</span>
              </span>
            ) : query.trim() ? (
              <span className="multilingual-tag" title="Standard English specification. Direct BIS standards search.">
                <span>✓ English · Direct BIS search</span>
              </span>
            ) : (
              <span className="multilingual-tag" title="Supports English and 22 Indian languages via Sarvam AI">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                <span>English & 22 Indian Languages (Sarvam AI)</span>
              </span>
            )}

            <span className="search-char-count">
              {query.length} chars{wordCount > 0 ? ` · ${wordCount} words` : ''}
            </span>

            {setLimit && (
              <label className="limit-select-label">
                <span>Limit:</span>
                <select
                  value={limit || 10}
                  onChange={(e) => setLimit(Number(e.target.value))}
                  disabled={loading}
                  className="limit-select"
                  aria-label="Number of results to return"
                >
                  <option value={5}>Top 5</option>
                  <option value={10}>Top 10</option>
                  <option value={15}>Top 15</option>
                </select>
              </label>
            )}
          </div>

          <div className="search-controls-right">
            {query && (
              <button
                type="button"
                className="clear-text-link"
                onClick={onClearQuery ? onClearQuery : () => setQuery('')}
                disabled={loading || isListening}
              >
                Clear
              </button>
            )}

            {/* Feature 3: English Speech-to-Text Microphone Button */}
            <button
              type="button"
              id="voice-input-btn"
              className={`voice-input-btn ${isListening ? 'listening' : ''}`}
              onClick={toggleListening}
              disabled={loading}
              title={
                !isSpeechSupported
                  ? 'Voice input not supported in this browser'
                  : isListening
                  ? 'Listening for English speech... Click to stop'
                  : 'Speak specification in English (en-IN Speech-to-Text)'
              }
              aria-label={isListening ? 'Stop voice input' : 'Start voice input (English en-IN)'}
              aria-pressed={isListening}
            >
              {isListening ? (
                <>
                  <span className="listening-pulse-dot" aria-hidden="true"></span>
                  <span>Stop</span>
                </>
              ) : (
                <>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                    <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
                    <line x1="12" y1="19" x2="12" y2="23"/>
                    <line x1="8" y1="23" x2="16" y2="23"/>
                  </svg>
                  <span>Voice</span>
                </>
              )}
            </button>

            <button
              id="search-btn"
              type="button"
              className="search-submit-btn"
              onClick={() => onSearch(query)}
              disabled={loading || !query.trim() || isListening}
            >
              {loading ? (
                <>
                  <span className="spinner spinner-white" aria-hidden="true"></span>
                  <span>{loadingText || 'Searching Standards...'}</span>
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  </svg>
                  <span>Find Applicable Standards</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Feature 3: Real-time Listening and Error Feedback */}
        {isListening && (
          <div className="voice-listening-bar" role="status" aria-live="polite">
            <span className="listening-pulse-dot" aria-hidden="true"></span>
            <span className="voice-listening-text">
              <strong>Listening (English en-IN)...</strong> Speak your procurement requirement. Click Stop when done.
            </span>
          </div>
        )}

        {voiceError && (
          <div className="voice-error-toast" role="alert">
            <span className="voice-error-text">⚠️ {voiceError}</span>
            <button
              type="button"
              className="voice-error-close"
              onClick={() => setVoiceError(null)}
              aria-label="Dismiss voice message"
            >
              &times;
            </button>
          </div>
        )}
      </div>

      <div className="sample-queries-section">
        <div className="sample-queries-title">Sample Procurement Specifications (Click to Test):</div>
        <div className="sample-chips-row">
          {QUICK_QUERIES.map((item, idx) => (
            <button
              key={idx}
              className="sample-chip"
              type="button"
              onClick={() => {
                setQuery(item);
                onSearch(item);
              }}
              disabled={loading}
            >
              {item}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
