# In backend/app/core/gemini_service.py
import google.generativeai as genai
import json
import requests
from typing import List, Dict, Optional
from ..config import get_settings
from PIL import Image
import io
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import os

# --- Configuration ---
FACT_CHECK_API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# --- Gemini Model Configuration ---
try:
    settings = get_settings()
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("Gemini model configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini model: {e}")
    model = None

class GeminiService:
    def _query_fact_check_api(self, claim: str) -> Optional[List[Dict]]:
        """
        Queries the Google Fact Check Tools API for professional fact-checks.
        Returns a list of fact-check results from credible sources.
        Requires the same Google API key used for Gemini.
        """
        try:
            params = {
                'query': claim,
                'languageCode': 'en',
                'key': settings.GOOGLE_API_KEY  # Use the same API key
            }
            
            response = requests.get(FACT_CHECK_API_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            claims = data.get('claims', [])
            
            if not claims:
                return None
            
            # Process and structure the fact-check results
            fact_checks = []
            for claim_review in claims[:3]:  # Limit to top 3 results
                claim_text = claim_review.get('text', '')
                claim_reviews = claim_review.get('claimReview', [])
                
                for review in claim_reviews:
                    publisher = review.get('publisher', {}).get('name', 'Unknown')
                    url = review.get('url', '')
                    title = review.get('title', '')
                    rating = review.get('textualRating', 'No rating')
                    
                    fact_checks.append({
                        'claim': claim_text,
                        'publisher': publisher,
                        'rating': rating,
                        'title': title,
                        'url': url
                    })
            
            return fact_checks if fact_checks else None
            
        except requests.exceptions.RequestException as e:
            print(f"Error querying Fact Check API: {e}")
            # Check if it's a 403 error (API not enabled)
            if hasattr(e, 'response') and e.response and e.response.status_code == 403:
                print("Note: Google Fact Check API may not be enabled. Enable it at: https://console.cloud.google.com/apis/library/factchecktools.googleapis.com")
            return None
        except Exception as e:
            print(f"Unexpected error in Fact Check API: {e}")
            return None
    
    def _create_super_prompt(self, claim: str, fact_check_results: Optional[List[Dict]] = None, 
                            linguistic_analysis: Optional[Dict] = None,
                            image_analysis: Optional[Dict] = None,
                            image_authenticity: Optional[Dict] = None) -> str:
        """
        A sophisticated prompt that asks for a full analysis, enrichment, and sources.
        Now incorporates professional fact-check results, linguistic analysis, CLIP image-text coherence, and image authenticity.
        """
        fact_check_context = ""
        if fact_check_results:
            fact_check_context = "\n\nProfessional fact-checkers have already reviewed similar claims:\n"
            for fc in fact_check_results:
                fact_check_context += f"- {fc['publisher']}: '{fc['rating']}' ({fc['url']})\n"
            fact_check_context += "\nConsider these professional assessments in your analysis.\n"
        
        # Add linguistic analysis context
        linguistic_context = ""
        if linguistic_analysis:
            tone = linguistic_analysis.get('tone', {})
            nature = linguistic_analysis.get('nature', {})
            style = linguistic_analysis.get('style', {})
            linguistic_context = f"\n\nLinguistic Analysis:\n"
            linguistic_context += f"- Tone: {tone.get('primary_tone', 'neutral')}\n"
            if nature.get('is_provocative'):
                linguistic_context += "- Contains provocative language\n"
            if nature.get('is_inflammatory'):
                linguistic_context += "- Contains inflammatory language\n"
            if nature.get('is_clickbait'):
                linguistic_context += "- Shows clickbait patterns\n"
            if style.get('is_sensationalist'):
                linguistic_context += "- Uses sensationalist style\n"
        
        # Add CLIP image-text coherence context
        clip_context = ""
        if image_analysis:
            if not image_analysis.get('match', True):
                clip_context = "\n\nImage-Text Coherence Analysis (CLIP Model):\n"
                clip_context += f"- WARNING: The provided image does NOT match the text content semantically.\n"
                clip_context += f"- {image_analysis.get('flag', 'Image and text appear unrelated')}\n"
                clip_context += "- This could indicate potential misinformation or misleading content.\n"
            else:
                clip_context = "\n\nImage-Text Coherence Analysis (CLIP Model):\n"
                clip_context += f"- The image and text appear to be semantically related.\n"
        
        # Add image authenticity context
        authenticity_context = ""
        if image_authenticity and not image_authenticity.get('error'):
            authenticity_context = "\n\nImage Authenticity Analysis (AI Detection):\n"
            authenticity_context += f"- Verdict: {image_authenticity.get('verdict', 'Unknown')}\n"
            authenticity_context += f"- Confidence: {image_authenticity.get('confidence', 0):.2f}\n"
            if 'AI-generated' in image_authenticity.get('verdict', ''):
                authenticity_context += "- WARNING: This image may be artificially generated, not a real photograph.\n"
        
        return f"""
        You are a world-class Trust & Safety analysis engine. Your task is to analyze a given claim for factual accuracy, provide context, and cite credible sources.

        Analyze this claim: "{claim}"
        {fact_check_context}{linguistic_context}{clip_context}{authenticity_context}

        IMPORTANT: Consider ALL the context provided above when forming your verdict. If the image-text coherence analysis shows a mismatch, or if the linguistic analysis reveals manipulative language, or if the image appears to be AI-generated, factor this into your verdict and explanation.

        Your response MUST be a single, minified JSON object with the following schema. Do not include any text before or after the JSON object.

        {{
          "verdict": "A short, definitive verdict. Choose one of: 'Factually Correct', 'Factually Incorrect', 'Misleading', 'Lacks Context'.",
          "confidence_score": "A float from 0.0 to 1.0 representing your confidence in the verdict.",
          "explanation": "A detailed but concise explanation of your reasoning. Explain WHY the claim is correct or incorrect. If it's misleading, explain what nuance is missing. MUST reference image-text mismatch if detected, AI-generated image if detected, or manipulative language patterns if found.",
          "correction": "If the verdict is 'Factually Incorrect' or 'Misleading', provide the corrected information. Otherwise, this should be null.",
          "enrichment": "An array of 2-3 strings. Each string is an additional, interesting, and verifiable fact that provides more context about the main subjects of the claim. This should be provided even if the claim is correct.",
          "sources": "An array of 2-3 URL strings from highly credible, publicly available sources that a user can visit to verify the information (e.g., Wikipedia, Reuters, BBC, Britannica, major scientific journals)."
        }}
        """

    def verify_claim(self, claim: str, linguistic_analysis: Optional[Dict] = None,
                    image_analysis: Optional[Dict] = None, 
                    image_authenticity: Optional[Dict] = None) -> dict:
        if not model:
            return {"error": "Gemini model is not configured."}
        if not claim or not claim.strip():
            return {"error": "Claim cannot be empty."}

        try:
            # Query Google Fact Check API first
            fact_check_results = self._query_fact_check_api(claim)
            
            # Use Gemini with all available context
            prompt = self._create_super_prompt(
                claim, 
                fact_check_results,
                linguistic_analysis=linguistic_analysis,
                image_analysis=image_analysis,
                image_authenticity=image_authenticity
            )
            response = model.generate_content(prompt)

            cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_response)
            
            # Add fact-check results to the response
            result['professional_fact_checks'] = fact_check_results
            
            return result
        except Exception as e:
            print(f"Error during Gemini verification: {e}")
            return {"error": "An error occurred during fact-checking."}

    def describe_image_for_claim(self, image_bytes: bytes) -> str:
        """
        Uses Gemini's multimodal capabilities to describe an image and generate a claim.
        """
        if not model:
            return "Error: Gemini model is not configured."

        try:
            image_for_gemini = Image.open(io.BytesIO(image_bytes))
            # This is the multimodal prompt
            response = model.generate_content([
                "Analyze this image closely. Describe the primary subject, scene, and any text visible. Formulate this description into a single, concise factual claim.",
                image_for_gemini
            ])
            return response.text.strip()
        except Exception as e:
            print(f"An error occurred during image description: {e}")
            return f"Error describing image: {e}"

gemini_service_instance = GeminiService()
