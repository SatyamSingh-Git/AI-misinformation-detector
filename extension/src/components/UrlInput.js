import React, { useState } from 'react';
import './UrlInput.css';

const UrlInput = ({ onAnalyze, isLoading }) => {
  const [text, setText] = useState('');
  const [imageUrl, setImageUrl] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!text.trim()) {
      alert('Please enter some text content to analyze.');
      return;
    }
    // Call the function passed from the parent component (App.js)
    onAnalyze({ text, imageUrl });
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <h2>Analyze Content</h2>
      <p>Paste the text from an article and optionally provide an image URL to check for credibility.</p>

      <div className="form-group">
        <label htmlFor="text-content">Article Text</label>
        <textarea
          id="text-content"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste the full text of the article here..."
          rows="10"
          required
          disabled={isLoading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="image-url">Image URL (Optional)</label>
        <input
          id="image-url"
          type="url"
          value={imageUrl}
          onChange={(e) => setImageUrl(e.target.value)}
          placeholder="https://example.com/path/to/image.jpg"
          disabled={isLoading}
        />
      </div>

      <button type="submit" className="analyze-button" disabled={isLoading}>
        {isLoading ? 'Analyzing...' : 'Analyze'}
      </button>
    </form>
  );
};

export default UrlInput;
