# AI Misinformation Detector
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Models](https://img.shields.io/badge/Models-Gemini%20%7C%20CLIP%20%7C%20GNN-orange.svg)](#)

A revolutionary, production-ready multimodal AI system that treats misinformation detection like digital forensics. It goes far beyond simple classification by gathering evidence from multiple independent sources—including text, images, metadata, and social networks—to provide transparent, actionable intelligence.

- **Detects and Explains**: Identifies likely misinformation, assigns confidence scores, and provides a detailed, evidence-based explanation for its verdict.
- **Forensic & Multimodal**: Fuses a 6-layer forensic evidence pipeline with an expert consensus architecture, combining specialist models (Deepfake, CLIP, GNNs) with Google's Gemini 2.5 Flash.
- **Production Ready**: Built with a scalable FastAPI backend, Docker support, and a comprehensive testing suite designed for real-world deployment.

---

## Table of contents
- [Demo](#demo)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Requirements](#requirements)
  - [Install](#install)
  - [Run the Application](#run-the-application)
- [Usage](#usage)
  - [API Endpoints](#api-endpoints)
  - [Python Inference Example](#python-inference-example)
- [Data & Training](#data--training)
- [Evaluation & Performance](#evaluation--performance)
- [Responsible AI & Limitations](#responsible-ai--limitations)
- [Contributing](#contributing)
- [Citation](#citation)
- [License & Contact](#license--contact)
- [Acknowledgements](#acknowledgements)

---

## Demo
Here is a sample output for a suspicious news article with a misleading image:
![demo-placeholder](frontend/demo-placeholder1.png)

![demo-placeholder](frontend/demo-placeholder2.png)

![demo-placeholder](frontend/demo-placeholder3.png)

```json
{
  "verdict": "Likely Misleading",
  "confidence_score": 0.82,
  "explanation": "The claim in the text is unsubstantiated and uses emotionally charged language. The associated image is authentic but is being used in a misleading context, as its semantic content does not align with the article's claims.",
  "correction": "The event described in the image occurred in a different location and context five years prior.",
  "sources": ["https://credible-fact-check-source.com/original-event"],
  "linguistic_analysis": {
    "sentiment": "NEGATIVE",
    "confidence": 0.91,
    "reasoning": "Detected emotionally manipulative language and logical fallacies."
  },
  "image_authenticity": {
    "specialist_verdict": "Likely Authentic",
    "gemini_verdict": "No signs of digital manipulation detected.",
    "consensus": "High probability the image is authentic but contextually misused."
  },
  "image_analysis": {
    "coherence_score": 0.25,
    "description": "Low semantic similarity between the image content (a protest) and the text content (a political policy debate)."
  }
}
```

---

## Features
- **Forensic Evidence Pipeline**: A multi-layered analysis combining 6 specialized AI models for robust, evidence-based detection.
- **Expert Consensus Architecture**: Fuses specialist detectors (Deepfake, Sentiment) with the broad reasoning capabilities of Google's Gemini 2.5 Flash.
- **Multi-Modal Reasoning**: Simultaneously analyzes text, images, metadata, and social network propagation patterns.
- **Explainable Intelligence**: Delivers step-by-step reasoning, confidence scores, and source attribution for full transparency.
- **Real-time Cross-Verification**: Integrates with Google's Fact Check API and ClaimReview database to validate against professional fact-checks.
- **Graph Neural Networks (GNNs)**: Employs GraphSAGE for advanced social propagation pattern detection and influence mapping.
- **Cross-Modal Coherence**: Uses OpenAI's CLIP to verify semantic consistency between images and text, detecting out-of-context media.
- **Production-Ready & Scalable**: Built on an async FastAPI backend with Docker support, capable of handling 100+ concurrent requests.

---

## Architecture
Our system is designed with a modular, scalable microservice-style architecture.

### System Architecture Overview
This diagram shows the complete flow from the user-facing applications through the API gateway to the various AI services and data layers.
```mermaid
graph TB
    subgraph "Frontend Layer"
        WEB[🌐 React Web App]
        EXT[🔧 Chrome Extension]
    end
    subgraph "API Gateway Layer"
        FASTAPI[⚡ FastAPI Server]
    end
    subgraph "Core Business Logic"
        ORCHESTRATOR[🎯 Analysis Orchestrator]
    end
    subgraph "AI Analysis Services"
        GEMINI_SVC[🧠 Gemini Service]
        FORENSICS_SVC[🔍 Forensics Service]
        SPECIALIST_SVC[🎯 Specialist Models]
        GNN_SVC[🕸️ GNN Service]
    end
    subgraph "External AI Models"
        GEMINI[🚀 Google Gemini 2.5 Flash]
        HF_MODELS[🤗 Hugging Face Models]
    end
    subgraph "Storage Layer"
        DB[🗄️ SQLite Database]
        MODELS[💾 Model Storage]
    end

    WEB & EXT --> FASTAPI --> ORCHESTRATOR
    ORCHESTRATOR --> GEMINI_SVC & FORENSICS_SVC & SPECIALIST_SVC & GNN_SVC
    GEMINI_SVC --> GEMINI
    FORENSICS_SVC --> GEMINI & HF_MODELS
    SPECIALIST_SVC --> HF_MODELS
    GNN_SVC --> MODELS
    ORCHESTRATOR --> DB
```

### Detailed Analysis Pipeline Flow
This sequence diagram illustrates the parallel execution of the analysis services.
```mermaid
sequenceDiagram
    participant User
    participant WebApp
    participant API
    participant Orchestrator
    participant AI Services

    User->>WebApp: Submit content (text/image/URL)
    WebApp->>API: POST /api/v1/analyze
    API->>Orchestrator: Initialize analysis
    par Parallel Analysis
        Orchestrator->>AI Services: Fact-check text (Gemini)
        Orchestrator->>AI Services: Analyze image authenticity (Forensics)
        Orchestrator->>AI Services: Check image-text coherence (CLIP)
        Orchestrator->>AI Services: Analyze network patterns (GNN)
    end
    AI Services-->>Orchestrator: Return evidence fragments
    Orchestrator->>Orchestrator: Synthesize multi-modal results
    Orchestrator-->>API: Return comprehensive report
    API-->>WebApp: Display results
```

---

## Quick Start

### Requirements
- Python 3.8+
- Node.js v16+
- Git
- A Google Gemini API Key

### Install
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ai-misinformation-detector.git
    cd ai-misinformation-detector
    ```

2.  **Set up the Backend:**
    ```bash
    cd backend
    python -m venv venv
    # Activate the virtual environment
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    # source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure API Keys:**
    Create a file named `.env` inside the `backend` directory and add your API key:
    ```env
    GOOGLE_API_KEY="your_gemini_api_key_here"
    DATABASE_URL="sqlite:///./misinformation.db"
    ```

4.  **Set up the Frontend:**
    ```bash
    cd ../frontend
    npm install
    ```

### Run the Application
You will need two separate terminals to run the backend and frontend servers.

1.  **Run the Backend Server (Terminal 1):**
    ```bash
    cd backend
    # Make sure your virtual environment is activated
    uvicorn app.main:app --reload
    ```
    The backend will be available at `http://127.0.0.1:8000`.

2.  **Run the Frontend App (Terminal 2):**
    ```bash
    cd frontend
    npm start
    ```
    The React application will open at `http://localhost:3000`.

---

## Usage

### API Endpoints
The core functionality is exposed via a REST API. You can see interactive documentation by navigating to `http://127.0.0.1:8000/docs` while the backend is running.

**Analyze Content**
- `POST /api/v1/analyze`
- **Content-Type**: `multipart/form-data`
- **Fields**: `text` (str), `image_url` (str), `image_file` (file)

**Submit Feedback**
- `POST /api/v1/vote`
- **Content-Type**: `application/json`
- **Body**: `{"url": "article_url", "vote": "trustworthy"}`

### Python Inference Example
You can interact with the running API using a simple Python script.

```python
import requests

# Example with text and an image URL
api_url = "http://127.0.0.1:8000/api/v1/analyze"
data = {
    "text": "Scientists discover that chocolate cures all diseases, study finds.",
    "image_url": "https://example.com/misleading-image.jpg"
}

response = requests.post(api_url, data=data)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}", response.text)
```

---

## Data & Training
The models are trained on a variety of public and proprietary datasets.

- **Supported Datasets**: LIAR-PLUS, FakeNewsNet, and the Kaggle "Fake and real news" dataset (`True.csv`, `Fake.csv`) are used for the text classifier.
- **Training Scripts**: The `backend/ml/training_scripts/` directory contains the scripts for training the text authenticity models (e.g., `train_text_model.py`).
- **Custom Training**: To train a model, run the script from the `backend` directory:
  ```bash
  # Ensure venv is active
  python ml/training_scripts/train_text_model.py
  ```

---

## Evaluation & Performance
- **Accuracy**: The core text classifier achieves **85%+ accuracy** on standard misinformation benchmarks.
- **Analysis Speed**: A full multimodal analysis (text + image) completes in **under 5 seconds**.
- **Scalability**: The async backend is capable of handling **100+ concurrent requests** on appropriate hardware.
- **Evaluation**: The `evaluate.py` script can be used to measure model performance on a held-out test set, reporting Precision, Recall, F1-score, and ROC-AUC.

---

## Responsible AI & Limitations
- **Not an Oracle**: This tool is designed to assist human analysis, not replace it. False positives and negatives are possible.
- **Model Bias**: Models are trained on public data and may reflect existing societal, demographic, or topical biases.
- **High-Stakes Decisions**: Do not use the automated output for high-stakes decisions without human review. The goal is to provide evidence, not a final judgment.
- **Transparency**: We are committed to transparency. The system provides explanations and confidence scores to help users understand the basis for its conclusions.

---

## Contributing
Contributions are welcome! Please follow this workflow:
1.  Open an issue to discuss major changes.
2.  Create a feature branch: `git checkout -b feat/your-awesome-feature`
3.  Commit your changes with clear messages and add tests.
4.  Open a pull request referencing the issue.

Please follow PEP 8 for code style and add unit tests for new functionality. You can run all backend tests with `pytest`.

---

## Citation
If you use this project in your research or work, please cite it as follows:

```bibtex
@misc{ai-misinformation-detector-2025,
  author = {Your Name/Organization and Contributors},
  title = {AI Misinformation Detector: A Multimodal Forensic Analysis Toolkit},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/your-username/ai-misinformation-detector}}
}
```

---

## License & Contact
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

For questions, feature requests, or security issues, please open an issue on GitHub.

---

## Acknowledgements
- The [Google AI](https://ai.google.dev/) team for the Gemini models.
- The [Hugging Face](https://huggingface.co/) community for the open-source models and `transformers` library.
- The open-source research community for providing the foundational datasets and tools that made this project possible.
