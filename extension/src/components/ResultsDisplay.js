import React from 'react';
import './ResultsDisplay.css';

const ResultsDisplay = ({ results }) => {
  // Don't render anything if there are no results yet
  if (!results) {
    return null;
  }

  const { credibility_score, explanation, image_text_match } = results;

  // Helper function to determine the color of the score circle
  const getScoreColor = (score) => {
    if (score >= 0.7) return 'high'; // Green
    if (score >= 0.4) return 'medium'; // Yellow
    return 'low'; // Red
  };

  const scoreColorClass = getScoreColor(credibility_score);
  const scorePercentage = Math.round(credibility_score * 100);

  return (
    <div className="results-card">
      <h3>Analysis Results</h3>
      <div className="results-content">
        <div className={`score-circle ${scoreColorClass}`}>
          <span className="score-value">{scorePercentage}</span>
          <span className="score-label">Credibility Score</span>
        </div>
        <div className="explanation-section">
          <h4>Explanation</h4>
          <p>{explanation}</p>
          {image_text_match !== null && (
            <div className="extra-info">
              <strong>Image-Text Match:</strong>
              <span className={image_text_match ? 'match-true' : 'match-false'}>
                {image_text_match ? ' Matched' : ' Mismatched'}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;
