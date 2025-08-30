misinformation-detector/
├── .vscode/                  # VS Code workspace settings
│   ├── extensions.json       # Recommends extensions for the team
│   └── settings.json         # Shared workspace settings (e.g., formatters)
│
├── backend/                  # Python backend (Flask or FastAPI)
│   ├── app/                  # Main application source code
│   │   ├── __init__.py
│   │   ├── api/              # API endpoints/routes
│   │   │   ├── __init__.py
│   │   │   ├── analysis_routes.py  # Endpoint for /analyze
│   │   │   └── feedback_routes.py  # Endpoint for /vote
│   │   ├── core/             # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py # Logic for text/image analysis
│   │   │   └── explainability_service.py # Logic for SHAP/LIME
│   │   ├── models/           # Database models (if using an ORM)
│   │   │   └── vote.py
│   │   ├── main.py             # Application entry point (starts the server)
        ├── database.py
│   │   └── config.py         # Configuration settings
│   │
│   ├── notebooks/              # Jupyter notebooks for model experimentation
│   │   └── model_prototyping.ipynb
│   │
│   ├── tests/                # Unit and integration tests
│   │   └── test_api.py
│   │
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # To containerize the backend
│
├── frontend/                 # React web application (for pasting links)
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/              # Functions for calling the backend
│   │   │   └── apiClient.js
│   │   ├── components/       # Reusable UI components
│   │   │   ├── UrlInput.js
│   │   │   ├── ResultsDisplay.js
│   │   │   └── Loader.js
│   │   ├── App.js            # Main application component
│   │   └── index.js          # React app entry point
│   ├── .env                  # Environment variables (e.g., API URL)
│   └── package.json          # Node.js dependencies
│
├── extension/                # Chrome browser extension
│   ├── public/
│   │   ├── manifest.json     # *** The core manifest file for the extension ***
│   │   ├── index.html        # The HTML for the popup window
│   │   └── icons/            # Icons for the browser toolbar
│   │       ├── icon16.png
│   │       └── icon48.png
│   ├── src/
│   │   ├── App.js            # Main React component for the popup UI
│   │   ├── index.js          # Entry point for the popup
│   │   ├── background.js     # Service worker: handles background tasks
│   │   └── contentScript.js  # Injected into web pages to read content
│   └── package.json          # Node.js dependencies
│
├── .gitignore                # Files and folders to ignore in Git
├── docker-compose.yml        # To easily run the backend and database together
└── README.md                 # Project overview, setup, and run instructions

An advanced, multimodal AI tool designed to analyze and verify content credibility. This application goes beyond simple "fake news" scores, providing users with a detailed forensic breakdown of text and images to foster media literacy and combat misinformation.

✨ Key FeaturesMultimodal
Analysis: Accepts text, image URLs, or direct image uploads for a comprehensive analysis.Gemini-Powered Fact-Checking: Leverages Google's Gemini 1.5 Flash model to perform deep factual verification, provide corrections, and enrich content with critical context.AI Image Forensics: Employs a multi-layered approach to detect AI-generated images by analyzing metadata and using Gemini's advanced visual reasoning to spot subtle artifacts.Linguistic & Coherence Analysis: Uses specialized models to detect sensationalized language and verify if an article's text semantically matches its imagery.Explainable & Sourced Results: Presents a detailed breakdown of its findings, including a confidence score, a step-by-step explanation, and links to credible sources to build user trust.Professional Dashboard UI: Features a responsive, side-by-side layout for an intuitive and efficient user experience on all devices.Browser Extension: A fully integrated Chrome extension for real-time analysis directly in the user's workflow.🛠️ Tech Stack & ArchitectureThis project is a full-stack monorepo with three main components: a Python backend, a React web app, and a React-based browser extension.ComponentTechnologyPurposeBackendFastAPI (Python)High-performance API for handling requests and orchestrating AI services.Web AppReact.js (JavaScript)The main user-facing dashboard for content submission and analysis.ExtensionReact.js & Manifest V3For in-browser, real-time analysis of active web pages.AI/MLGoogle Gemini 1.5 FlashThe core reasoning engine for fact-checking, visual forensics, and enrichment.Hugging Face TransformersFor specialized tasks like sentiment analysis (detecting emotive language).OpenAI CLIPFor measuring the semantic similarity between images and text.DatabaseSQLAlchemy & SQLite/PostgreSQLFor storing crowdsourced feedback and other potential data.ContainerDocker & Docker ComposeFor creating a portable, production-ready development environment.🌊 Flow of Information & DataThe application follows a clear, orchestrated flow from user input to final analysis, designed for robustness and clarity. code Mermaiddownloadcontent_copyexpand_less    graph TD
    subgraph User Interface
        A[React Web App]
        B[Chrome Extension]
    end

    subgraph User Input
        C[Text Content]
        D[Image URL]
        E[Image File Upload]
    end

    subgraph FastAPI Backend
        F[API Endpoint /analyze]
        G[AnalysisService Orchestrator]
        H[ForensicsService]
        I[GeminiService]
        J[Sentiment & CLIP Models]
    end

    subgraph External AI Models
        K[Google Gemini API]
        L[Hugging Face Models]
    end

    A -- "Text, URL, or File" --> F
    B -- "Scraped Text & URL" --> F
    C --> A
    D --> A
    E --> A

    F -- "Request Data" --> G
    G -- "Image Bytes" --> H
    G -- "Text/Claim" --> I
    G -- "Text/Image" --> J

    H -- "Visual Reasoning Prompt" --> K
    I -- "Fact-Check & Enrichment Prompt" --> K
    J -- "Linguistic Analysis" --> L

    K -- "Rich JSON Response" --> H & I
    L -- "Sentiment Score" --> J

    H & I & J -- "Synthesized Results" --> G
    G -- "Final Rich Payload (JSON)" --> F
    F -- "200 OK" --> A & B

    A -- "Renders Professional UI" --> User
    B -- "Renders Popup UI" --> User
  🧠 Core Concepts, Strategies, and IdeasThis tool was built on several core principles to make it more effective and trustworthy than a simple classifier.Beyond a Single Score: We intentionally moved away from a single "credibility score" early on. A number is meaningless without context. The goal is to provide a verdict with evidence, empowering the user to make their own informed decision.Multi-Layered Forensic Analysis: We treat misinformation detection like a digital forensics investigation. Instead of relying on one signal, we gather evidence from multiple, independent layers:Factual Layer (Gemini): Is the core claim true?Visual Layer (Gemini Vision): Does this image make sense physically and logically?Metadata Layer (Pillow): Does the image have the digital "fingerprints" of a real camera?Linguistic Layer (Transformers): Is the language designed to manipulate emotions?Coherence Layer (CLIP): Is the image being used in the correct context?LLM as a Reasoning Engine, Not Just a Knowledge Base: Our "super-prompt" for Gemini is the heart of the engine. We don't just ask it "is this true?". We instruct it to act as a Trust & Safety analyst, forcing it to provide a verdict, reasoning, corrections, and sources in a structured format. This makes the output reliable and easy to parse.Graceful Degradation: The system is designed to be robust. If a particular analysis fails (e.g., an image URL is broken), it can still provide results from the other successful analyses, rather than crashing entirely.🤖 AI Models UsedModelSourceRole(s)Gemini 1.5 FlashGoogle AI1. Fact-Checking & Correction: Verifies claims against its vast knowledge base. <br> 2. Contextual Enrichment: Provides additional relevant information. <br> 3. Image-to-Text: Describes images to create a claim for image-only analysis. <br> 4. Visual Forensic Reasoning: Acts as an expert eye to spot signs of AI generation.distilbert-base...Hugging FaceSentiment Analysis: A lightweight but effective model used to detect strong negative sentiment, a common indicator of emotionally manipulative or biased language.openai/clip-vit...Hugging FaceImage-Text Coherence: Measures the semantic similarity between an image and a piece of text to detect if an image is being used out of context.🚀 Getting Started: Setup and InstallationFollow these steps to get the entire project running on your local machine.PrerequisitesPython 3.8+Node.js v16+ and npmDocker and Docker Compose (Recommended for database)A Google Gemini API Key from Google AI Studio.1. Clone the Repository code Bashdownloadcontent_copyexpand_lessIGNORE_WHEN_COPYING_STARTIGNORE_WHEN_COPYING_END    git clone <your-repository-url>
