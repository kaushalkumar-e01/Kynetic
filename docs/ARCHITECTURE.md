# Kynetic — Architecture Overview

## 1. Goals
Kynetic should be a persistent multi-user application with independently accessible modules, evidence-aware AI, secure authorization, and extensible integrations. Start with a modular FastAPI application; do not prematurely split into microservices.

## 2. Logical Architecture
```text
Browser
  |
Next.js / React Frontend
  | HTTPS / JSON REST API
FastAPI Backend
  +-- Authentication & Authorization
  +-- User Workspace / Profile
  +-- Resume Analysis
  +-- Assessment
  +-- Capability & Evidence
  +-- Project / GitHub Analysis
  +-- Placement Matching
  +-- Roadmap & Progress
  +-- AI Provider Abstraction
  |
  +-- PostgreSQL
  +-- Private Object Storage
  +-- Background Job Worker
  +-- Isolated Code Execution Service (separate security boundary)
  +-- Authorized External APIs
```

## 3. Frontend
Render the personalized workspace, call APIs through a shared client, display backend-saved data, and handle loading/empty/success/error states. Browser state is for temporary UI state, not the source of truth for user records. Never put privileged API keys in client code.

## 4. Backend
Authenticate and authorize users, validate requests/uploads, persist data, coordinate AI/background jobs, maintain evidence and capability estimates, and enforce ownership on every user-owned resource.

## 5. Persistence and Resume-Where-You-Left-Off
PostgreSQL is the source of truth for structured records. Private object storage holds files. Persist profiles, resume versions/analyses, connected accounts, projects/reports, assessment sessions/attempts, skills/evidence/capabilities, goals/matches, roadmaps/milestones, and useful activity. On login, fetch the authenticated user's workspace summary. Save in-progress activities through backend APIs; do not rely on browser storage alone.

## 6. AI Service Design
Use a provider-independent service layer where practical. Keep prompts, provider calls, validation, retries, and model configuration out of route handlers. Validate AI outputs against schemas, store source references/timestamps, mark estimates, and allow user review. Treat documents and repository content as untrusted input; do not let embedded instructions override system rules or trigger arbitrary tools.

## 7. Background Work
For long tasks: validate request, create owned job, return job ID/status, process in worker, save result/status, and let frontend fetch the result. Choose queue technology after evaluating need and hosting complexity.

## 8. Coding Assessment Isolation
Never execute submissions inside FastAPI or the ordinary app server. Use a dedicated isolated runner/provider with strict CPU, memory, wall-time, process, filesystem, and network limits. Runner must not access application secrets, database credentials, or other users' data.

## 9. External Integrations
- **GitHub:** official API/OAuth or app authorization, least privilege, explicit private-repository permission, server-side token storage, disconnect support.
- **LinkedIn:** user-provided details or authorized integration only; no scraping or access-control bypass.
- **Coding platforms:** permitted API/integration, licensed content, original questions, or links to provider challenges; no unauthorized copying.

## 10. Security Boundaries
Frontend is untrusted; every protected API needs authentication and ownership checks. Files, repository content, AI output, and code submissions are untrusted. Code execution is a separate restricted environment. Secrets are server-side only.
