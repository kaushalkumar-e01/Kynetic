# Kynetic — API Contract (Initial)

This is the initial REST contract proposal between Next.js and FastAPI, not a claim that endpoints already exist.

## 1. General Rules
- Base path: `/api/v1`
- HTTPS in deployed environments.
- JSON except file uploads.
- Validate all input; authenticate protected routes; enforce ownership.
- Paginate collections and use ISO 8601 UTC timestamps.
- Long-running AI tasks return a job ID/status.

## 2. Authentication
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `POST /auth/refresh` (only if required by selected auth design)
- `GET /auth/me`

Agree on secure session design before implementation. Prefer secure HttpOnly, SameSite cookies where compatible. Do not store long-lived privileged tokens in localStorage.

## 3. Profile and Workspace
- `GET /profile`
- `PATCH /profile`
- `GET /workspace/summary`
- `GET /activity`
- `GET /settings`
- `PATCH /settings`

Workspace summary returns only the authenticated user's recent activity, goals, roadmap progress, assessment summaries, and recommendations.

## 4. Resume
- `POST /resumes` — multipart upload; validate size/type and store privately.
- `GET /resumes`
- `GET /resumes/{resume_id}`
- `DELETE /resumes/{resume_id}`
- `POST /resumes/{resume_id}/analyze` — create analysis job.
- `GET /resumes/{resume_id}/analysis`
- `GET /resume-analyses/{analysis_id}`

Analysis distinguishes extracted claims from verified assessment evidence.

## 5. Skills and Capabilities
- `GET /skills`
- `GET /capabilities`
- `GET /capabilities/{skill_id}`
- `GET /evidence`
- `POST /evidence` — user-confirmed evidence where supported.

Return estimate, confidence/coverage, evidence categories, and last evaluation where available.

## 6. Assessments
- `GET /assessment-topics`
- `GET /questions` — permitted question content/metadata only.
- `POST /assessments`
- `GET /assessments`
- `GET /assessments/{assessment_id}`
- `POST /assessments/{assessment_id}/answers`
- `POST /assessments/{assessment_id}/code-submissions`
- `GET /assessments/{assessment_id}/results`
- `GET /assessment-attempts`

Backend owns question selection and difficulty progression. Never send answer keys or hidden tests to the browser. Code execution uses a separate sandbox.

## 7. Projects and GitHub
Manual projects:
- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `DELETE /projects/{project_id}`

Analysis:
- `POST /projects/{project_id}/analyze`
- `GET /projects/{project_id}/analyses`
- `GET /project-analyses/{analysis_id}`

GitHub:
- `GET /integrations/github/connect`
- `GET /integrations/github/callback`
- `GET /integrations/github/repositories`
- `POST /integrations/github/repositories`
- `DELETE /integrations/github/connection`

Private repository URLs are not proof of authorization. Check provider authorization server-side and request least-privilege scopes.

## 8. LinkedIn/Profile Sources
- `POST /profile-sources/linkedin` — user-provided details or authorized import.
- `GET /profile-sources`
- `DELETE /profile-sources/{source_id}`

Do not implement unauthorized scraping. Confirm that an integration is available and permitted before adding it.

## 9. Goals, Placement, Roadmaps
Goals:
- `POST /goals`
- `GET /goals`
- `GET /goals/{goal_id}`
- `PATCH /goals/{goal_id}`
- `DELETE /goals/{goal_id}`

Placement:
- `POST /placement/matches`
- `GET /placement/matches`
- `GET /placement/matches/{match_id}`

Roadmaps:
- `POST /roadmaps`
- `GET /roadmaps`
- `GET /roadmaps/{roadmap_id}`
- `PATCH /roadmaps/{roadmap_id}`
- `POST /roadmaps/{roadmap_id}/milestones`
- `PATCH /roadmaps/{roadmap_id}/milestones/{milestone_id}`

Users can access modules independently. A goal or roadmap is not a prerequisite for resume analysis, assessments, or project analysis.

## 10. AI Assistant
- `POST /assistant/messages`
- `GET /assistant/conversations`
- `GET /assistant/conversations/{conversation_id}`
- `DELETE /assistant/conversations/{conversation_id}`

Only use context the authenticated user is authorized to access.

## 11. Background Jobs
- `GET /jobs/{job_id}`

Suggested states: `queued`, `processing`, `completed`, `failed`. A user must not inspect another user's job.

## 12. Standard Error
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request could not be processed.",
    "details": []
  }
}
```
Do not return stack traces, secrets, filesystem paths, or provider credentials.

## 13. Contract Changes
Discuss API changes between frontend/backend developers. Update this document alongside implementation. Agree on fields, validation, status codes, and errors. Use OpenAPI schemas or example payloads to coordinate.
