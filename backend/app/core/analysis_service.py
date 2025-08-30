import requests
from PIL import Image
import requests
from transformers import pipeline, CLIPProcessor, CLIPModel
import torch
from typing import Optional
from .gemini_service import gemini_service_instance
from transformers import AutoImageProcessor, AutoModelForImageClassification
import io # For handling image bytes
from .forensics_service import forensics_service_instance

# Import the explainability service we just created
from .explainability_service import explainability_service_instance

# --- Model Loading ---
# Models are loaded once when the application starts to ensure fast API responses.
# The first time the app runs, these models will be downloaded (can be several GB).

print("Loading text analysis pipeline...")
# Using a sentiment model as a proxy for detecting sensationalized/emotive language.
text_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("Text analysis pipeline loaded.")

print("Loading multimodal (CLIP) model...")
# Using OpenAI's CLIP for measuring semantic similarity between image and text.
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
print("Multimodal (CLIP) model loaded.")

print("Loading AI image authenticity model...")
try:
    auth_processor = AutoImageProcessor.from_pretrained("umm-maybe/AI-image-detector")
    auth_model = AutoModelForImageClassification.from_pretrained("umm-maybe/AI-image-detector")
    print("AI image authenticity model loaded.")
except Exception as e:
    print(f"Could not load AI image authenticity model: {e}")
    auth_processor, auth_model = None, None


class AnalysisService:
    """
    Service to perform the core AI/ML analysis on text and image content.
    """

    def _analyze_text(self, text: str) -> dict:
        """
        Analyzes text for cues of misinformation, like high negative sentiment.
        Returns a dictionary with a raw score and an explanation flag.
        """
        try:
            # Truncate text to the model's max input size to avoid errors
            truncated_text = text[:512]
            results = text_analyzer(truncated_text)
            sentiment = results[0]

            # Heuristic: Highly negative content is often sensationalized.
            if sentiment['label'] == 'NEGATIVE' and sentiment['score'] > 0.8:
                return {"score": 0.3, "flag": "The text exhibits strong negative sentiment, which can be a sign of emotive or biased language."}
            else:
                return {"score": 0.7, "flag": "The text's tone appears to be neutral."}
        except Exception as e:
            print(f"Error in text analysis: {e}")
            return {"score": 0.5, "flag": "Text analysis could not be completed."}

    def _match_image_with_text(self, image_url: str, text: str) -> dict:
        """
        Uses CLIP to score the semantic similarity between an image URL and text.
        Returns a dictionary with a score, match status, and an explanation flag.
        """
        try:
            response = requests.get(image_url, stream=True, timeout=15)
            response.raise_for_status()
            image = Image.open(response.raw).convert("RGB")
        except Exception as e:
            print(f"Error fetching or processing image URL '{image_url}': {e}")
            return {"match": False, "score": 0.0, "flag": "The provided image could not be processed."}

        inputs = clip_processor(text=[text[:77]], images=image, return_tensors="pt", padding=True)

        with torch.no_grad():
            outputs = clip_model(**inputs)

        # This is the raw similarity score from the model.
        similarity_score = outputs.logits_per_image.item()

        # A score over 25.0 is a strong indicator of a match for this CLIP model.
        if similarity_score > 25.0:
            return {"match": True, "score": 0.9, "flag": "The main image appears to be semantically related to the article's text."}
        else:
            return {"match": False, "score": 0.2, "flag": "The main image does not seem to match the content of the text."}


    async def analyze_content(self, text: Optional[str] = None, image_bytes: Optional[bytes] = None, image_url: Optional[str] = None, image_source_context: Optional[str] = None) -> dict:
    # --- Initialize result containers ---
        linguistic_analysis = None
        image_analysis = None
        image_authenticity_analysis = None
        gemini_result = None
        final_payload = {}

        # Prioritize uploaded image bytes, but if only a URL is given, download the image.
        effective_image_bytes = image_bytes
        if not effective_image_bytes and image_url:
            print(f"Downloading image from URL: {image_url}")
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status() # Raise an exception for bad status codes
                effective_image_bytes = response.content
                print("Image downloaded successfully.")
            except Exception as e:
                print(f"Failed to download image from URL: {e}")
                # Create a specific error message for the frontend
                image_authenticity_analysis = {"error": "The provided image URL could not be downloaded or is invalid."}

        # --- Perform Image Forensics if we have image data (either uploaded or downloaded) ---
        if effective_image_bytes and not image_authenticity_analysis:
            image_authenticity_analysis = forensics_service_instance.analyze_image_authenticity(effective_image_bytes, source_context=image_source_context or 'unknown')

        # --- Determine the primary claim for Gemini ---
        primary_claim = text
        if not text and effective_image_bytes:
            primary_claim = gemini_service_instance.describe_image_for_claim(effective_image_bytes)
            print(f"Generated claim from image: {primary_claim}")

        # --- Perform Text-based Analyses if a claim exists ---
        if primary_claim:
            linguistic_analysis = self._analyze_text(primary_claim)
            gemini_result = gemini_service_instance.verify_claim(primary_claim)

        # --- Perform Image-Text Coherence (if applicable) ---
        if primary_claim and image_url: # This check remains URL-based
            image_analysis = self._match_image_with_text(image_url, primary_claim)

        # --- Combine all results into the final payload ---
        if gemini_result and "error" not in gemini_result:
            final_payload = gemini_result.copy()
        else:
            final_payload = {
                "verdict": "Analysis Complete" if primary_claim else "Image Analyzed",
                "confidence_score": 0.0,
                "explanation": gemini_result.get("error") if gemini_result else "Provide text for a full fact-check.",
                "correction": None, "enrichment": [], "sources": []
            }

        final_payload['linguistic_analysis'] = linguistic_analysis
        final_payload['image_analysis'] = image_analysis
        final_payload['image_authenticity'] = image_authenticity_analysis

        return final_payload    

# Create a single, reusable instance of the service for the API to use.
analysis_service_instance = AnalysisService()
