# InkFlow AI — Intelligent Blog Writing Agent ✍️

An AI-powered blog writing platform that transforms ideas into well-structured, research-backed blog articles. Built with FastAPI, LangGraph, Google Gemini, and Tavily, InkFlow AI automates research, content planning, writing, and proofreading through an intelligent multi-step workflow.

Users can generate, edit, regenerate, save, manage, and export their blogs through a modern web interface.

## ✨ Key Features

### AI-Powered Blog Generation
- Generate structured blog articles from a simple topic.
- Research topics using Tavily Search.
- Create blog outlines and writing plans.
- Generate content using Google Gemini.
- Parallel section writing through the LangGraph workflow.
- Proofreading and source verification.

### User Authentication & Blog Management
- User registration and login.
- JWT-based authentication.
- Secure password handling.
- Save generated blogs to PostgreSQL.
- Personal blog history.
- Open, view, and delete saved blogs.

### Content Editing & Export
- Edit generated blog content.
- Regenerate and improve articles using custom instructions.
- Export blogs in Markdown, PDF, and DOCX formats.
- View blog statistics such as word count and estimated reading time.
- Display research sources.

### Modern User Interface
- Responsive web interface.
- Premium AI Studio-inspired design.
- Dark and Light themes.
- Live generation progress.
- Login and signup interface.
- Password visibility toggle.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Backend | Python, FastAPI |
| AI Workflow | LangGraph |
| LLM | Google Gemini |
| Web Research | Tavily Search |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Authentication | JWT |
| Frontend | HTML, CSS, JavaScript |
| Document Export | Markdown, PDF, DOCX |

## 🏗️ Project Architecture

```text
InkFlow-AI-Blog-Writer/
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── blog_routes.py
│   ├── database.py
│   └── models.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── migrations/
│   └── versions/
│
├── alembic.ini
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

*Note: The structure above highlights the main application files; additional modules may exist in the repository.*

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/atulsahu003/InkFlow-AI-Blog-Writer.git

cd InkFlow-AI-Blog-Writer
```

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Add the environment variables required by the application, including your:

- Google Gemini API key
- Tavily API key
- PostgreSQL database connection settings
- JWT authentication configuration

Use the exact variable names expected by the backend configuration.

**Important:** Never commit `.env` files, API keys, database passwords, or authentication secrets to GitHub.

### 5. Configure PostgreSQL

Install and start PostgreSQL.

Create the database using the database name configured for the application.

Ensure that the database connection settings in `.env` are correct.

### 6. Run Database Migrations

After configuring the database, apply the migrations:

```bash
alembic upgrade head
```

### 7. Start the Backend

```bash
uvicorn backend.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 8. Launch the Frontend

Open the project in Visual Studio Code.

Launch `frontend/index.html` using the Live Server extension.

Make sure the frontend API configuration points to the running backend.

## 🔄 Application Workflow

```text
User Registration / Login
          |
          v
     Enter Blog Topic
          |
          v
     Tavily Research
          |
          v
    Blog Planning
          |
          v
  Parallel Content Writing
          |
          v
    Proofreading
          |
          v
    Generated Blog
          |
          v
   Edit / Regenerate
          |
          v
  Save to PostgreSQL
          |
          v
  Export / Blog History
```

## 🔐 Security

- JWT-based authentication.
- Password hashing.
- Protected user-specific blog operations.
- Environment-based configuration for sensitive credentials.
- `.env` and virtual environment excluded from version control.

## 🚀 Deployment

Production deployment is planned.

The intended deployment architecture includes:

- Frontend hosting for the web application.
- Backend hosting for the FastAPI application.
- Managed PostgreSQL database.
- Secure production environment variables.
- Production API and CORS configuration.

Deployment links will be added after the application is successfully deployed and tested.

## 🔮 Future Improvements

- Enhanced AI writing capabilities.
- More customization options for generated blogs.
- Additional export formats.
- Improved research and source management.
- Production deployment and performance optimization.

## 📄 License

No license has been specified yet.

## 👨‍💻 Author

**Atul Sahu**

AI & Data Science Developer

GitHub: [@atulsahu003](https://github.com/atulsahu003)

---

⭐ If you find this project interesting, consider exploring the repository and its development.
