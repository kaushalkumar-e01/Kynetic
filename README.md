# Kynetic — Knowledge in Motion

**Turn Ambition Into Capability.**

Kynetic is an AI-powered personalized capability-development platform designed to help students and job seekers prepare for internships and technical roles by understanding their current skills, evaluating their knowledge through adaptive assessments, analysing their repositories, identifying skill gaps, and generating personalized learning roadmaps.

Kynetic is a **persistent personal workspace**, not a one-time resume checker. Each user has a private account where information, analyses, repositories, assessment history, goals, roadmaps, and progress remain available across sessions.

---

## What Makes Kynetic Different?

Kynetic combines three forms of evidence:
1. **Resume & Profile Evidence** — what the candidate claims to know.
2. **Assessment Evidence** — what the candidate demonstrates through adaptive quizzes, output prediction, bug identification, and coding challenges.
3. **Project & Repository Evidence** — what can be verified through GitHub repository analysis and real-world implementation.

A resume claim alone is never treated as verified proficiency.

---

## Architecture & Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | Next.js 14, React 18, TypeScript | App Router, Tailwind CSS, Lucide icons |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2 | RESTful API, async lifespan, JWT authentication |
| **Database** | SQLite + SQLAlchemy 2.0 | Portable, zero-configuration local database (`kynetic_dev.db`) |
| **AI / LLM** | Google Gemini 2.5 Flash | Resume skill extraction, question generation, roadmap synthesis (with built-in local deterministic fallback) |
| **Code Sandbox** | Piston / Judge0 isolated runner | Secure remote sandboxing with input/output validation |

---

## Prerequisites for Developers

Before setting up Kynetic on any operating system (Windows, macOS, or Linux), make sure you have:

