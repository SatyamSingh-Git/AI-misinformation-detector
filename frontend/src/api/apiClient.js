const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const analyzeContent = async (content) => {
  const { text, imageUrl, imageFile, imageSourceContext } = content;

  // Use FormData to send multipart data (for the file upload)
  const formData = new FormData();

  if (text) formData.append('text', text);
  if (imageUrl) formData.append('image_url', imageUrl);
  if (imageFile) formData.append('image_file', imageFile);
  if (imageSourceContext) formData.append('image_source_context', imageSourceContext); // Append the new data

  try {
    // We no longer set 'Content-Type'. The browser does it automatically
    // for FormData, including the crucial 'boundary' part.
    const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Server error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to analyze content:", error);
    throw error;
  }
};
