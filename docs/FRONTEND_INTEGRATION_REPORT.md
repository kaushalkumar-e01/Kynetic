# Kynetic: Frontend-Backend Integration Audit & Delivery Report

**Date:** November 4, 2026  
**Branch:** `feature/frontend-integration`  
**Engineer:** Senior Full-Stack Integration Engineer  
**Workspace:** `Kynetic` Platform Repository  

---

## 1. Executive Summary & Readiness Rating

Kynetic ("Knowledge in Motion") is an AI-driven capability-development and career-readiness platform designed for students and job seekers. Over this integration initiative, the FastAPI backend (63 endpoints under `/api/v1`) and the Next.js 15 (App Router) frontend prototype have been reconciled, typed, and end-to-end integrated across all core domains. All mock data has been decoupled from UI screens, centralized HttpOnly cookie authentication (`credentials: 'include'`) has been instituted, and all seven integration stages (Auth, Profile, Workspace Summary, Resumes, Capabilities/Evidence, Goals, Roadmaps, Placement, Assessments, Projects, GitHub Integration, and AI Assistant) have been connected and verified with live regression testing. Per strict architectural safety guidelines, the code execution sandbox has been disabled with an explicit "Coming Soon" guard due to server-side isolation vulnerabilities.

### Readiness Rating

| Target Environment | Status | Rating | Key Justification |
| :--- | :--- | :--- | :--- |
| **Local Demo** | **READY** | 🟢 **9.5 / 10** | Complete end-to-end user journey works against live backend with zero console errors, full loading/error states, and smooth UI reactivity. |
| **Internal Testing (QA)** | **READY (Guarded)** | 🟡 **8.0 / 10** | All CRUD, AI analysis, adaptive quizzing, and placement matching are functional. Coding challenge sandbox is safely disabled. |
| **Production** | **NOT READY** | 🔴 **4.5 / 10** | Blocked by security constraints: sandbox isolation needed, GitHub OAuth CSRF `state` check missing, tokens stored unencrypted in DB, and lack of rate limiting. |

---

## 2. Verification Summary & Audit Claim Fact-Checking

### What Was Verified
1. **Backend Test Suite:** Executed via `pytest` in `backend/.venv` (Python 3.13.15). **45 passed, 0 failed** (100% pass rate).
2. **Database Migrations:** Clean SQLite initialization and migration verification using `alembic upgrade head` (revisions `03b8fda41d1d` and `a3f24cacf581`).
3. **Frontend Compilation & Types:** `npx tsc --noEmit` passed with **0 errors**.
4. **Frontend Linter:** `npm run lint` passed with **0 errors and 0 warnings** across all pages and components.
5. **Frontend Production Build:** `npm run build` generated 7 static route entry points and dynamic App Router chunks without warnings.
6. **Live Multi-User Integration Script:** Automated end-to-end Python test script verified authentication, session cookies, resume parsing, evidence accumulation, goal creation, roadmap generation, placement matching, assistant messaging, and cross-user resource isolation.

### Backend Audit Claim Fact-Checking ("Trust but Verify")

The backend repository included an internal audit report (`docs/BACKEND_FINAL_AUDIT_REPORT.md`). A rigorous line-by-line inspection revealed multiple substantial inaccuracies:

| Claimed in Audit Report | Verified Reality | Discrepancy Analysis |
| :--- | :--- | :--- |
| *"Total registered REST API endpoints: 41"* | **63 Endpoints Registered** | The backend actually registers 63 endpoints under `/api/v1` across 13 routers. The audit report undercounted endpoints by 35% (missed activity, challenges, questions, roadmaps, placement sub-routes). |
| *"Code linting via ruff passed with 0 errors"* | **~380 Ruff Violations** | `ruff` was completely omitted from `requirements.txt`. When installed and executed without custom rule ignores, `ruff check .` produced ~380 errors (line length > 88, import orders, unused variables). |
| *"All backend tests pass cleanly"* | **Failed to Collect / Run** | Initial test collection crashed immediately with `ModuleNotFoundError: No module named 'pypdf'`. In addition, `test_health.py::test_app_routes_registered` failed under modern FastAPI because `_IncludedRouter` objects do not expose `.path`. |
| *"Tokens encrypted at rest in database"* | **Plaintext Storage** | The database column in `ConnectedAccount` is named `encrypted_token`, but `integrations.py:52` stores the raw string directly without encryption or hashing. |
| *"Secure AST-based sandboxed code runner"* | **Escapable Subprocess** | The AST visitor only blocks names like `eval` or imports of `os`. It completely ignores attribute access (`__class__.__bases__[0].__subclasses__()`), allowing arbitrary host command execution in an unconfined OS subprocess. |

