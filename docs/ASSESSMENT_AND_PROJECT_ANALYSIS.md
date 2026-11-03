# Kynetic — Assessment and Project Analysis Design

## 1. Purpose
Define how Kynetic combines resumes, adaptive assessments, and project evidence to estimate capabilities and recommend what to learn.

## 2. Three Evidence Categories

### Resume/profile claims
Skills, education, certifications, internships, and projects listed by the user. Useful context, but not proof of proficiency.

### Assessment evidence
Quiz answers, coding test results, topic coverage, difficulty, and repeated attempts. Evidence of demonstrated knowledge within the scope tested.

### Project evidence
Repository README/source/dependencies/tests/documentation and user-confirmed contributions. Evidence of practical exposure; repository presence alone does not prove authorship or mastery.

## 3. Adaptive Assessment Flow
1. Select candidate skills from resume, profile, goal, or user-selected topics.
2. Show topics to be assessed.
3. Choose baseline difficulty from evidence or user choice.
4. Present a question.
5. Evaluate answer.
6. Update topic estimate using accumulated evidence.
7. Select next difficulty/topic.
8. Stop when coverage is sufficient, user ends, or configured limit is reached.
9. Save attempt, result, feedback, and coverage.
10. Update capability evidence and explain uncertainty.

### Initial difficulty rules
- Strong performance across enough questions can move toward harder questions.
- Repeated difficulty can move toward easier questions or prerequisite topics.
- One answer must not cause a major proficiency change.
- Evidence is topic-specific.
- Rules must be configurable and testable; backend owns progression.

## 4. Assessment Modes
**Practice:** user chooses topics/difficulty; hints and explanations may be available; results are marked practice.

**Assessment:** structured questions and consistent scoring; results are saved as assessment evidence.

## 5. Question Types
Multiple choice, multi-select, true/false where useful, output prediction, debugging, code comprehension, conceptual response with rubric, and coding challenges evaluated with test cases. Each question needs topic tags, difficulty, source/ownership, evaluation method, and version metadata.

## 6. External Coding Platforms and Content Rights
LeetCode and HackerRank are examples of familiar platforms, not assumed content providers. Do not scrape or copy their question banks. Use permitted APIs/integrations, licensed content, links to original challenges, or original Kynetic questions. Verify provider terms before implementation.

## 7. Coding Evaluation Safety
Never execute submissions in FastAPI or the ordinary application server. Use a dedicated isolated runner/provider with strict CPU, memory, wall-time, process, filesystem, and network limits. The runner must not access application secrets or other users' data. Complete a threat review before enabling arbitrary code execution.

## 8. Capability Profile Output
For each skill show name, estimated band/score, evidence types, assessment topics/coverage, recent evidence date, confidence/uncertainty, and suggested next action. Do not claim mastery from insufficient evidence.

## 9. Project Analysis Workflow

### Inputs
Manual project name/description, project idea/outcome, public repository URL, private repository after explicit authorization, or uploaded documentation/files where supported.

### Analysis
- Identify purpose and intended users.
- Extract stated features and requirements.
- Inspect available repository structure and relevant files.
- Identify languages, frameworks, dependencies, architecture, tests, and setup.
- Summarize implemented, incomplete, or unclear parts.
- Identify skills/concepts needed to build, understand, or extend the project.
- Compare requirements with saved capability evidence.

### Output
Project summary; requirements/features; technologies; architecture/implementation summary; skills supported by evidence; missing/unverified skills; prerequisites and learning recommendations; implementation milestones; evidence sources and limitations.

Separate facts observed in repository files from inferred requirements and assumptions needing confirmation. Do not claim the user authored all code just because a repository was connected.

## 10. Illustrative Project Skill Gap
An AI-powered web application may require programming fundamentals, backend/API development, database design, frontend development, AI/LLM integration, testing, and deployment. These are examples only; recommendations depend on the actual project scope and user evidence.

## 11. Recommendation Principles
Prioritize gaps relevant to the selected goal, explain why each topic matters, include prerequisites and practical exercises, let users accept/dismiss/edit/reorder recommendations, and update recommendations when new evidence is saved.
