import React, { useState } from 'react';
import './App.css'; // This CSS file will be the most important change

// Import components
import UrlInput from './components/UrlInput';
import Loader from './components/Loader';
import ResultsDisplay from './components/ResultsDisplay';
import Placeholder from './components/Placeholder'; // Import the new placeholder

// Import the API client function
import { analyzeContent } from './api/apiClient';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (contentToAnalyze) => {
    setIsLoading(true);
    setError('');
    setResults(null);

    try {
      const analysisResults = await analyzeContent(contentToAnalyze);
      setResults(analysisResults);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Misinformation Detector</h1>
        <p className="subtitle">A real-time dashboard to analyze and verify content credibility.</p>
      </header>

      {/* This is the new two-column layout container */}
      <main className="App-main-grid">
        <div className="input-column">
          <UrlInput onAnalyze={handleAnalyze} isLoading={isLoading} />
        </div>

        <div className="results-column">
          {isLoading && <Loader />}
          {error && <div className="error-message">{error}</div>}
          {results && !isLoading && <ResultsDisplay results={results} />}

          {/* Show placeholder only when there's nothing else to show */}
          {!isLoading && !error && !results && <Placeholder />}
        </div>
      </main>
    </div>
  );
}

export default App;
