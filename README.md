# InkFlow AI — Blog Writing Agent

An AI-powered blog writing application that researches topics, plans blog structure, generates content, and helps users edit and export their blogs.

## Features

- AI-powered blog generation
- Web research with Tavily
- LangGraph-based writing workflow
- Parallel section writing
- Source verification and proofreading
- Live generation progress
- Edit and regenerate blog content
- Markdown, PDF, and DOCX export
- Responsive frontend

## Tech Stack

- Python
- FastAPI
- LangGraph
- Google Gemini
- Tavily Search
- HTML, CSS, JavaScript

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/atulsahu003/InkFlow-AI-Blog-Writer.git
cd InkFlow-AI-Blog-Writer
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add your own API keys using the variable names expected by the application.

Never upload your `.env` file or share your API keys publicly.

### 5. Start the backend

```bash
uvicorn backend.main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

### 6. Open the frontend

Open `frontend/index.html` using the VS Code Live Server extension.

## Security

API keys and local virtual environment files are excluded using `.gitignore`.

## License

No license has been specified yet.