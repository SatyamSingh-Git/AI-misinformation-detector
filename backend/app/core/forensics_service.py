# In backend/app/core/forensics_service.py
from PIL import Image
import io
import json

# Import the Gemini model instance from the gemini_service
from .gemini_service import model

class ForensicsService:
    """
    A sophisticated service for analyzing image authenticity using multiple techniques.
    """

    def _analyze_metadata(self, image: Image.Image) -> dict:
        """
        Analyzes the image's metadata (EXIF) for forensic clues.
        Real photos have EXIF data; AI images almost never do.
        """
        exif_data = image.info.get('exif')

        if exif_data:
            return {
                "has_exif": True,
                "flag": "Image contains EXIF metadata, a strong indicator of a real photograph from a camera."
            }
        else:
            return {
                "has_exif": False,
                "flag": "Image lacks EXIF metadata. This is highly common for AI-generated images or images that have been scrubbed of their original data."
            }

    def _analyze_with_gemini_vision(self, image: Image.Image) -> dict:
        """
        Uses Gemini's multimodal vision capabilities to perform deep visual reasoning.
        This is our "expert eye".
        """
        if not model:
            return {"error": "Gemini model not configured."}

        # This is a highly advanced prompt designed for forensic analysis.
        prompt = [
            """
            You are a world-class digital image forensics expert and meticulous auditor. Analyze the PROVIDED IMAGE for signs of AI generation or digital manipulation. Base EVERY claim on visible evidence; avoid speculation. If evidence is insufficient, choose "Indeterminate."

            Inspection checklist (cover each briefly, citing concrete cues you see):
            1) Lighting & Shadows: global light direction; shadow hardness vs. time-of-day; color of shadows; specular highlights; eye catchlights; reflections obeying incidence=reflection; occlusion consistency.
            2) Geometry & Perspective: horizon/vanishing points; lens distortion; parallax/occlusion; object boundaries; impossible joins; perspective of text/signage.
            3) Textures & Materials: skin pores/hair strands; fabric weave; wood grain; repetition/tiling; over-smoothing/denoising “plasticky” look; wormy diffusion artifacts; oversharpen/haloing; moiré.
            4) Biological Plausibility: hands/fingers/thumbs; ears/teeth/eyes; limb lengths/poses; jewelry and wear marks; glasses frames/contact between objects and skin.
            5) Background & Fine Print: coherence vs. collage; edge melt/feathering; duplicated motifs; signage/license plates/clocks (warping, gibberish, inconsistent fonts/kerning).
            6) Color/Tone & DoF: white balance uniformity; unnatural gradients/bloom/HDR halos; color bleeding; bokeh shape vs. aperture; depth mask errors (fringing around hair/fur).
            7) Edges/Compositing: matte halos; segmentation seams; unnatural micro-edges; inconsistencies at overlaps/transparencies (veils, smoke, glass).
            8) Compression/Noise/Metadata (visual only): noise distribution uniformity across regions/channels; block boundaries; double-JPEG hints; upscaler artifacts. If metadata unavailable, do not assume.
            9) Editing Tells: cloning/patch repeats; copy-move; resynthesis; mismatched sharpness/noise between regions; re-lighting inconsistencies.

            Output FORMAT RULES (must follow EXACTLY):
            - Return ONE single MINIFIED JSON object, no markdown, no code fences, no extra text.
            - Keys (exact order): verdict, confidence_score, reasoning.
            - verdict ∈ {"Likely AI-Generated","Likely Real Photograph","Indeterminate"}.
            - confidence_score ∈ [0.0,1.0] (float with up to 2 decimals).
            - reasoning: a concise, stepwise explanation referencing the checklist (e.g., "1)…; 2)…; …"). Max ~700 characters. No newlines.

            Scoring guidance (to avoid overconfidence):
            - +0.15–0.30 for multiple independent strong artifacts (e.g., inconsistent shadows + warped text + tiling).
            - +0.05–0.10 for each weak cue (e.g., mild smoothing) if several align.
            - Cap at ≤0.85 unless evidence is overwhelming; use 0.40–0.60 for mixed signals.
            - Use 0.20–0.35 and "Indeterminate" for low-res/obstructed images or when cues conflict.

            Edge cases:
            - If image is too small/heavily compressed/partially visible: return "Indeterminate" and state why in reasoning.
            - Do NOT include suggestions, questions, or extra keys. Do NOT mention tools or methods not directly visible in the pixels.

            Example (structure only; replace content with your findings):
            {"verdict":"Indeterminate","confidence_score":0.34,"reasoning":"1) Shadows plausible but soft vs. sun; 2) Perspective OK; 3) Skin slightly over-smoothed; 4) Hands plausible; 5) Background text mildly warped; 6) DoF consistent; 7) Minor edge halos near hair; 8) Uniform noise suggests upscaling. Mixed cues."}

            """,
            image
        ]

        try:
            response = model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_response)
            return result
        except Exception as e:
            print(f"Error during Gemini Vision analysis: {e}")
            return {"error": f"Gemini Vision analysis failed: {e}"}

    def analyze_image_authenticity(self, image_bytes: bytes, source_context: str) -> dict:
        """
        The main public method that orchestrates the full forensic analysis,
        now using the user-provided source context.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            return {"error": f"Could not open image file: {e}"}

        # --- Run all forensic analyses ---
        metadata_result = self._analyze_metadata(image)
        vision_result = self._analyze_with_gemini_vision(image)

        # --- CONTEXT-AWARE SYNTHESIS ---
        final_verdict = vision_result.get("verdict", "Error")
        explanation_parts = []

        if "reasoning" in vision_result:
            explanation_parts.append(vision_result["reasoning"])

        # New intelligent logic for metadata flag
        context_flag = ""
        has_exif = metadata_result["has_exif"]
        if source_context == 'camera' and not has_exif:
            context_flag = "The image lacks camera metadata (EXIF), which is unusual for a photo claimed to be directly from a camera. This is a suspicious sign."
        elif (source_context == 'downloaded' or source_context == 'messaging') and not has_exif:
            context_flag = "The image lacks camera metadata, which is normal and expected for images downloaded from the internet or sent via messaging apps."
        elif source_context == 'camera' and has_exif:
            context_flag = "The image contains camera metadata (EXIF), which strongly supports the claim that it is an original photograph."
        else: # Handle 'unknown' or other cases
            context_flag = metadata_result["flag"] # Use the original, neutral flag

        explanation_parts.append(context_flag)

        final_confidence = vision_result.get("confidence_score", 0.0)
        # Only penalize confidence if the context makes it suspicious
        if source_context == 'camera' and not has_exif:
             final_confidence = max(0.3, final_confidence * 0.6) # Penalize heavily
             explanation_parts.append("Confidence was significantly reduced due to the mismatch between the stated source and the image's metadata.")

        return {
            "verdict": final_verdict,
            "confidence": final_confidence,
            "full_explanation": " ".join(explanation_parts),
            "metadata_analysis": metadata_result,
            "visual_analysis": vision_result,
        }

# Create a single, reusable instance
forensics_service_instance = ForensicsService()