---

## 3. Integration Status Matrix by Module

| Module | Features & Screens | Backend Endpoints | Status | Data Source | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth** | Register, Login, Logout, Session check | `POST /auth/register`<br>`POST /auth/login`<br>`POST /auth/logout`<br>`GET /auth/me` | **Fully Supported** | Live API | HttpOnly cookies (`samesite="lax"`), global 401 redirect, zero token exposure in client storage. |
| **Profile** | User profile view & edit | `GET /profile`<br>`PATCH /profile` | **Fully Supported** | Live API | Mapped to backend schema (`headline`, `education_summary`, `experience_summary`, `preferred_domains`). |
| **Workspace / Summary** | Dashboard, quick stats, radar metrics | `GET /workspace/summary`<br>`GET /workspace/activity`<br>`GET /capabilities` | **Fully Supported** | Live API | Dynamic capability counts and real user audit logs rendered. |
| **Resumes** | Upload PDF, list, delete, AI parse | `POST /resumes/upload`<br>`GET /resumes`<br>`DELETE /resumes/{id}`<br>`POST /resumes/{id}/analyze`<br>`GET /resumes/{id}/analysis` | **Fully Supported** | Live API | Strict 10MB limit, PDF validation, synchronous blocking AI analysis (replaces polling UI). |
| **Capabilities & Evidence** | Matrix, bands, evidence sources | `GET /capabilities`<br>`GET /capabilities/{id}/evidence`<br>`POST /capabilities/{id}/evidence` | **Fully Supported** | Live API | Explicitly displays `claimed`, `foundational`, `proficient`, `advanced` bands, distinguishing resume, quiz, and project evidence. |
| **Assessments (MCQ)** | Topic list, adaptive start, question answering, results | `GET /assessments/topics`<br>`POST /assessments`<br>`GET /assessments/{id}`<br>`POST /assessments/{id}/answers`<br>`GET /assessments/{id}/results` | **Fully Supported** | Live API | Dynamic adaptive question retrieval and instant option evaluation. |
| **Assessments (Coding)** | In-browser coding challenge runner | `POST /assessments/{id}/challenges/run` | **Disabled (Security)** | Guarded / Coming Soon | UI displays explicit security notice. Code sandbox executes unconfined on host. |
| **Projects** | Project CRUD, synchronous analysis | `GET /projects`<br>`POST /projects`<br>`GET /projects/{id}`<br>`DELETE /projects/{id}`<br>`POST /projects/{id}/analyze` | **Fully Supported** | Live API | Keyword & heuristic analysis of tech stack and project strengths. |
| **GitHub Integration** | Connect OAuth, list repos, import repo, disconnect | `GET /integrations/github/connect`<br>`GET /integrations/github/callback`<br>`GET /integrations/github/repositories`<br>`POST /integrations/github/repositories`<br>`DELETE /integrations/github/disconnect` | **Fully Supported** | Live API / Dev Mock | Handles local mock tokens seamlessly when GitHub Client ID is unconfigured. |
| **LinkedIn Integration** | Profile import preview | N/A (Not in backend) | **Mock Preview** | Mock Flag | Gracefully isolated behind mock toggle; displays explicit "Import Service Upcoming" notice. |
| **Goals** | Goal CRUD, target dates, progress | `GET /goals`<br>`POST /goals`<br>`GET /goals/{id}`<br>`PATCH /goals/{id}`<br>`DELETE /goals/{id}` | **Fully Supported** | Live API | Reactive status updates and goal deletion. |
| **Placement** | Job description match & gap analysis | `POST /placement/matches`<br>`GET /placement/matches`<br>`GET /placement/matches/{id}` | **Fully Supported** | Live API | Validates minimum 20-character job description requirement. Displays score breakdowns and limitations. |
| **Roadmaps** | Learning roadmaps & milestones | `POST /roadmaps`<br>`GET /roadmaps`<br>`GET /roadmaps/{id}`<br>`PATCH /roadmaps/milestones/{id}` | **Fully Supported** | Live API | Step-by-step milestone toggle with progress bar calculation. |
| **AI Assistant** | Conversations and chat messages | `GET /assistant/conversations`<br>`POST /assistant/conversations`<br>`GET /assistant/conversations/{id}`<br>`POST /assistant/conversations/{id}/messages` | **Fully Supported** | Live API | Context-aware career assistant messages with optimistic UI rendering. |
| **Settings** | User preferences & notifications | `GET /profile`<br>`PATCH /profile` | **Partially Supported** | Hybrid | Preferences mapped to `learning_preferences` JSON column. Client-only theme toggles kept local. |

