import React from 'react';
import './ResultsDisplay.css';

// --- Helper function to determine colors and icons based on the verdict ---
const getVerdictDetails = (verdict) => {
  // Handles potential null or undefined verdict
  const lowerCaseVerdict = verdict?.toLowerCase() || '';

  if (lowerCaseVerdict.includes('incorrect') || lowerCaseVerdict.includes('false')) {
    return { className: 'verdict-false', icon: '✕' };
  }
  if (lowerCaseVerdict.includes('misleading') || lowerCaseVerdict.includes('lacks context')) {
    return { className: 'verdict-misleading', icon: '!' };
  }
  if (lowerCaseVerdict.includes('correct') || lowerCaseVerdict.includes('true')) {
    return { className: 'verdict-true', icon: '✓' };
  }
  // Default for "Analysis Complete", "Image Analyzed", or errors
  return { className: 'verdict-neutral', icon: '?' };
};


const ResultsDisplay = ({ results }) => {
  // Main guard clause: Don't render anything if there are no results
  if (!results) {
    return null;
  }

  // Destructure all the rich data from our advanced backend
  const {
    verdict,
    confidence_score,
    explanation,
    correction,
    enrichment,
    sources,
    linguistic_analysis,
    image_analysis,
    image_authenticity,
  } = results;

  const verdictDetails = getVerdictDetails(verdict);
  const confidencePercentage = Math.round((confidence_score || 0) * 100);

  return (
    <div className="results-container">
      {/* 1. The Verdict Header */}
      <div className={`verdict-header ${verdictDetails.className}`}>
        <span className="verdict-icon">{verdictDetails.icon}</span>
        <h2 className="verdict-text">{verdict || 'Analysis Complete'}</h2>
      </div>

      <div className="results-body">
        {/* 2. The Main Finding (Correction or Enrichment) */}
        {(correction || (enrichment && enrichment.length > 0)) && (
          <div className="finding-card">
            <h3>{correction ? 'The Facts Are:' : 'Key Information:'}</h3>
            <p className="finding-text">{correction || enrichment?.join(' ')}</p>
          </div>
        )}

        {/* 3. The Evidence Section */}
        <div className="evidence-section">
          <h3>Analysis Breakdown</h3>

          {/* Fact-Check Details */}
          {explanation && (
             <div className="evidence-item">
                <h4>Fact-Check</h4>
                <div className="evidence-content">
                  <p>{explanation}</p>
                  <div className="confidence-bar">
                    <div className="confidence-fill" style={{ width: `${confidencePercentage}%` }}></div>
                  </div>
                  <span className="confidence-label">Confidence: {confidencePercentage}%</span>
                </div>
            </div>
          )}

          {/* Image Authenticity (Forensics) */}
          {image_authenticity && !image_authenticity.error && (
            <div className="evidence-item">
              <h4>Image Authenticity</h4>
              <div className="evidence-content">
                <p><strong>Verdict:</strong> {image_authenticity.verdict}</p>
                <div className="confidence-bar" style={{marginTop: '0.5rem'}}>
                    <div className="confidence-fill" style={{ width: `${Math.round((image_authenticity.confidence || 0) * 100)}%` }}></div>
                </div>
                <span className="confidence-label">Confidence: {Math.round((image_authenticity.confidence || 0) * 100)}%</span>

                <p style={{marginTop: '1rem'}}>
                    <strong>Forensic Reasoning:</strong><br />
                    {image_authenticity.full_explanation}
                </p>
              </div>
            </div>
          )}

          {/* Linguistic Tone */}
          {linguistic_analysis && (
            <div className="evidence-item">
              <h4>Linguistic Tone</h4>
              <div className="evidence-content">
                  <p>{linguistic_analysis.flag}</p>
              </div>
            </div>
          )}

          {/* Image-Text Coherence */}
          {image_analysis && (
            <div className="evidence-item">
              <h4>Image-Text Coherence</h4>
              <div className="evidence-content">
                <p>{image_analysis.flag}</p>
              </div>
            </div>
          )}

          {/* Credible Sources */}
          {sources && sources.length > 0 && (
             <div className="evidence-item">
                <h4>Credible Sources</h4>
                 <div className="evidence-content">
                    <ul className="sources-list">
                        {sources.map((source, index) => (
                            <li key={index}>
                              <a href={source} target="_blank" rel="noopener noreferrer">
                                {new URL(source).hostname.replace('www.', '')}
                              </a>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;
