from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from enum import Enum

# Create an API router
router = APIRouter()

# --- Pydantic Models for Data Validation ---

class VoteType(str, Enum):
    """
    Enumeration for the possible vote types.
    Using an Enum ensures that only valid votes are submitted.
    """
    TRUSTWORTHY = "trustworthy"
    MISLEADING = "misleading"
    NOT_SURE = "not_sure"

class FeedbackRequest(BaseModel):
    """
    Defines the shape of the request body for the /vote endpoint.
    """
    url: str = Field(..., description="The URL of the article being voted on.")
    vote: VoteType = Field(..., description="The user's credibility vote.")

class FeedbackResponse(BaseModel):
    """
    Defines the shape of a successful feedback submission response.
    """
    status: str = "success"
    message: str = Field(..., example="Your feedback has been recorded. Thank you!")


# --- API Endpoint ---

@router.post("/vote", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Receives a user's vote on a piece of content.

    This is a placeholder. In a real application, this would save the
    vote to a PostgreSQL database.
    """
    if not request.url:
        raise HTTPException(status_code=400, detail="URL must be provided.")

    # --- MOCK DATABASE LOGIC ---
    # In a real application, you would connect to your database (e.g., PostgreSQL)
    # and store the vote associated with the URL.
    print(f"Received vote for URL: {request.url}")
    print(f"Vote Type: {request.vote.value}")
    # --- END MOCK LOGIC ---

    return FeedbackResponse(
        message=f"Feedback '{request.vote.value}' for {request.url} recorded successfully."
    )