---

## 4. Changes Made with Commit References

### Backend Changes
1. **Pinned Dependencies:** Added `pypdf==6.21.4` and `ruff==0.17.3` to `backend/requirements.txt` with exact version pins.
2. **FastAPI Route Reflection Fix:** Refactored `backend/tests/test_health.py` to inspect both direct router paths and `app.openapi()['paths']`, fixing test suite failure under modern FastAPI `_IncludedRouter`.
3. **Fail-Fast Secret Key Guard:** Added startup validation in `backend/app/core/config.py` and `backend/app/main.py` ensuring the server refuses to boot if `APP_ENV != "development"` while `SECRET_KEY` remains the default insecure string. Added regression tests in `backend/tests/test_errors.py`.

### Frontend Changes
1. **Prototype Extraction & Structuring:** Extracted prototype from `frontend/kynetic (1).zip` into clean App Router architecture.
2. **Strict Tooling Setup:** Configured `frontend/.eslintrc.json` extending `next/core-web-vitals` with zero lint tolerance.
3. **Typed API Layer (`frontend/lib/api/`):**
   - Built unified typed HTTP client (`client.ts`) utilizing `credentials: 'include'` and normalizing backend errors (`{ error: { code, message, details } }`).
   - Implemented 12 typed domain modules: `auth.ts`, `profile.ts`, `workspace.ts`, `resumes.ts`, `skills.ts`, `assessments.ts`, `projects.ts`, `integrations.ts`, `goals.ts`, `placement.ts`, `roadmaps.ts`, `assistant.ts`.
4. **Generated Contract Types (`frontend/types/`):** Generated TypeScript types matching backend schemas from OpenAPI (`types/openapi.d.ts` and `types/index.ts`).
5. **Modular Views Architecture (`frontend/components/views/`):**
   - Converted monolithic prototype screens into isolated, modular views: `ProfileView.tsx`, `SettingsView.tsx`, `ResumeView.tsx`, `CapabilitiesView.tsx`, `AssessmentsView.tsx`, `ProjectsView.tsx`, `GoalsView.tsx`, `PlacementView.tsx`, `RoadmapsView.tsx`, `AssistantView.tsx`, `IntegrationsView.tsx`, `ProgressView.tsx`.
   - Wired live loading spinners, empty states, and dismissible error alerts across every view.
   - Guarded coding challenge feature behind security banner.

### Git Commits on `feature/frontend-integration`
- `7c1667f`: *feat(integration): Phase 0-2 inventory, baseline checks, and prerequisite fixes*
- `bfb2576`: *feat(api): Phase 3 build typed API client and domain modules from OpenAPI contract*
- `411239e`: *feat(screens): Phase 4 connect modules Stages 1-7 with real API and loading/error states*

---

## 5. Contract Mismatches & Architectural Recommendations

| Domain | Frontend Prototype Expected | Backend Reality | Architectural Recommendation |
| :--- | :--- | :--- | :--- |
| **User Profile** | `bio`, `target_role`, `target_industry`, `linkedin_url`, `github_username` | `headline`, `education_summary`, `experience_summary`, `preferred_domains`, `learning_preferences` | Adopt backend schema; store `target_role` inside `preferred_domains` or extend UserProfile model with a migration. |
| **Resume Analysis** | `parsed_data`, `credibility_score`, `detected_skills` | `extracted_profile`, `strengths`, `suggestions` (synchronous) | Maintain synchronous UI blocking state; do not build polling against non-existent `/jobs/{id}`. |
| **Project Analysis** | `identified_tech_stack`, `completeness_score` | `detected_technologies`, `demonstrated_skills`, `missing_requirements`, `recommendations` | Map UI cards to `detected_technologies` and `missing_requirements`. |
| **Placement Match** | `overall_match_score`, `source_reference` | `estimated_score`, `match_breakdown`, `limitations` | Display breakdown bars for skills, experience, and domains as returned by the backend. |
| **Job Description** | Any short string | String must have $\ge 20$ characters | Frontend form now validates `min(20)` before initiating `POST /placement/matches`. |
| **Assessment Questions** | Array of `{ text, is_correct }` | `options: string[]` (correct answers hidden server-side) | Use server-side answer evaluation via `POST /assessments/{id}/answers`. |

---

## 6. Bugs Discovered & Resolved

