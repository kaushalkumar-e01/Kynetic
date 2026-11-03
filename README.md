# Kynetic — Knowledge in Motion

**Turn Ambition Into Capability.**

Kynetic is an AI-powered personalized capability-development platform. Its primary focus is helping students and job seekers prepare for internships and placements by understanding their current skills, testing their knowledge, analysing their projects, identifying skill gaps, and creating personalized learning roadmaps.

Kynetic is a **persistent personal workspace**, not a one-time resume checker or forced step-by-step wizard. Each user has a private account where information, analyses, repositories, assessment history, goals, roadmaps, and progress remain available across logins.

## What makes Kynetic different?

Kynetic combines three forms of evidence:
1. **Resume/profile evidence** — what the user says they know.
2. **Assessment evidence** — what the user demonstrates through quizzes and coding challenges.
3. **Project evidence** — what can be supported by project descriptions, repositories, and implementation.

A resume claim alone is not treated as verified proficiency.

## Main Modules
- Personalized Dashboard and persistent workspace.
- Resume intelligence and versioned analysis.
- Adaptive quizzes and coding challenges (Easy, Medium, Hard).
- Capability profile distinguishing claimed, assessed, and project-supported skills.
- GitHub and project intelligence.
- LinkedIn profile information through user-provided data or authorized integrations.
- Placement/job matching and explainable skill gaps.
- Personalized learning roadmaps.
- Progress analytics and AI learning assistant.

## Persistent and Flexible by Design
- User data is stored in the backend/database, not only in browser state.
- Users can log out and return without losing progress.
- Modules are independently accessible; there is no mandatory linear sequence.
- Users can add/update resumes, projects, repositories, goals, and profile information over time.
- Recommendations use saved information and evidence.

## Planned Technology
| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI, Pydantic |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| AI | LLM provider layer; embeddings/RAG where useful |
| Integrations | GitHub API; authorized profile integrations |
| Coding assessment | Isolated code-execution service |

## Repository Structure
```text
Kynetic/
├── frontend/
│   └── .gitkeep
├── backend/
│   └── .gitkeep
├── docs/
│   ├── API_CONTRACT.md
│   ├── TEAM_WORKFLOW.md
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   └── ASSESSMENT_AND_PROJECT_ANALYSIS.md
├── plan.md
├── README.md
├── .env.example
└── .gitignore
```

## Documentation
- [Project plan](plan.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data model](docs/DATA_MODEL.md)
- [API contract](docs/API_CONTRACT.md)
- [Assessment and project analysis](docs/ASSESSMENT_AND_PROJECT_ANALYSIS.md)
- [Team workflow](docs/TEAM_WORKFLOW.md)

## Development Setup
Application setup instructions will be added during the foundation milestone. Planned prerequisites:
- Git
- Python (version to be agreed)
- Node.js and npm
- PostgreSQL
- Visual Studio Code or another editor

Do not put real API keys, database passwords, OAuth secrets, or other credentials in this repository. Use local environment files based on `.env.example`; real environment files are ignored by Git.

## Team
Three-member team:
- Project coordination, repository management, documentation, and integration.
- Backend development and AI integration.
- Frontend development and API integration.

See [TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md).

## Important Notes
- AI match scores and capability estimates are estimates, not guaranteed employer ATS results or formal certifications.
- External platform content must only be accessed and used as permitted.
- Do not scrape LinkedIn or copy/redistribute LeetCode or HackerRank question banks without authorization.
- User-submitted code must only run in an isolated, resource-limited environment.

**Kynetic — Turn Ambition Into Capability.**
