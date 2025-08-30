# In backend/app/core/gemini_service.py
import google.generativeai as genai
import json
from ..config import get_settings
from PIL import Image
import io

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
    def _create_super_prompt(self, claim: str) -> str:
        """
        A sophisticated prompt that asks for a full analysis, enrichment, and sources.
        """
        return f"""
        You are a world-class Trust & Safety analysis engine. Your task is to analyze a given claim for factual accuracy, provide context, and cite credible sources.

        Analyze this claim: "{claim}"

        Your response MUST be a single, minified JSON object with the following schema. Do not include any text before or after the JSON object.

        {{
          "verdict": "A short, definitive verdict. Choose one of: 'Factually Correct', 'Factually Incorrect', 'Misleading', 'Lacks Context'.",
          "confidence_score": "A float from 0.0 to 1.0 representing your confidence in the verdict.",
          "explanation": "A detailed but concise explanation of your reasoning. Explain WHY the claim is correct or incorrect. If it's misleading, explain what nuance is missing.",
          "correction": "If the verdict is 'Factually Incorrect' or 'Misleading', provide the corrected information. Otherwise, this should be null.",
          "enrichment": "An array of 2-3 strings. Each string is an additional, interesting, and verifiable fact that provides more context about the main subjects of the claim. This should be provided even if the claim is correct.",
          "sources": "An array of 2-3 URL strings from highly credible, publicly available sources that a user can visit to verify the information (e.g., Wikipedia, Reuters, BBC, Britannica, major scientific journals)."
        }}
        """

    def verify_claim(self, claim: str) -> dict:
        if not model:
            return {"error": "Gemini model is not configured."}
        if not claim or not claim.strip():
            return {"error": "Claim cannot be empty."}

        try:
            prompt = self._create_super_prompt(claim)
            response = model.generate_content(prompt)

            cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_response)
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