### 1. `ModuleNotFoundError: No module named 'pypdf'`
- **Severity:** High (Crash on startup/test)
- **Location:** `backend/app/services/resume_parser.py:5`
- **Reproduction:** Run `pytest` or attempt PDF upload without `pypdf` installed.
- **Resolution:** Added `pypdf==6.21.4` to `backend/requirements.txt`.

### 2. FastAPI Route Introspection Failure
- **Severity:** Medium (Test failure)
- **Location:** `backend/tests/test_health.py:19`
- **Reproduction:** Run `pytest tests/test_health.py` with FastAPI >= 0.115.
- **Resolution:** Added defensive check inspecting `getattr(route, "path", "")` and unioning with OpenAPI paths.

### 3. Blank PDF Extraction 422 Error
- **Severity:** Low / Informational
- **Location:** `backend/app/services/resume_parser.py:44`
- **Reproduction:** Upload a PDF with 0 extractable text characters.
- **Resolution:** The backend deliberately raises 422 `VALIDATION_ERROR` ("Resume does not contain extractable text"). Frontend now surfaces a descriptive alert instructing the user to upload a text-based PDF.

### 4. Job Match Payload Validation Failure
- **Severity:** Low
- **Location:** `backend/app/schemas/placement.py:9`
- **Reproduction:** Submit `POST /placement/matches` with `job_description < 20` chars.
- **Resolution:** Frontend input form enforces `minlength="20"` with helper text.

---

## 7. Ranked Security Findings & Vulnerability Review

### [CRITICAL] 1. Arbitrary Code Execution via Insecure Sandbox
- **Location:** `backend/app/services/sandbox.py:15-37`, `backend/app/api/v1/endpoints/assessments.py:108`
- **Vulnerability:** The sandbox relies solely on an AST visitor checking `ast.Import` and `ast.Call(func=ast.Name)`. It fails to inspect `ast.Attribute`. An attacker can submit Python code utilizing dunder introspection:
  ```python
  ().__class__.__bases__[0].__subclasses__()[140].__init__.__globals__['system']('id')
  ```
- **System Impact:** Spawns an unconfined OS subprocess on the host application server with no cgroup memory limits, no CPU quota, no seccomp profile, and full host file/network access.
- **Mitigation Taken:** Coding challenge feature was completely hidden/disabled on the frontend with a security disclaimer.
- **Required Production Fix:** Deploy a containerized execution runner (e.g., Firecracker microVM, Docker with `--network none --cap-drop ALL --read-only`, or an external runner like Judge0).

### [HIGH] 2. OAuth CSRF Vulnerability in GitHub Callback
- **Location:** `backend/app/api/v1/endpoints/integrations.py:36-40`
- **Vulnerability:** `GET /integrations/github/connect` generates a random `state` token, but does not store it in the session or database. `GET /integrations/github/callback` does not accept or verify the `state` parameter at all.
- **Attack Vector:** An attacker can trick a user into completing an OAuth callback with the attacker's authorization code, binding the victim's account to an attacker's repository.
- **Required Production Fix:** Store `state` in an encrypted signed session cookie or DB cache with a 10-minute TTL, and strictly verify `state` in the callback before exchanging the authorization code.

### [HIGH] 3. Plaintext Third-Party Token Storage
- **Location:** `backend/app/models/project.py:53`, `backend/app/api/v1/endpoints/integrations.py:52`
- **Vulnerability:** GitHub access tokens are stored directly in the `encrypted_token` column without encryption.
- **System Impact:** Database compromises or read-only SQL injection leaks live GitHub access tokens granting access to user repositories.
- **Required Production Fix:** Apply symmetric AES-256-GCM envelope encryption using a dedicated database encryption key prior to persisting tokens.

### [MEDIUM] 4. Absence of Endpoint Rate Limiting
- **Location:** All routes in `backend/app/api/v1/endpoints/*.py`
- **Vulnerability:** No rate limiting or throttling exists on `/auth/login` (brute-force exposure) or AI endpoints (`/resumes/{id}/analyze`, `/projects/{id}/analyze`, `/assistant/conversations/{id}/messages`).
- **Required Production Fix:** Implement Redis-backed token-bucket rate limiting (e.g., `slowapi`) limiting login attempts to 5/minute and AI calls to 20/minute per user.

### [MEDIUM] 5. Unbounded In-Memory File Buffering
- **Location:** `backend/app/api/v1/endpoints/resumes.py:37`
- **Vulnerability:** The 10MB file size check occurs *after* `file_bytes = await file.read()`. An attacker uploading a multi-gigabyte payload will cause severe memory pressure or OOM before the check triggers.
- **Required Production Fix:** Read the file in streaming chunks (e.g., 64KB chunks) and abort the upload immediately if the cumulative stream exceeds 10MB.

