from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import settings and database components
from .config import get_settings
from .database import engine
from .models import vote # Import the vote model to ensure its table is created

# Import the API routers from the 'api' directory
from .api import analysis_routes, feedback_routes

# --- Database Table Creation ---
# This line is crucial. It tells SQLAlchemy to create the database tables
# defined in your models (e.g., the 'votes' table) if they don't already exist.
# This is executed once when the application starts up.
vote.Base.metadata.create_all(bind=engine)

# Get the application settings
settings = get_settings()

# --- FastAPI Application Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- CORS (Cross-Origin Resource Sharing) Middleware ---
# This is essential for allowing your frontend (web app, browser extension)
# to communicate with this backend API. Without it, browsers would block requests.
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"], # Allow all methods (GET, POST, etc.)
        allow_headers=["*"], # Allow all headers
    )

# --- Include API Routers ---
# This adds the endpoints defined in your route files to the main application.
# The prefix makes all routes in that file start with, e.g., /api/v1/analyze
app.include_router(analysis_routes.router, prefix=settings.API_V1_STR, tags=["Analysis"])
app.include_router(feedback_routes.router, prefix=settings.API_V1_STR, tags=["Feedback"])


# --- Root Endpoint ---
# A simple endpoint to check if the API is running.
@app.get("/", tags=["Root"])
async def read_root():
    """
    A health check endpoint to confirm the API is alive.
    """
    return {"status": "ok", "message": f"Welcome to the {settings.PROJECT_NAME}"}
