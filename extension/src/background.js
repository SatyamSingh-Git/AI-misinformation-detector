// The base URL for your backend API.
// IMPORTANT: Update this if your backend is deployed elsewhere.
const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Fetches analysis from the backend API.
 * @param {object} content - The content to analyze { text, imageUrl }.
 */
const fetchAnalysis = async (content) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: content.text,
        image_url: content.imageUrl,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Server error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API request failed:", error);
    // Propagate a structured error object
    return { error: true, message: error.message };
  }
};

/**
 * Main message listener for communications from other parts of the extension.
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Listener for when the content script sends back the extracted page data
  if (message.type === "CONTENT_EXTRACTED") {
    // We've received the content, now call the API
    fetchAnalysis(message.payload).then(analysisResult => {
      // Save the result to local storage for the popup to access
      chrome.storage.local.set({ analysisResult: analysisResult });
    });
  }

  // Listener for when the popup requests an analysis
  if (message.type === "ANALYZE_PAGE") {
    // When the popup button is clicked, we inject the content script into the active tab
    chrome.tabs.query({ active: true, currentWindow: true }).then(([tab]) => {
      if (tab) {
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['contentScript.js'],
        });
      }
    });
  }

  // Return true to indicate you wish to send a response asynchronously
  return true;
});
