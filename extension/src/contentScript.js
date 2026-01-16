/**
 * This script is injected into the active webpage to extract content.
 * It finds the main article text and a potential main image URL.
 */
(() => {
  // Heuristic to find the main content body. Look for the element with the most <p> tags.
  const allElements = document.querySelectorAll('body *');
  let mainContentElement = null;
  let maxPCount = 0;

  allElements.forEach(el => {
    const pCount = el.querySelectorAll('p').length;
    if (pCount > maxPCount && el.textContent.length > 500) { // Require some minimum length
      mainContentElement = el;
      maxPCount = pCount;
    }
  });

  const textContent = mainContentElement ? mainContentElement.innerText : document.body.innerText;

  // Heuristic to find the main image. Look for the Open Graph image meta tag first.
  let imageUrl = '';
  const ogImage = document.querySelector("meta[property='og:image']");
  if (ogImage) {
    imageUrl = ogImage.content;
  }

  // The content script sends a message back to the service worker with the extracted data.
  // Note: We use chrome.runtime.sendMessage, which is the standard way for content scripts
  // to communicate back to the extension's background script.
  chrome.runtime.sendMessage({
    type: "CONTENT_EXTRACTED",
    payload: {
      text: textContent.trim(),
      imageUrl: imageUrl,
    }
  });
})();
