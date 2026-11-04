# Kynetic — Frontend to Backend Integration Matrix

**Date:** November 2026  
**Branch:** `feature/frontend-integration`  
**Phase:** Phase 0 Inventory

---

## 1. Backend API Map

- **Base URL:** `/api/v1`
- **Authentication Method:** Dual-mode authentication supported via `app/api/deps.py`:
  1. `Authorization: Bearer <token>` header (JWT).
  2. `access_token` HttpOnly cookie with `samesite="lax"`, `secure=(env != "development")`, 15-minute default expiry.
- **Standard Error Format:**
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human readable message",
      "details": []
    }
  }
  ```
  Validation error `details` entries format: `[{"location": "body -> field", "message": "...", "type": "value_error"}]`.

### Complete Endpoint Registry (63 Registered Endpoints)

| # | Router / Area | Method | Endpoint Path | Request Schema / Input | Response Schema | Auth Required |
|---|---|---|---|---|---|---|
| 1 | Health | `GET` | `/health` | None | `HealthResponse` | No |
| 2 | Auth | `POST` | `/auth/register` | `UserRegisterRequest` | `TokenResponse` (sets cookie) | No |
| 3 | Auth | `POST` | `/auth/login` | `UserLoginRequest` | `TokenResponse` (sets cookie) | No |
| 4 | Auth | `POST` | `/auth/logout` | None | `{"message": str}` (clears cookie) | No |
| 5 | Auth | `GET` | `/auth/me` | None | `UserResponse` | Yes |
| 6 | Profile | `GET` | `/profile` | None | `UserProfileResponse` | Yes |
| 7 | Profile | `PATCH` | `/profile` | `UserProfileUpdate` | `UserProfileResponse` | Yes |
| 8 | Workspace | `GET` | `/workspace/summary` | None | `WorkspaceSummaryResponse` | Yes |
| 9 | Workspace | `GET` | `/activity` | `limit: int = 20` | `List[ActivityResponse]` | Yes |
| 10 | Workspace | `GET` | `/settings` | None | `UserSettingsResponse` | Yes |
| 11 | Workspace | `PATCH` | `/settings` | `UserSettingsUpdate` | `UserSettingsResponse` | Yes |
| 12 | Resumes | `POST` | `/resumes` | `multipart/form-data` (`file`) | `ResumeResponse` | Yes |
| 13 | Resumes | `GET` | `/resumes` | None | `List[ResumeResponse]` | Yes |
| 14 | Resumes | `GET` | `/resumes/{resume_id}` | `resume_id: str` (path) | `ResumeResponse` | Yes |
| 15 | Resumes | `DELETE` | `/resumes/{resume_id}` | `resume_id: str` (path) | `{"message": str}` | Yes |
| 16 | Resumes | `POST` | `/resumes/{resume_id}/analyze` | `resume_id: str` (path) | `ResumeAnalysisResponse` | Yes |
| 17 | Resumes | `GET` | `/resumes/{resume_id}/analysis` | `resume_id: str` (path) | `ResumeAnalysisResponse` | Yes |
| 18 | Resumes | `GET` | `/resume-analyses/{analysis_id}` | `analysis_id: str` (path) | `ResumeAnalysisResponse` | Yes |
| 19 | Skills | `GET` | `/skills` | None | `List[SkillResponse]` | No |
| 20 | Skills | `GET` | `/capabilities` | None | `List[UserCapabilityResponse]` | Yes |
| 21 | Skills | `GET` | `/capabilities/{skill_id}` | `skill_id: str` (path) | `UserCapabilityResponse` | Yes |
| 22 | Skills | `GET` | `/evidence` | None | `List[EvidenceRecordResponse]` | Yes |
| 23 | Skills | `POST` | `/evidence` | `CreateEvidenceRequest` | `EvidenceRecordResponse` | Yes |
| 24 | Assessments | `GET` | `/assessment-topics` | None | `List[AssessmentTopicResponse]` | No |
| 25 | Assessments | `GET` | `/questions` | `topic_id`, `difficulty`, `limit` | `List[QuestionPublicResponse]` | No |
| 26 | Assessments | `POST` | `/assessments` | `CreateAssessmentRequest` | `AssessmentResponse` | Yes |
| 27 | Assessments | `GET` | `/assessments` | None | `List[AssessmentResponse]` | Yes |
| 28 | Assessments | `GET` | `/assessments/{assessment_id}` | `assessment_id: str` (path) | `AssessmentResponse` | Yes |
| 29 | Assessments | `POST` | `/assessments/{assessment_id}/answers` | `SubmitAnswerRequest` | `AssessmentAttemptResponse` | Yes |
| 30 | Assessments | `POST` | `/assessments/{assessment_id}/code-submissions` | `SubmitCodeRequest` | `AssessmentAttemptResponse` | Yes |
| 31 | Assessments | `GET` | `/assessments/{assessment_id}/results` | `assessment_id: str` (path) | `AssessmentSummaryResultsResponse` | Yes |
| 32 | Assessments | `GET` | `/assessment-attempts` | None | `List[AssessmentAttemptResponse]` | Yes |
| 33 | Projects | `POST` | `/projects` | `ProjectCreate` | `ProjectResponse` | Yes |
| 34 | Projects | `GET` | `/projects` | None | `List[ProjectResponse]` | Yes |
| 35 | Projects | `GET` | `/projects/{project_id}` | `project_id: str` (path) | `ProjectResponse` | Yes |
| 36 | Projects | `PATCH` | `/projects/{project_id}` | `ProjectUpdate` | `ProjectResponse` | Yes |
| 37 | Projects | `DELETE` | `/projects/{project_id}` | `project_id: str` (path) | `{"message": str}` | Yes |
| 38 | Projects | `POST` | `/projects/{project_id}/analyze` | `project_id: str` (path) | `ProjectAnalysisResponse` | Yes |
| 39 | Projects | `GET` | `/projects/{project_id}/analyses` | `project_id: str` (path) | `List[ProjectAnalysisResponse]` | Yes |
| 40 | Projects | `GET` | `/project-analyses/{analysis_id}` | `analysis_id: str` (path) | `ProjectAnalysisResponse` | Yes |
| 41 | Integrations | `GET` | `/integrations/github/connect` | None | `GitHubConnectResponse` | Yes |
| 42 | Integrations | `GET` | `/integrations/github/callback` | `code: str` (query) | `{"message": str, "provider": str}` | Yes |
| 43 | Integrations | `GET` | `/integrations/github/repositories` | None | `List[GitHubRepoItem]` | Yes |
| 44 | Integrations | `POST` | `/integrations/github/repositories` | `ImportGitHubRepoRequest` | `ProjectResponse` | Yes |
| 45 | Integrations | `DELETE` | `/integrations/github/connection` | None | `{"message": str}` | Yes |
| 46 | Goals | `POST` | `/goals` | `GoalCreate` | `GoalResponse` | Yes |
| 47 | Goals | `GET` | `/goals` | None | `List[GoalResponse]` | Yes |
| 48 | Goals | `GET` | `/goals/{goal_id}` | `goal_id: str` (path) | `GoalResponse` | Yes |
| 49 | Goals | `PATCH` | `/goals/{goal_id}` | `GoalUpdate` | `GoalResponse` | Yes |
| 50 | Goals | `DELETE` | `/goals/{goal_id}` | `goal_id: str` (path) | `{"message": str}` | Yes |
| 51 | Placement | `POST` | `/placement/matches` | `JobMatchCreate` | `JobMatchResponse` | Yes |
| 52 | Placement | `GET` | `/placement/matches` | None | `List[JobMatchResponse]` | Yes |
| 53 | Placement | `GET` | `/placement/matches/{match_id}` | `match_id: str` (path) | `JobMatchResponse` | Yes |
| 54 | Roadmaps | `POST` | `/roadmaps` | `RoadmapCreate` | `RoadmapResponse` | Yes |
| 55 | Roadmaps | `GET` | `/roadmaps` | None | `List[RoadmapResponse]` | Yes |
| 56 | Roadmaps | `GET` | `/roadmaps/{roadmap_id}` | `roadmap_id: str` (path) | `RoadmapResponse` | Yes |
| 57 | Roadmaps | `PATCH` | `/roadmaps/{roadmap_id}` | `RoadmapUpdate` | `RoadmapResponse` | Yes |
| 58 | Roadmaps | `POST` | `/roadmaps/{roadmap_id}/milestones` | `MilestoneCreate` | `MilestoneResponse` | Yes |
| 59 | Roadmaps | `PATCH` | `/roadmaps/{roadmap_id}/milestones/{milestone_id}` | `MilestoneUpdate` | `MilestoneResponse` | Yes |
| 60 | Assistant | `POST` | `/assistant/messages` | `SendMessageRequest` | `ConversationResponse` | Yes |
| 61 | Assistant | `GET` | `/assistant/conversations` | None | `List[ConversationSummaryResponse]` | Yes |
| 62 | Assistant | `GET` | `/assistant/conversations/{conversation_id}` | `conversation_id: str` (path) | `ConversationResponse` | Yes |
| 63 | Assistant | `DELETE` | `/assistant/conversations/{conversation_id}` | `conversation_id: str` (path) | `{"message": str}` | Yes |

*Note on discrepancy with Backend Audit Report:* The backend audit report claimed 41 endpoints, but enumeration of all registered FastAPI route handlers shows 63 active endpoints across the 13 router modules.

---

## 2. Frontend Map

- **Framework:** Next.js 15.1.3 (App Router)
- **UI Library:** React 19.0.0, React DOM 19.0.0
- **TypeScript:** Strict mode enabled (`strict: true` in `tsconfig.json`)
- **Styling:** Tailwind CSS 3.4.17 + PostCSS + raw custom CSS system in `app/globals.css` (custom design system variables, classes like `.card`, `.btn-primary`, `.evidence-badge`).
- **Icons & Visualization:** `lucide-react` 0.468.0, `recharts` 2.15.0.
- **State Management:** Local React state (`useState`), Next.js router navigation. No global Redux/Zustand store.
- **Data Layer:** `frontend/lib/api/index.ts` exporting functions reading static data from `frontend/lib/mocks/data.ts`.
- **Route Structure:**
  - `app/page.tsx` -> Landing page
  - `app/login/page.tsx` -> Auth login
  - `app/register/page.tsx` -> Auth register
  - `app/design-system/page.tsx` -> Design system gallery
  - `app/[...slug]/page.tsx` -> Catch-all route for `/dashboard` and all other workspace paths (`/resume`, `/capabilities`, `/assessments`, `/projects`, `/integrations`, `/goals`, `/placement`, `/roadmaps`, `/progress`, `/assistant`, `/profile`, `/settings`).

---

## 3. Screen-to-Endpoint Integration Matrix

| Frontend Screen Route | Screen Purpose / Manus Prototype Status | Backend Endpoints Needed | Backend Support Classification | Notes & Gaps |
|---|---|---|---|---|
| `/` | Public Landing Page | None | **Fully supported** | Static marketing screen |
| `/login` | User Login form | `POST /auth/login`, `GET /auth/me` | **Fully supported** | Cookie-based session |
| `/register` | Account registration | `POST /auth/register`, `GET /auth/me` | **Fully supported** | Auto-logs in with HttpOnly cookie |
| `/dashboard` | Workspace summary dashboard | `GET /workspace/summary`, `GET /capabilities`, `GET /activity` | **Fully supported** | All data models exist in backend |
| `/profile` | Profile settings & target direction | `GET /profile`, `PATCH /profile` | **Fully supported** | Backend `UserProfile` model matches |
| `/settings` | Workspace preferences | `GET /settings`, `PATCH /settings` | **Partially supported** | Backend only has `learning_preferences` JSON |
| `/resume` | Resume list & upload view | `POST /resumes`, `GET /resumes`, `DELETE /resumes/{id}`, `POST /resumes/{id}/analyze` | **Fully supported** | Multipart upload + synchronous analysis |
| `/resume/:id` | Resume details & analysis | `GET /resumes/{id}`, `GET /resumes/{id}/analysis` | **Fully supported** | Full analysis breakdown available |
| `/capabilities` | Skills & evidence bands | `GET /capabilities`, `GET /skills`, `GET /evidence` | **Fully supported** | Shows claimed, assessed, project evidence |
| `/capabilities/:skillId` | Skill capability detail | `GET /capabilities/{skill_id}`, `POST /evidence` | **Fully supported** | Detail view and add user evidence |
| `/projects` | Projects list | `GET /projects` | **Fully supported** | Lists manual & imported repos |
| `/projects/new` | Create project form | `POST /projects` | **Fully supported** | Manual creation supported |
| `/projects/:id` | Project details & analysis trigger | `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}`, `POST /projects/{id}/analyze` | **Fully supported** | Sync project analysis |
| `/projects/:id/analysis/:analysisId` | View project analysis report | `GET /project-analyses/{analysisId}` | **Fully supported** | Analysis details & recommendations |
| `/assessments` | Assessment history & topic catalog | `GET /assessments`, `GET /assessment-topics` | **Fully supported** | Topic listing + past attempts |
| `/assessments/new` | Start new assessment | `POST /assessments` | **Fully supported** | Generates initial question |
| `/assessments/:id` | Take active assessment | `GET /assessments/{id}`, `POST /assessments/{id}/answers` | **Fully supported** (Multiple Choice only) | Adaptive question progression. Code execution is intentionally blocked/coming soon per security policy. |
| `/assessments/:id/results` | Assessment results breakdown | `GET /assessments/{id}/results` | **Fully supported** | Score, correct answers, topic performance |
| `/assessments/history` | List user attempts | `GET /assessment-attempts` | **Fully supported** | Complete log of quiz attempts |
| `/goals` | Career & placement goals list | `GET /goals`, `POST /goals` | **Fully supported** | Full CRUD available |
| `/goals/:id` | Goal detail & edit | `GET /goals/{id}`, `PATCH /goals/{id}`, `DELETE /goals/{id}` | **Fully supported** | Full CRUD available |
| `/placement` | Job placement matches list | `GET /placement/matches`, `POST /placement/matches` | **Fully supported** | Match evaluation against skills |
| `/placement/:matchId` | Job match detail & skill gaps | `GET /placement/matches/{matchId}` | **Fully supported** | Gap breakdown & matched skills |
| `/roadmaps` | Learning roadmaps list | `GET /roadmaps`, `POST /roadmaps` | **Fully supported** | Generator service available |
| `/roadmaps/:id` | Roadmap detail & milestones | `GET /roadmaps/{id}`, `PATCH /roadmaps/{id}`, `POST /roadmaps/{id}/milestones`, `PATCH /roadmaps/{id}/milestones/{mId}` | **Fully supported** | Milestone progression |
| `/integrations` | External account connectors | `GET /integrations/github/connect`, `GET /integrations/github/repositories`, `POST /integrations/github/repositories`, `DELETE /integrations/github/connection` | **Partially supported** | GitHub OAuth and repo listing are supported. LinkedIn has no backend endpoints (`/profile-sources`), so LinkedIn remains on mock UI. |
| `/progress` | Long-term capability trend | `GET /workspace/summary`, `GET /activity`, `GET /capabilities` | **Partially supported** | Reconstructed from activities & capabilities; no dedicated timeseries endpoint exists. |
| `/assistant` | AI Assistant chat | `POST /assistant/messages`, `GET /assistant/conversations`, `GET /assistant/conversations/{id}`, `DELETE /assistant/conversations/{id}` | **Fully supported** | Context-aware chat session |
| `/design-system` | Visual component library | None | **Fully supported** | Visual reference only |

### Classification Summary:
- **Fully Supported:** 25 screens
- **Partially Supported:** 4 screens (`/settings`, `/integrations`, `/progress`, `/assessments/:id` code execution portion)
- **Not Supported by Backend:** 0 screens (no entirely unsupported module, only missing sub-features such as LinkedIn OAuth and standalone timeseries metrics).