cd misinformation-detector
  2. Backend Setup code Bashdownloadcontent_copyexpand_lessIGNORE_WHEN_COPYING_STARTIGNORE_WHEN_COPYING_END    # Navigate to the backend directory
cd backend

# Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt

# Create a .env file for your API key
# Create a new file named .env in the `backend/` directory and add your key:
echo "GOOGLE_API_KEY='YOUR_GEMINI_API_KEY_HERE'" > .env
  3. Frontend Setup code Bashdownloadcontent_copyexpand_lessIGNORE_WHEN_COPYING_STARTIGNORE_WHEN_COPYING_END    # Navigate to the frontend directory from the root
cd frontend

# Install all Node.js dependencies
npm install

# The frontend uses a .env file to know the backend's address.
# This is already configured correctly in the provided files.
  4. Running the ApplicationYou will need three separate terminals running simultaneously.Terminal 1: Start the Backend code Bashdownloadcontent_copyexpand_lessIGNORE_WHEN_COPYING_STARTIGNORE_WHEN_COPYING_END    cd backend
source venv/bin/activate
uvicorn app.main:app --reload
# The API will be running at http://127.0.0.1:8000
  Terminal 2: Start the Frontend Web App code Bashdownloadcontent_copyexpand_lessIGNORE_WHEN_COPYING_STARTIGNORE_WHEN_COPYING_END    cd frontend
npm start
# The web app will open at http://localhost:3000
  Terminal 3: Build the Chrome ExtensionThe extension is not "run" but "built". code Bashdownloadcontent_copyexpand_lessIGNORE_WHEN_COPYING_STARTIGNORE_WHEN_COPYING_END    cd extension
npm install # If you haven't already
npm run build
# This will create a `build` folder inside `extension/`
  5. Loading the Chrome ExtensionOpen Google Chrome and navigate to chrome://extensions.Enable "Developer mode" in the top-right corner.Click "Load unpacked".Select the misinformation-detector/extension/build folder.The extension will appear, and you can pin it to your toolbar.🗺️ Future RoadmapVideo & Audio Analysis: Integrate models to detect deepfake videos and cloned voices.Source Credibility Database: Build a historical database to track the reliability of news domains over time.Browser-Side AI: Utilize WebML to run lighter models (like sentiment analysis) directly in the browser for enhanced privacy and speed.Integration with Perplexity API: Add Perplexity as an alternative or supplementary reasoning engine for sourced answers.📄 LicenseThis project is licensed under the MIT License. See the LICENSE file for details.🙏 AcknowledgementsThe teams at Google for the powerful Gemini models.Hugging Face for democratizing access to state-of-the-art NLP models.The open-source community for the incredible tools that made this project possible.
