import React, { useState, useRef } from 'react';
import './UrlInput.css';

const UrlInput = ({ onAnalyze, isLoading }) => {
  const [text, setText] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [fileName, setFileName] = useState('');
  // --- NEW STATE for image context ---
  const [imageSourceContext, setImageSourceContext] = useState('downloaded'); // Default to the most common case
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImageFile(file);
      setFileName(file.name);
      setImageUrl('');
    }
  };

  const handleImageUrlChange = (event) => {
    setImageUrl(event.target.value);
    if (imageFile) {
      setImageFile(null);
      setFileName('');
      if(fileInputRef.current) fileInputRef.current.value = null;
    }
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!text.trim() && !imageFile && !imageUrl.trim()) {
      alert('Please provide text, an image URL, or upload an image to analyze.');
      return;
    }
    // --- Pass the new context to the parent ---
    onAnalyze({ text, imageUrl, imageFile, imageSourceContext });
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <h2>Analyze Content</h2>
      <p>Provide text, an image, and its source to get the most accurate analysis.</p>

      <div className="form-group">
        <label htmlFor="text-content">Text Content (Optional)</label>
        <textarea
          id="text-content"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste text here..."
          rows="8"
          disabled={isLoading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="image-url">Image URL or Upload</label>
        <input
          id="image-url"
          type="url"
          value={imageUrl}
          onChange={handleImageUrlChange}
          placeholder="Paste an image URL..."
          disabled={isLoading}
        />
      </div>

      <div className="or-divider">OR</div>

      <div className="form-group">
        <div className="file-display-area" onClick={() => fileInputRef.current.click()}>
          {fileName || 'Click to upload an image from your device'}
        </div>
        <input id="image-upload" type="file" accept="image/*" onChange={handleFileChange} disabled={isLoading} ref={fileInputRef} style={{ display: 'none' }} />
      </div>

      {/* --- NEW SECTION for Image Source Context --- */}
      {(imageFile || imageUrl) && (
        <div className="form-group source-context-group">
            <label>Where did this image come from?</label>
            <div className="radio-options">
                <label className="radio-label">
                    <input type="radio" value="downloaded" checked={imageSourceContext === 'downloaded'} onChange={(e) => setImageSourceContext(e.target.value)} />
                    Website / Social Media
                </label>
                <label className="radio-label">
                    <input type="radio" value="messaging" checked={imageSourceContext === 'messaging'} onChange={(e) => setImageSourceContext(e.target.value)} />
                    Messaging App (WhatsApp)
                </label>
                <label className="radio-label">
                    <input type="radio" value="camera" checked={imageSourceContext === 'camera'} onChange={(e) => setImageSourceContext(e.target.value)} />
                    My own camera/phone
                </label>
                <label className="radio-label">
                    <input type="radio" value="unknown" checked={imageSourceContext === 'unknown'} onChange={(e) => setImageSourceContext(e.target.value)} />
                    Other / I don't know
                </label>
            </div>
        </div>
      )}

      <button type="submit" className="analyze-button" disabled={isLoading}>
        {isLoading ? 'Analyzing...' : 'Analyze'}
      </button>
    </form>
  );
};

export default UrlInput;