- **Git**: [Download Git](https://git-scm.com/downloads)
- **Python**: Version **3.11** or higher ([python.org](https://www.python.org/downloads/))
- **Node.js**: Version **18** or higher (LTS recommended) and **npm** ([nodejs.org](https://nodejs.org/))

---

## Quickstart (One-Click Launch)

Kynetic includes automated dev launch scripts that detect dependencies, create virtual environments, install packages, initialize the SQLite database, seed 2,000+ catalog questions, and launch both servers simultaneously:

### Windows
Double-click `run-dev.bat` or run in PowerShell:
```powershell
.\run-dev.bat
```

### macOS / Linux
Open a terminal and run:
```bash
chmod +x run-dev.sh
./run-dev.sh
```

Once running:
- **Web Application**: Open [http://localhost:3000](http://localhost:3000)
- **API Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: Open [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## Manual Step-by-Step Setup

Follow these steps to set up and run Kynetic on any developer machine (Windows, macOS, or Linux):

### Step 1 — Clone the Repository
```bash
git clone https://github.com/kaushalkumar-e01/Kynetic.git
cd Kynetic
```

### Step 2 — Install Dependencies

#### Backend (Python 3.11+)
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# Install all required Python packages
pip install -r requirements.txt
```

#### Frontend (Node.js 18+)
In a separate terminal:
```bash
cd frontend

# Install Node dependencies using npm or pnpm
npm install
```

### Step 3 — Configure Environment Variables

#### Backend Environment
```bash
# In the backend directory:
cp .env.example .env
```
Edit `backend/.env` if you wish to configure live Google Gemini AI:
- `GEMINI_API_KEY`: *(Optional)* Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).
- If left blank, Kynetic uses its built-in local deterministic AI engine.

#### Frontend Environment
```bash
# In the frontend directory:
cp .env.example .env.local
```
The default `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1` works immediately out of the box.

### Step 4 — Initialize the Database

The local SQLite database (`kynetic_dev.db`) is automatically initialized and seeded on backend startup. If you wish to explicitly apply Alembic database migrations:
```bash
cd backend
python -m alembic upgrade head
```

### Step 5 — Start the Application

#### Start the Backend Server (Terminal 1)
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Start the Frontend Development Server (Terminal 2)
```bash
cd frontend
npm run dev
```

### Step 6 — Verify the Application

Open your browser and verify:
1. **Frontend**: [http://localhost:3000](http://localhost:3000) (Dashboard & Application)
2. **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
3. **Backend Health & Diagnostics**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
4. **AI Assistant**: Navigate to the **Assistant** tab and send a message.
5. **Roadmaps**: Navigate to the **Roadmaps** tab to explore built-in curriculums (C, C++, Python, DSA, MySQL, Full Stack) with verified resources and interactive progress tracking.

---

## Environment Variables & Configuration

### Backend (`backend/.env`)

| Variable | Required? | Default Value | Description |
|---|---|---|---|
| `APP_ENV` | Yes | `development` | Runtime environment (`development`, `test`, `production`) |
| `DATABASE_URL` | Yes | `sqlite:///./kynetic_dev.db` | SQLite database file location (portable absolute resolution) |
| `SECRET_KEY` | Yes | *(development default)* | JWT token signing key |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://127.0.0.1:3000` | Allowed origins (development permits loopback & LAN) |
| `GEMINI_API_KEY` | Optional | *(empty)* | Google Gemini API Key from Google AI Studio |
| `GEMINI_MODEL` | Optional | `gemini-2.5-flash` | Gemini model variant |
| `LLM_PROVIDER` | Yes | `gemini` | `gemini` (with fallback) or `fallback` |

### Frontend (`frontend/.env.local`)

| Variable | Required? | Default Value | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Yes | `http://localhost:8000/api/v1` | Backend API base URL (auto-normalized by client) |
| `NEXT_PUBLIC_USE_MOCKS` | No | `false` | When `false`, calls live backend |

---

## Google Gemini AI Setup & Local Fallback

Kynetic uses Google Gemini for deep capability analysis, resume parsing, and dynamic question generation.

### How to Configure Gemini:
1. Generate an API key from [Google AI Studio](https://aistudio.google.com/).
2. Add your key to `backend/.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. Restart the backend server.

### Local Deterministic Fallback (No Key Required):
If `GEMINI_API_KEY` is not provided, **Kynetic will NOT crash or fail**. The backend includes built-in deterministic fallback engines that:
- Serve pre-validated catalog questions across all difficulties and tracks.
- Parse resumes using rule-based keyword extraction.
- Provide structured roadmap suggestions.

This ensures every new developer on the team can clone, run, and test the entire application immediately without waiting for API keys.

---

## Health Check & System Verification

The backend provides a comprehensive health check at `GET /api/v1/health` that returns operational readiness without exposing sensitive keys:

```json
{
  "status": "ok",
  "app_env": "development",
  "version": "1.0.0",
  "database_connected": true,
  "database_type": "sqlite",
  "gemini_configured": true,
  "active_questions_count": 2313
}
```

---

## Common Troubleshooting

### 1. "Failed to fetch" or Connection Refused
- **Cause**: The frontend is trying to talk to the backend, but the backend is not running or running on an incompatible address.
- **Fix**:
  - Verify backend is running on `http://127.0.0.1:8000` or `http://localhost:8000`.
  - The frontend automatically detects whether you are accessing via `localhost`, `127.0.0.1`, or LAN IP (`192.168.x.x`) and routes API requests to the matching backend port 8000.
  - If accessing from another device on the same local Wi-Fi, run the backend with `--host 0.0.0.0`.

### 2. Port 8000 or 3000 Already in Use
- **Windows**:
  ```powershell
  # Find PID using port 8000
  netstat -ano | findstr :8000
  # Stop the process
  taskkill /PID <PID> /F
  ```
- **macOS / Linux**:
  ```bash
  lsof -ti :8000 | xargs kill -9
  ```

### 3. Missing Virtual Environment on Windows
If running `.venv\Scripts\Activate.ps1` gives an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Project Structure

```text
Kynetic/
├── frontend/                   # Next.js 14 App Router frontend
│   ├── app/                    # Pages & routing (assessments, resume, projects, etc.)
│   ├── components/             # Reusable UI components & layouts
│   ├── lib/                    # API client, state stores, utilities
│   └── .env.example            # Frontend environment template
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/             # Endpoints (auth, assessments, projects, health, etc.)
│   │   ├── core/               # Configuration, security, database session
│   │   ├── db/                 # Base models & migrations
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── services/           # Business logic (adaptive assessment, Gemini, sandbox)
│   ├── tests/                  # Pytest test suite
│   ├── requirements.txt        # Python dependencies
│   ├── kynetic_dev.db          # Default local SQLite database (auto-generated)
│   └── .env.example            # Backend environment template
├── run-dev.bat                 # One-click Windows development launcher
├── run-dev.sh                  # One-click macOS/Linux development launcher
└── README.md                   # Project documentation & developer guide
```

---

## Team & Contribution Guidelines

- **Database**: SQLite is the standard local development database. All schema changes must be backward-compatible.
- **Security**: Never commit `.env`, `.env.local`, API keys, or private user data to Git.
- **Testing**: Run `pytest backend/tests/` before pushing commits to verify all API contracts remain intact.
