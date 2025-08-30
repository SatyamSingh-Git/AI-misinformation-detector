from fastapi.testclient import TestClient
from unittest.mock import patch

# Import the main FastAPI app instance from your main.py
from app.main import app

# The TestClient allows you to make requests to your FastAPI application in your tests
client = TestClient(app)

def test_read_root():
    """
    Test the health check endpoint '/'.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# The @patch decorator temporarily replaces the real AI service with a mock object.
# This makes the test fast and independent of the actual model's behavior.
@patch("app.api.analysis_routes.analysis_service_instance")
def test_analyze_content_success(mock_analysis_service):
    """
    Test a successful request to the /analyze endpoint.
    """
    # Configure the mock to return a predictable result
    mock_result = {
        "credibility_score": 0.55,
        "explanation": "Mocked explanation.",
        "image_text_match": True,
        "source_rating": "Mocked"
    }
    mock_analysis_service.analyze_content.return_value = mock_result

    # Make the API request
    response = client.post(
        "/api/v1/analyze",
        json={"text": "This is a test article.", "image_url": "http://example.com/image.jpg"}
    )

    # Assert the results
    assert response.status_code == 200
    assert response.json() == mock_result
    # Verify that our mock service was called correctly
    mock_analysis_service.analyze_content.assert_called_once_with(
        text="This is a test article.",
        image_url="http://example.com/image.jpg"
    )

def test_analyze_content_missing_data():
    """
    Test a request to /analyze with invalid data (missing the 'text' field).
    """
    response = client.post("/api/v1/analyze", json={"image_url": "http://example.com/image.jpg"})

    assert response.status_code == 422 # 422 Unprocessable Entity is FastAPI's validation error
    assert "field required" in response.text

def test_submit_feedback_success():
    """
    Test a successful request to the /vote endpoint.
    Note: This test does not check the database, only that the API responds correctly.
    """
    response = client.post(
        "/api/v1/vote",
        json={"url": "http://example.com/article", "vote": "trustworthy"}
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert "recorded successfully" in json_response["message"]

def test_submit_feedback_invalid_vote_type():
    """
    Test submitting a vote with an invalid vote type.
    """
    response = client.post(
        "/api/v1/vote",
        json={"url": "http://example.com/article", "vote": "definitely_fake"} # not a valid VoteType
    )

    assert response.status_code == 422
    assert "unexpected value" in response.text
