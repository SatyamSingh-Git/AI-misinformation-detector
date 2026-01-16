# AI vs Human Image Detector Integration

## Overview
The project now uses a fine-tuned SigLIP model to detect whether uploaded images are AI-generated or real photographs. This model is located in the `ai-vs-human-image-detector/` directory and has been integrated into the backend analysis pipeline.

## Model Details
- **Architecture**: SigLIP (fine-tuned for image classification)
- **Training**: 60,000 AI-generated + 60,000 human images
- **Accuracy**: 99.23% on test set
- **Labels**: 
  - 0 = "ai" (AI-Generated)
  - 1 = "hum" (Human-Created)

## Changes Made

### 1. Backend Analysis Service (`backend/app/core/analysis_service.py`)
- **Updated Model Loading**: Changed from remote `umm-maybe/AI-image-detector` to local model at `/app/ai-vs-human-image-detector`
- **Model Path**: Uses the local fine-tuned SigLIP model included in the project

### 2. Forensics Service (`backend/app/core/forensics_service.py`)
- **New Method**: `_analyze_with_ai_detector()` - Classifies images using the SigLIP model
- **Enhanced Analysis**: AI detector results are now the primary source of truth for image authenticity
- **Confidence Scoring**: Returns probabilities for both AI and Human classifications
- **Multi-layered Approach**: Combines:
  1. AI detector model classification (primary)
  2. Gemini Vision analysis (secondary visual reasoning)
  3. EXIF metadata analysis (context-aware)

### 3. Docker Configuration
- **Dockerfile** (`backend/Dockerfile`): 
  - Updated COPY commands to account for new build context
  - Copies `ai-vs-human-image-detector/` model into container at `/app/ai-vs-human-image-detector`
  
- **docker-compose.yml**:
  - Changed build context from `./backend` to `.` (root directory)
  - Specified dockerfile path as `backend/Dockerfile`
  - Fixed port mapping: 8000 (host) → 8080 (container)

### 4. Dependencies
The following packages in `requirements.txt` support the AI detector:
- `torch` - PyTorch framework
- `transformers` - Hugging Face Transformers library
- `Pillow` - Image processing
- `timm` - Additional vision models support

## How It Works

### Image Analysis Flow
1. **Image Upload**: User uploads an image (or provides URL)
2. **AI Detection**: SigLIP model classifies image as AI-generated or human-created
3. **Confidence Scoring**: Model returns probability scores for both classes
4. **Visual Analysis**: Gemini Vision provides additional forensic reasoning
5. **Metadata Check**: EXIF data is analyzed with context awareness
6. **Final Verdict**: Results are synthesized with explanations

### API Response Structure
```json
{
  "verdict": "Likely AI-Generated" | "Likely Real Photograph",
  "confidence": 0.95,
  "full_explanation": "AI Detection Model: AI-Generated with 95.0% confidence...",
  "ai_detector_analysis": {
    "classification": "AI-Generated",
    "confidence": 0.95,
    "is_ai_generated": true,
    "probabilities": {
      "ai": 0.95,
      "human": 0.05
    }
  },
  "metadata_analysis": { ... },
  "visual_analysis": { ... }
}
```

## Building and Running

### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# The backend will be available at http://localhost:8000
```

### Local Development
If running locally without Docker:
1. Ensure Python 3.10+ is installed
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Update model path in code from `/app/ai-vs-human-image-detector` to `./ai-vs-human-image-detector`
4. Run: `uvicorn app.main:app --reload`

## Model Performance
- **Test Accuracy**: 99.23%
- **Test Loss**: 0.055
- **Inference Speed**: ~212 samples/second on evaluation
- **Note**: Some users have reported overfitting on certain image types

## Future Improvements
1. Add ensemble methods combining multiple models
2. Implement A/B testing between different detector models
3. Add adversarial attack detection
4. Fine-tune on domain-specific datasets
5. Add model versioning and rollback capabilities

## Troubleshooting

### Model Loading Errors
- Ensure the `ai-vs-human-image-detector/` directory contains all model files
- Check that `model.safetensors`, `config.json`, and `preprocessor_config.json` are present

### Memory Issues
- The SigLIP model requires ~2GB RAM
- Ensure Docker container has sufficient memory allocated

### Path Issues
- In Docker: Model path is `/app/ai-vs-human-image-detector`
- In local dev: Model path is `./ai-vs-human-image-detector` or absolute path
