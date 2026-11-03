# Kynetic — Project Plan

**Tagline:** Turn Ambition Into Capability.

## 1. Product Vision
Kynetic (Knowledge in Motion) is an AI-powered personalized capability-development platform. Its primary focus is helping students and job seekers understand their current capabilities, prepare for internships and placements, and develop the skills needed for career and project goals.

Kynetic is not merely a resume-scoring website, a course website, or a linear step-by-step wizard. It is a persistent personal workspace. Each user has an account where their information, analyses, projects, assessment attempts, goals, roadmaps, and progress are saved and available across logins and devices.

The platform combines three forms of evidence:
1. **Claimed knowledge:** skills and experience described in a resume or profile.
2. **Demonstrated knowledge:** performance in quizzes, coding challenges, and other assessments.
3. **Practical evidence:** technologies, implementation, and contributions demonstrated by projects and repositories.

Kynetic uses this evidence to estimate capabilities, explain uncertainty, identify skill gaps, and recommend useful next actions. Its longer-term vision can expand beyond placements into project building, broader career development, and learning across technology, business, design, finance, science, mathematics, languages, music, and research.

## 2. Problem Statement
Students and early-career job seekers often do not know whether their resume communicates their abilities, whether they can demonstrate claimed skills, which skills matter for a target role, what they should practise first, what a project requires, or how to maintain progress. A resume-only score cannot answer these questions.

## 3. Product Principles

### Persistent workspace
- Every user has an independent account and private workspace.
- Save profile information, resumes, analysis reports, connected sources, projects, assessments, goals, roadmaps, milestones, and activity.
- Users can leave an activity and continue later.
- Data persists on the server/database, not only in browser state or local storage.
- Users should not need to re-enter information after every login.
- Retain useful history and show which source/version an analysis used.

### Flexible, non-linear experience
- Do not force users through a fixed sequence.
- Provide a personalized dashboard with independently accessible modules.
- Users may analyse a resume, take an assessment, inspect a project, explore a role, or continue a roadmap in any order.
- Offer contextual recommendations without locking unrelated features.

### Evidence-based capability estimates
- A resume mention is a claim, not proof of proficiency.
- A single quiz answer must not determine a skill level.
- Combine multiple attempts, question difficulty, topic coverage, project evidence, and user-confirmed information.
- Show why an estimate was assigned and how confident it is.
- Allow users to correct inaccurate extracted information.

### Explainability and user control
- Explain match scores and skill gaps.
- Label AI-generated scores as estimates, not guarantees or employer ATS results.
- Let users inspect, edit, disconnect, or delete connected sources and stored data.
- Ask permission before accessing private repositories or external accounts.

## 4. User Inputs and Evidence Sources

| Source | Possible information | Use |
|---|---|---|
| Resume PDF | Education, skills, experience, projects, certifications | Resume analysis and initial skill claims |
| GitHub account/repository | Metadata, README, source files, contributions where authorized | Project and practical evidence |
| LinkedIn profile | User-provided details or authorized import | Experience, education, skills, certifications |
| Manual project details | Description, goals, features, technologies | Project analysis |
| Quizzes | Answers, topic coverage, correctness | Conceptual knowledge evidence |
| Coding challenges | Submitted code, test results, category and difficulty | Programming/problem-solving evidence |
| Job description | Role and required/preferred skills | Placement matching |
| User goals | Target role, project ambition, timeline | Recommendations and roadmap |

External platform access must follow current terms, API permissions, and licensing. Do not scrape LinkedIn or copy/redistribute LeetCode or HackerRank question banks without authorization. Where direct integration is unavailable, accept user-provided information or link to the original challenge.

## 5. Core Product Modules

### 5.1 Authentication and account management
Registration, login, logout, password reset, session management, secure user-specific authorization, profile preferences, and privacy controls.

### 5.2 Personalized dashboard
Show saved workspace summaries, current goals, recent activity, assessment summaries, project analyses, roadmap progress, and recommendations. Provide navigation to independent modules. Show where the user last left off without forcing them to resume it. Include useful empty states.

### 5.3 Resume intelligence
- Upload PDF resumes initially; validate any additional formats before supporting them.
- Extract education, experience, skills, certifications, and projects.
- Identify strengths, missing details, unclear claims, and improvement suggestions.
- Preserve resume versions and associate each analysis with its source version.
- Identify skills that could be verified through assessments.
- Let users review and correct extracted information.

