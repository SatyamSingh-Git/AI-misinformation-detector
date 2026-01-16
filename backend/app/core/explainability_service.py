from typing import Optional, Dict

class ExplainabilityService:
    """
    A service to generate human-readable explanations for AI-driven credibility scores.

    For a hackathon, this uses a fast and effective rule-based approach instead of
    computationally expensive methods like SHAP or LIME.
    """

    def generate_explanation(
        self,
        text_analysis_result: Dict,
        image_analysis_result: Optional[Dict]
    ) -> str:
        """
        Constructs an explanation string from the analysis result dictionaries.

        Args:
            text_analysis_result: The dictionary output from the text analysis module.
            image_analysis_result: The dictionary output from the image analysis module.

        Returns:
            A consolidated, human-readable explanation string.
        """
        explanations = []

        # Add explanation from the text analysis
        if 'flag' in text_analysis_result:
            explanations.append(text_analysis_result['flag'])

        # Add explanation from the image-text match analysis
        if image_analysis_result and 'flag' in image_analysis_result:
            explanations.append(image_analysis_result['flag'])

        # Add explanation for source credibility (currently a placeholder)
        explanations.append("Source credibility could not be verified at this time.")

        if not explanations:
            return "No specific flags were raised during the analysis."

        return " ".join(explanations)

# Create a single, reusable instance of the service.
explainability_service_instance = ExplainabilityService()
