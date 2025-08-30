# In backend/app/api/analysis_routes.py

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Any

# Import the service instance from the core logic directory
from ..core.analysis_service import analysis_service_instance, AnalysisService

# Create a new router for this part of the API
router = APIRouter()

# --- Pydantic Models ---
# These models define the "data contract" for our API.
# They ensure that incoming data is valid and outgoing data has the correct shape.

class AnalysisRequest(BaseModel):
    """
    The shape of the incoming request from the frontend.
    Pydantic will automatically validate that requests have a 'text' field.
    """
    text: str = Field(..., description="The main text content of the article.")
    image_url: Optional[str] = Field(None, description="The optional URL of the main image.")


class AnalysisResponse(BaseModel):
    verdict: str
    confidence_score: float
    explanation: str
    correction: Optional[str] = None
    enrichment: List[str]
    sources: List[str]
    linguistic_analysis: Optional[Any] = None
    image_analysis: Optional[Any] = None
    image_authenticity: Optional[Any] = None # Add the new field


# --- Dependency Injection ---
# This is a best practice in FastAPI. It makes our code more testable by
# allowing us to easily "inject" a different service during tests.
def get_analysis_service():
    """Provides a singleton instance of the AnalysisService."""
    return analysis_service_instance


# --- API Endpoint ---
# This defines the actual web endpoint that the frontend will call.

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(
    service: AnalysisService = Depends(get_analysis_service),
    text: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    image_source_context: Optional[str] = Form(None)
):
    """
    Accepts text, an image URL, or a direct image upload for analysis.
    """
    if not text and not image_file and not image_url:
        raise HTTPException(status_code=400, detail="Please provide text, an image URL, or upload an image file.")

    image_bytes = await image_file.read() if image_file else None

    try:
        analysis_result = await service.analyze_content(
        text=text,
        image_bytes=image_bytes,
        image_url=image_url,
        image_source_context=image_source_context # <--- CORRECTED
        )
        return analysis_result
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