### 5.4 Adaptive skill assessment
Assessment types: multiple-choice/multi-select quizzes, conceptual questions, code/output prediction, debugging, and coding challenges.

Difficulty progression:
- Organize questions into Easy, Medium, and Hard.
- Start with a baseline based on available evidence or user choice.
- Increase difficulty when performance demonstrates readiness.
- Reduce difficulty or change topic when the user struggles.
- Use multiple questions and topic coverage before estimating proficiency.
- Support practice and assessment modes.
- Save every attempt and allow review.

Evaluation signals can include correctness, test results, topic coverage, difficulty, consistency, and time/efficiency only where relevant. Do not equate speed with knowledge by itself. Display coverage and limitations.

Question sourcing:
- Prefer original Kynetic questions or properly licensed content.
- Use external APIs/integrations only where permitted, or link to original LeetCode/HackerRank challenges.
- Do not scrape, copy, or redistribute protected question banks without permission.
- Store provider identifiers and links where permitted rather than duplicating restricted content.

Coding execution:
- Run submissions only in a separate isolated, resource-limited sandbox.
- Never execute user code directly on the application server.
- Apply time, memory, process, filesystem, and network restrictions.
- Keep execution infrastructure separate from the main API.

### 5.5 Capability profile
Combine resume/profile claims, quiz/coding evidence, project/repository evidence, and user-confirmed experience. For each skill, show a proficiency band/estimate, confidence, evidence sources, assessment coverage, last evaluated date, and user notes. Distinguish claimed, assessed, project-supported, and unverified skills. Do not imply AI estimates are formal certifications.

### 5.6 GitHub and project intelligence
Users may connect GitHub or add a repository URL. Private repository access requires explicit authorization and least-privilege scopes. Inspect accessible metadata, README/documentation, structure, relevant source files, dependencies, tests, and authorized contribution information.

Explain project purpose, features, technologies, architecture, skills supported by available evidence, missing/incomplete/unclear requirements, concepts needed to understand or extend the project, and possible improvements. Do not claim the user personally implemented all repository code based only on repository access.

### 5.7 Project requirement and learning analysis
Users can provide an existing project, idea, or repository. Kynetic should understand its goal, identify expected features and technical requirements, identify technologies/prerequisites, compare these with the saved capability profile, separate supported skills from missing or unverified skills, and recommend learning topics, exercises, and implementation milestones. Save the analysis for later. Distinguish repository facts from requirements inferred from a description.

### 5.8 LinkedIn profile information
Accept user-provided profile information. Use an authorized integration only if available and permitted. Store source/import date/confirmation status. Do not scrape LinkedIn or bypass access controls. Allow editing/removal.

### 5.9 Placement and job matching
Let users select a target role or paste a job description. Extract required/preferred skills, compare against capability evidence, explain matched/partial/missing/unverified skills, and save multiple job matches. Scores are estimates, not guarantees of selection or employer ATS results.

### 5.10 Skill gap analysis
Consider role-relevant areas such as programming, DSA, OOP, DBMS, OS, networks, web development, AI/ML, software engineering/testing, practical projects, communication, and interviews. Do not assume every user needs every topic.

### 5.11 Personalized learning roadmaps
Generate plans from the user's evidence and goal. Break work into topics, activities, milestones, and practical tasks. Recommend resources and exercises. Support user timelines. Save progress. Allow editing, pausing, resuming, and regeneration. Update recommendations when new evidence arrives.

### 5.12 AI learning assistant
Answer questions using relevant saved user context when authorized, explain concepts, help with coding/project decisions, and recommend next actions. Never expose another user's data.

### 5.13 Progress and analytics
Show assessment history, topic performance, capability changes with evidence, roadmap milestones, and project tasks. Distinguish self-reported from assessed progress.

## 6. User Experience and Navigation
Kynetic is a personalized workspace, not a forced wizard. Suggested navigation:
- Dashboard
- My Profile / Capability Profile
- Resume Analysis
- Skill Assessments
- Projects
- GitHub Connections
- Placement & Job Matches
- Learning Roadmaps
- Progress & Analytics
- AI Assistant
- Settings & Privacy

Users may enter any available module directly. Each module preserves its state and history.

