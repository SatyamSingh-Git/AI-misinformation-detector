/*global chrome*/ // This tells ESLint that 'chrome' is a global variable
import React, { useState, useEffect } from 'react';
import './App.css';

// You can reuse the Loader and ResultsDisplay components from your frontend web app!
// Just copy the component files (and their CSS) into a 'components' folder
// within 'extension/src/'. For this example, I'll assume they exist.
import Loader from './components/Loader';
import ResultsDisplay from './components/ResultsDisplay';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  // Effect to load results from storage when the popup opens
  useEffect(() => {
    // Immediately check storage for any existing results
    chrome.storage.local.get(['analysisResult'], (data) => {
      if (data.analysisResult) {
        handleResult(data.analysisResult);
      }
    });

    // Set up a listener for storage changes
    const storageListener = (changes, area) => {
      if (area === 'local' && changes.analysisResult) {
        handleResult(changes.analysisResult.newValue);
      }
    };
    chrome.storage.onChanged.addListener(storageListener);

    // Cleanup listener on component unmount
    return () => {
      chrome.storage.onChanged.removeListener(storageListener);
    };
  }, []);

  const handleResult = (result) => {
    setIsLoading(false);
    if (result.error) {
      setError(result.message);
      setResults(null);
    } else {
      setResults(result);
      setError('');
    }
  };

  const handleAnalyzeClick = () => {
    setIsLoading(true);
    setError('');
    setResults(null);

    // Clear previous results from storage
    chrome.storage.local.remove(['analysisResult']);

    // Send a message to the background script to start the analysis
    chrome.runtime.sendMessage({ type: "ANALYZE_PAGE" });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h3>Misinformation Detector</h3>
      </header>
      <main className="App-main">
        {isLoading ? (
          <Loader />
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : results ? (
          <ResultsDisplay results={results} />
        ) : (
          <div className="initial-view">
            <p>Click the button to analyze the current page for potential misinformation.</p>
            <button onClick={handleAnalyzeClick} className="analyze-button">
              Analyze Page
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
