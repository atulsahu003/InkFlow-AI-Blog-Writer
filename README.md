# ✍️ InkFlow AI — AI-Powered Blog Writing Agent

An intelligent AI-powered blog writing platform that generates, revises, and exports high-quality blog content using **Google Gemini, LangGraph, and Tavily**.

InkFlow AI simplifies content creation by transforming user prompts into structured blog articles with an AI-driven workflow.

<p align="center">

**Live Demo:** https://inkflow-ai-frontend.onrender.com/

**Backend API:** https://inkflow-ai-blog-writer.onrender.com/

**API Documentation:** https://inkflow-ai-blog-writer.onrender.com/docs

</p>

---

## 🚀 Project Overview

InkFlow AI is an AI-powered blog writing application designed to automate and simplify the blog creation process.

Users can generate blog articles by providing a topic and relevant instructions. The application uses Google's Gemini model and LangGraph-powered workflows to generate and refine content.

The platform also supports blog history management, content revision, and DOCX export.

## ✨ Key Features

- **AI Blog Generation:** Generate structured blog articles using Google Gemini.
- **Agentic Workflow:** Use LangGraph to organize AI-powered writing workflows.
- **Web Research:** Integrate Tavily for web search and research.
- **Blog Revision:** Regenerate and improve existing blog content.
- **Blog History:** Save, retrieve, update, and delete previously generated blogs.
- **DOCX Export:** Export generated blog content into Word documents.
- **User Authentication:** Signup, login, and protected API endpoints.
- **Streaming Generation:** Support streaming responses during blog generation.
- **REST API:** Backend APIs built using FastAPI.
- **Cloud Deployment:** Frontend and backend deployed on Render.
- **Database Integration:** PostgreSQL database hosted on Neon.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| AI Model | Google Gemini |
| Agent Framework | LangGraph |
| Web Research | Tavily |
| Database | PostgreSQL |
| Database ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Authentication | JWT, Argon2 |
| Frontend | HTML, CSS, JavaScript |
| Document Export | python-docx |
| Deployment | Render |
| Database Hosting | Neon |
| API Documentation | Swagger / OpenAPI |

## 🏗️ System Architecture

```text
             USER
               |
               v
       INKFLOW FRONTEND
        HTML / CSS / JS
               |
               v
          FASTAPI
          BACKEND
               |
       +-------+-------+
       |               |
       v               v
  LANGGRAPH         AUTH SYSTEM
  WORKFLOW          JWT / JWT
       |
       v
   GOOGLE GEMINI
       |
       +------> TAVILY WEB SEARCH
       |
       v
  GENERATED BLOG
       |
       +------> BLOG MANAGEMENT
       |        PostgreSQL
       |
       +------> DOCX EXPORT
       |
       v
    USER OUTPUT
```

## 📂 Project Structure

```text
InkFlow-AI-Blog-Writer/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   └── ...
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── alembic/
├── requirements.txt
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

*Note: The structure above presents the main project components; individual folders may contain additional modules.*

## ⚙️ Installation & Setup

Follow these steps to run InkFlow AI locally.

### 1. Clone the Repository

```bash
git clone https://github.com/atulsahu003/InkFlow-AI-Blog-Writer.git

cd InkFlow-AI-Blog-Writer
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Add the following variables:

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key

AUTH_SECRET_KEY=your_secure_secret_key

DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=your_database_name
```

**Important:** Never commit your `.env` file or expose API keys, database credentials, or authentication secrets publicly.

### 5. Run Database Migrations

```bash
python -m alembic upgrade head
```

### 6. Start the Backend Server

```bash
python -m uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Run the Frontend

Open `frontend/index.html` in your browser or serve the frontend using a local development server.

Make sure the frontend API configuration points to your local backend when running locally.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Authenticate user |
| GET | `/auth/me` | Get authenticated user |
| POST | `/api/generate` | Generate a blog |
| POST | `/api/generate/stream` | Stream blog generation |
| POST | `/api/regenerate` | Revise or regenerate a blog |
| POST | `/api/blogs` | Save a blog |
| GET | `/api/blogs` | Retrieve blog history |
| GET | `/api/blogs/{blog_id}` | Retrieve a specific blog |
| PATCH | `/api/blogs/{blog_id}` | Update a blog |
| DELETE | `/api/blogs/{blog_id}` | Delete a blog |
| POST | `/api/export/docx` | Export blog as DOCX |
| GET | `/api/health` | Check backend health |

For complete request and response schemas, visit the [Swagger API Documentation](https://inkflow-ai-blog-writer.onrender.com/docs).

## ☁️ Deployment

InkFlow AI is deployed using cloud services.

| Component | Platform |
|---|---|
| Frontend | Render Static Site |
| Backend | Render Web Service |
| Database | Neon PostgreSQL |
| Source Code | GitHub |

**Live Application:** https://inkflow-ai-frontend.onrender.com/

**Backend:** https://inkflow-ai-blog-writer.onrender.com/

## 🔐 Security

- Environment variables are used to manage sensitive credentials.
- JWT-based authentication protects authorized endpoints.
- Password hashing is implemented using Argon2.
- Database connections use SSL.
- API access is controlled through authentication and CORS configuration.

## 🎯 Project Objectives

- Automate blog writing using generative AI.
- Explore agentic AI workflows using LangGraph.
- Integrate external web research into AI applications.
- Build scalable REST APIs using FastAPI.
- Implement authentication and PostgreSQL database management.
- Deploy a complete full-stack AI application.

## 🔮 Future Enhancements

- Multiple writing tones and styles.
- SEO optimization and keyword analysis.
- AI-powered grammar and readability checking.
- Blog templates and custom formatting.
- Multi-language blog generation.
- Improved content research and source attribution.
- Advanced analytics and writing history.

## 👨‍💻 Author

**Atul Sahu**

B.Tech Computer Science Engineering — AI & Data Science

- GitHub: https://github.com/atulsahu003
- Project Repository: https://github.com/atulsahu003/InkFlow-AI-Blog-Writer

---

<p align="center">

**Built with ❤️ using Python, Generative AI, and Agentic Workflows.**

</p>