## 7. Technology Stack
- Frontend: Next.js, React, TypeScript, Tailwind CSS.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy.
- Database: PostgreSQL; Alembic migrations.
- Storage: private object/file storage for resumes and permitted artifacts.
- AI: provider-independent LLM service layer where practical; embeddings/RAG where useful.
- Assessment: question/assessment service and isolated code-execution service.
- Integrations: GitHub API; LinkedIn only through authorized options or user-provided data; external learning resources; MCP/coding agents in later phases.

## 8. Development Phases
Phases are implementation priorities, not a mandatory sequence imposed on end users.

### Phase 0 — Foundation
Confirm requirements/architecture, create repository/docs, agree API contract/workflow, configure environments.

### Phase 1 — Persistent application foundation
Frontend/backend skeletons, database/migrations, authentication, profile, persistent user-owned data, personalized dashboard shell, authorization and isolation tests.

### Phase 2 — Resume and profile intelligence
Private resume upload, parsing, AI analysis, user review/correction, initial capability profile and evidence.

### Phase 3 — Adaptive assessments
Topics/questions, quiz interface/APIs, Easy/Medium/Hard adaptation, coding workflow, isolated execution, attempt history, evidence-based capability updates.

### Phase 4 — Project and GitHub intelligence
Manual project input, GitHub authorization, permitted repository analysis, project reports, project-to-capability gap comparison.

### Phase 5 — LinkedIn and profile sources
User-provided profile details and authorized integration only where available.

### Phase 6 — Placement matching
Target roles, job description extraction, evidence-aware matching, explainable gaps, saved matches.

### Phase 7 — Roadmaps, assistant, progress
Roadmap generation, resources/practice, milestone tracking, analytics, context-aware assistant.

### Phase 8 — Advanced ecosystem
MCP, coding-agent workflows, additional integrations, broader domains and goals.

## 9. Initial Repository Structure
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

## 10. Team Responsibilities
### Project Coordinator — repository, documentation, integration
Maintain repository/docs, coordinate tasks/milestones, track API changes, coordinate PRs, test end-to-end flows and user isolation, keep `main` stable.

### Backend and AI Developer
FastAPI, database/migrations, authentication/authorization, persistent workspace, resume analysis, adaptive assessment, safe coding evaluation, GitHub and permitted profile integrations, project analysis, matching, roadmap APIs, tests and API docs.

### Frontend Developer
Next.js UI, landing/authentication, persistent dashboard/navigation, resume, assessment, project/GitHub, capability, placement, roadmap, analytics, settings, API integration, responsive/loading/error/empty states.

All members agree on API contracts before implementing dependent features.

## 11. MVP Definition
1. User registers and logs in.
2. Account/profile persist across sessions.
3. Dashboard loads saved user data.
4. User uploads and analyses a resume.
5. Extracted skills are shown as claims and can be reviewed.
6. User completes at least one topic-based adaptive quiz.
7. Attempts are saved and contribute evidence to a capability profile.
8. User adds a project description or permitted GitHub repository.
9. Kynetic summarizes the project and identifies relevant skills to learn.
10. User selects a target role or provides a job description.
11. System explains skill gaps and saves a roadmap.
12. User logs out and later returns to find data and progress intact.

The first release need not include every integration or assessment category. Build a reliable foundation and expand incrementally.

## 12. Definition of Done
A feature must have a documented API contract, persist required data, enforce authentication/ownership, handle loading/empty/validation/error states, include appropriate tests, protect secrets/private data, and pass integration checks.

## 13. Security, Privacy, and Responsible AI
- Enforce user ownership in backend APIs.
- Store secrets in environment variables/secret manager; never commit them.
- Validate files and store them privately.
- Use least-privilege GitHub scopes.
- Do not scrape LinkedIn or bypass provider controls.
- Respect coding platform terms and content licensing.
- Never execute user code in the main application process.
- Treat documents/repository content as untrusted input and protect against prompt injection.
- Define data retention/deletion behavior.
- Do not log resumes, tokens, passwords, or private source code.
- Explain limitations of AI capability and job-match estimates.

## 14. Final Goal
Build Kynetic as a persistent, personalized AI workspace that understands what users claim to know, tests what they can demonstrate, analyses what they have built, identifies what they need for their goals, and helps them continue improving over time.

**Kynetic — Turn Ambition Into Capability.**
