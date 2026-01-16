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
try:
    text_analyzer = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    print("Text analysis pipeline loaded.")
except Exception as e:
    print(f"Could not load text analyzer: {e}")
    text_analyzer = None

print("Loading multimodal (CLIP) model...")
# Using OpenAI's CLIP for measuring semantic similarity between image and text.
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
print("Multimodal (CLIP) model loaded.")

print("Loading AI vs Human image detector model...")
try:
    # Load the local fine-tuned SigLIP model for AI/Human image classification
    from pathlib import Path
    docker_path = Path("/app/ai-vs-human-image-detector")
    local_path = Path(__file__).parent.parent.parent.parent / "ai-vs-human-image-detector"
    
    model_path = docker_path if docker_path.exists() else local_path
    auth_processor = AutoImageProcessor.from_pretrained(str(model_path))
    auth_model = AutoModelForImageClassification.from_pretrained(str(model_path))
    print(f"AI vs Human image detector loaded from: {model_path}")
except Exception as e:
    print(f"Could not load AI vs Human image detector model: {e}")
    auth_processor, auth_model = None, None


class AnalysisService:
    """
    Service to perform the core AI/ML analysis on text and image content.
    """

    def _analyze_text(self, text: str) -> dict:
        """
        Comprehensive linguistic analysis including sentiment, tone, style, and nature.
        Returns a detailed dictionary with scores and multi-dimensional analysis.
        """
        if not text_analyzer:
            return {"score": 0.5, "flag": "Text analysis not available."}
        
        try:
            # Truncate text to the model's max input size to avoid errors
            truncated_text = text[:512]
            
            # --- Sentiment Analysis ---
            sentiment_results = text_analyzer(truncated_text)
            sentiment = sentiment_results[0]
            sentiment_label = sentiment['label']
            sentiment_score = sentiment['score']
            
            # --- Tone Analysis ---
            tone = self._analyze_tone(truncated_text, sentiment_label)
            
            # --- Style Analysis ---
            style = self._analyze_style(truncated_text)
            
            # --- Nature Analysis (provocative, inflammatory, etc.) ---
            nature = self._analyze_nature(truncated_text)
            
            # --- Calculate Overall Credibility Score ---
            # Lower score = more suspicious
            credibility_score = 0.7  # Base score
            
            # Adjust based on sentiment extremity
            if sentiment_score > 0.85:
                credibility_score -= 0.15
            elif sentiment_score > 0.75:
                credibility_score -= 0.1
            
            # Adjust based on nature indicators
            if nature['is_provocative'] or nature['is_inflammatory']:
                credibility_score -= 0.2
            if nature['is_biased']:
                credibility_score -= 0.15
            if nature['is_clickbait']:
                credibility_score -= 0.25
            
            # Adjust based on style
            if style['is_sensationalist']:
                credibility_score -= 0.15
            if style['excessive_punctuation'] or style['excessive_caps']:
                credibility_score -= 0.1
                
            # Ensure score stays in valid range
            credibility_score = max(0.0, min(1.0, credibility_score))
            
            # --- Build Comprehensive Flag/Explanation ---
            flags = []
            
            # Sentiment flags
            if sentiment_label == 'NEGATIVE' and sentiment_score > 0.8:
                flags.append(f"Strong negative sentiment (confidence: {sentiment_score:.1%})")
            elif sentiment_label == 'POSITIVE' and sentiment_score > 0.8:
                flags.append(f"Strong positive sentiment (confidence: {sentiment_score:.1%})")
            else:
                flags.append(f"Neutral to mild sentiment")
            
            # Tone flags
            flags.append(f"Tone: {tone['primary_tone']}")
            
            # Style flags
            if style['is_sensationalist']:
                flags.append("Sensationalist writing style detected")
            if style['excessive_caps']:
                flags.append("Excessive capitalization used")
            if style['excessive_punctuation']:
                flags.append("Excessive punctuation marks")
            
            # Nature flags
            if nature['is_provocative']:
                flags.append("Provocative language detected")
            if nature['is_inflammatory']:
                flags.append("Inflammatory content present")
            if nature['is_biased']:
                flags.append("Potential bias indicators found")
            if nature['is_clickbait']:
                flags.append("Clickbait patterns identified")
            
            return {
                "score": credibility_score,
                "flag": " | ".join(flags),
                "sentiment": {
                    "label": sentiment_label,
                    "confidence": sentiment_score
                },
                "tone": tone,
                "style": style,
                "nature": nature
            }
            
        except Exception as e:
            print(f"Error in text analysis: {e}")
            return {"score": 0.5, "flag": "Text analysis could not be completed."}
    
    def _analyze_tone(self, text: str, sentiment_label: str) -> dict:
        """Analyze the tone of the text (formal, casual, aggressive, etc.)"""
        text_lower = text.lower()
        
        # Tone indicators
        formal_indicators = ['furthermore', 'therefore', 'consequently', 'moreover', 'nonetheless']
        casual_indicators = ['yeah', 'gonna', 'wanna', 'kinda', 'sorta', 'cool', 'awesome']
        aggressive_indicators = ['must', 'never', 'always', 'everyone', 'no one', 'demand', 'insist']
        urgent_indicators = ['now', 'immediately', 'urgent', 'breaking', 'alert', 'warning']
        
        formal_count = sum(1 for word in formal_indicators if word in text_lower)
        casual_count = sum(1 for word in casual_indicators if word in text_lower)
        aggressive_count = sum(1 for word in aggressive_indicators if word in text_lower)
        urgent_count = sum(1 for word in urgent_indicators if word in text_lower)
        
        # Determine primary tone
        if urgent_count > 2:
            primary_tone = "urgent"
        elif aggressive_count > 2:
            primary_tone = "aggressive"
        elif formal_count > casual_count:
            primary_tone = "formal"
        elif casual_count > 0:
            primary_tone = "casual"
        elif sentiment_label == 'NEGATIVE':
            primary_tone = "critical"
        else:
            primary_tone = "neutral"
        
        return {
            "primary_tone": primary_tone,
            "is_formal": formal_count > casual_count,
            "is_aggressive": aggressive_count > 2,
            "is_urgent": urgent_count > 2
        }
    
    def _analyze_style(self, text: str) -> dict:
        """Analyze writing style (sensationalist, objective, etc.)"""
        
        # Sensationalist keywords
        sensationalist_words = [
            'shocking', 'unbelievable', 'amazing', 'incredible', 'stunning',
            'outrageous', 'explosive', 'bombshell', 'devastating', 'miraculous',
            'secret', 'exposed', 'revealed', 'truth', 'they don\'t want you to know'
        ]
        
        text_lower = text.lower()
        sensationalist_count = sum(1 for word in sensationalist_words if word in text_lower)
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        excessive_punctuation = exclamation_count > 2 or question_count > 3
        
        # Check for excessive capitalization
        words = text.split()
        if words:
            caps_words = sum(1 for word in words if len(word) > 2 and word.isupper())
            excessive_caps = (caps_words / len(words)) > 0.15
        else:
            excessive_caps = False
        
        return {
            "is_sensationalist": sensationalist_count >= 2,
            "excessive_punctuation": excessive_punctuation,
            "excessive_caps": excessive_caps,
            "sensationalist_word_count": sensationalist_count
        }
    
    def _analyze_nature(self, text: str) -> dict:
        """Analyze nature of content (provocative, inflammatory, biased, etc.)"""
        text_lower = text.lower()
        
        # Provocative language
        provocative_words = [
            'outrage', 'scandal', 'corrupt', 'fraud', 'scam', 'lie', 'fake',
            'hoax', 'conspiracy', 'cover-up', 'hidden agenda'
        ]
        
        # Inflammatory language
        inflammatory_words = [
            'destroy', 'attack', 'war', 'enemy', 'threat', 'danger', 'crisis',
            'disaster', 'catastrophe', 'chaos', 'invaded', 'assault'
        ]
        
        # Bias indicators
        bias_words = [
            'always', 'never', 'everyone', 'no one', 'all', 'none',
            'clearly', 'obviously', 'undoubtedly', 'certainly'
        ]
        
        # Clickbait patterns
        clickbait_patterns = [
            'you won\'t believe', 'what happened next', 'will shock you',
            'this one trick', 'doctors hate', 'number', '#'
        ]
        
        provocative_count = sum(1 for word in provocative_words if word in text_lower)
        inflammatory_count = sum(1 for word in inflammatory_words if word in text_lower)
        bias_count = sum(1 for word in bias_words if word in text_lower)
        clickbait_count = sum(1 for pattern in clickbait_patterns if pattern in text_lower)
        
        return {
            "is_provocative": provocative_count >= 2,
            "is_inflammatory": inflammatory_count >= 2,
            "is_biased": bias_count >= 3,
            "is_clickbait": clickbait_count >= 1,
            "provocative_indicators": provocative_count,
            "inflammatory_indicators": inflammatory_count,
            "bias_indicators": bias_count
        }

    def _match_image_with_text(self, text: str, image_url: Optional[str] = None, image_bytes: Optional[bytes] = None) -> dict:
        """
        Uses CLIP to score the semantic similarity between an image and text.
        Accepts either an image URL or image bytes.
        Returns a dictionary with a score, match status, and an explanation flag.
        """
        try:
            # Load image from URL or bytes
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            elif image_url:
                response = requests.get(image_url, stream=True, timeout=15)
                response.raise_for_status()
                image = Image.open(response.raw).convert("RGB")
            else:
                return {"match": False, "score": 0.0, "flag": "No image provided for CLIP analysis."}
                
        except Exception as e:
            print(f"Error processing image for CLIP analysis: {e}")
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

        # --- Perform Image-Text Coherence using CLIP (if we have both text and image) ---
        if primary_claim and (image_url or effective_image_bytes):
            # Use either uploaded image bytes or URL for CLIP analysis
            image_analysis = self._match_image_with_text(
                text=primary_claim,
                image_url=image_url if not effective_image_bytes else None,
                image_bytes=effective_image_bytes
            )

        # --- Perform Text-based Analyses if a claim exists ---
        if primary_claim:
            linguistic_analysis = self._analyze_text(primary_claim)
            
            # Pass all analysis results to Gemini for comprehensive verdict
            gemini_result = gemini_service_instance.verify_claim(
                primary_claim,
                linguistic_analysis=linguistic_analysis,
                image_analysis=image_analysis,
                image_authenticity=image_authenticity_analysis
            )

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