### [LOW] 6. Frontend Transitive Dependencies
- **Location:** `frontend/package.json` (`npm audit`)
- **Vulnerability:** 16 vulnerabilities reported (15 moderate in ESLint/minimatch dev tooling, 1 high in Next.js internal PostCSS CSS stringifier).
- **Required Production Fix:** Upgrade Next.js to latest stable release once verified with App Router tree.

---

## 8. Prioritized Remediation To-Do List

| Priority | Task Description | Scope | Effort | Suggested Owner |
| :--- | :--- | :--- | :--- | :--- |
| **MUST** | Build containerized/isolated sandbox microservice (Docker/Firecracker) | Backend / Infra | **L** | DevOps / Backend |
| **MUST** | Implement OAuth `state` verification & AES-256 token encryption | Backend Security | **M** | Backend Lead |
| **MUST** | Add Redis rate limiting on auth, AI, and upload endpoints | Backend | **M** | Backend Engineer |
| **SHOULD** | Implement streaming file upload checks in `resumes.py` | Backend | **S** | Backend Engineer |
| **SHOULD** | Implement refresh token rotation & server-side JWT revocation | Backend Auth | **M** | Backend Engineer |
| **SHOULD** | Expand question bank from 12 questions to $\ge 100$ questions across topics | Content / AI | **M** | Content / AI Lead |
| **NICE** | Implement LinkedIn Profile import worker/service | Backend | **L** | Integrations Engineer |
| **NICE** | Add client-side dark/light theme persistence to user profile settings | Frontend | **S** | Frontend Engineer |

---

## 9. Feature Gaps vs. Original Specifications

Comparing current implementation against `plan.md` and `docs/API_CONTRACT.md`:
1. **Coding Challenge Execution:** Specification called for an interactive in-browser coding test with real-time test case execution. Current status is disabled due to backend host execution vulnerability.
2. **Repository Analysis Depth:** Specification implied AST/code analysis of connected GitHub repositories. Currently, `projects.py` performs heuristic keyword matching against project name, description, and repository URL without cloning or inspecting repository files.
3. **LinkedIn & External Profile Sources:** The API contract referenced `/profile-sources` for importing profile data. The backend does not register this endpoint; frontend retains this feature under a prototype preview banner.
4. **Adaptive Quiz Breadth:** The question bank consists of 12 hardcoded questions across 3 topics (`python-fundamentals`, `data-structures`, `api-design`). Real-world adaptivity is constrained by question volume.

---

## 10. Recommended Next Sprint Plan

1. **Sprint Task 1 (Security - Token Encryption & OAuth State):** Implement cryptographic envelope for `ConnectedAccount.encrypted_token` and enforce signed CSRF `state` validation on `/integrations/github/callback`.
2. **Sprint Task 2 (Infrastructure - Containerized Sandbox):** Provision isolated execution worker using gVisor or Docker with restricted capabilities to safely unblock Phase 4 Stage 7 coding challenges.
3. **Sprint Task 3 (Auth - Rate Limiting & Refresh Tokens):** Add `slowapi` rate limiting on `/auth/*` and implement refresh token rotation for extended web sessions.
4. **Sprint Task 4 (AI Analysis - Streaming & Prompt Hardening):** Add delimited prompt templates with injection defenses for resume and project parsing, and switch resume file reading to chunked streams.
5. **Sprint Task 5 (Content - Question Bank Expansion):** Populate database seed with 150+ categorized questions with granular difficulty tiers (`foundational`, `intermediate`, `advanced`).
6. **Sprint Task 6 (Frontend - Theme & Notification Preferences):** Wire UI settings toggles to persisted backend user preference schemas.

---

## 11. Run & Verification Guide

### 1. Backend Environment Setup & Launch
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Install pinned dependencies
pip install -r requirements.txt

# Execute database migrations
alembic upgrade head

# Run backend test suite
pytest

# Start development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### 2. Frontend Environment Setup & Launch
```bash
# Navigate to frontend directory
cd frontend

# Verify environment variables (.env.local)
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
# NEXT_PUBLIC_USE_MOCKS=false

# Install dependencies
npm install

# Run type checker and linter
npx tsc --noEmit
npm run lint

# Build production bundle
npm run build

# Start Next.js development server
npm run dev
```
- Web Application: `http://localhost:3000`
- Access `/login` to register a new user or log in to the workspace dashboard.

