# Kynetic — Initial Data Model

This is a logical starting point, not a final SQL schema. Backend developer should refine types, constraints, indexes, and relationships.

## Ownership Rule
Every user-owned record must be associated with its owner directly or through a parent. Backend must enforce ownership on every read, update, and delete.

## Entities

### users
`id`, `email` (unique), `password_hash` or external identity reference, `account_status`, `created_at`, `updated_at`.

### user_profiles
`id`, `user_id`, `display_name`, optional education/experience summary, preferred domains/roles, learning preferences, timestamps.

### resumes
`id`, `user_id`, `file_storage_key`, `original_filename`, `mime_type`, `file_size`, optional version label, upload time, status.

### resume_analyses
`id`, `user_id`, `resume_id`, status, validated extracted profile, strengths, suggestions, created/completed timestamps, model metadata.

### connected_accounts
`id`, `user_id`, provider, provider account ID, encrypted token reference, granted scopes, connected/disconnected timestamps. Never expose plaintext tokens. Do not assume LinkedIn API access exists.

### projects
`id`, `user_id`, name, description, source type (manual/GitHub/other permitted source), optional repository URL, access metadata, timestamps.

### project_analyses
`id`, `user_id`, `project_id`, status, purpose, detected technologies/features, architecture summary, demonstrated skills, missing/unclear requirements, recommendations, source snapshot/reference, timestamps.

### skills
`id`, canonical name, category, optional description.

### evidence_records
`id`, `user_id`, `skill_id`, source type (resume/assessment/project/profile/user-confirmed), source record ID, summary, confidence/quality metadata, observed and created timestamps.

### user_capabilities
`id`, `user_id`, `skill_id`, estimated band/score, confidence, evidence count, last evaluated time, updated time. Keep history in a separate history table or versioned records.

### assessment_topics
`id`, name, optional parent topic, description.

### questions
`id`, topic ID, question type, difficulty (easy/medium/hard), prompt or licensed provider reference, protected answer/evaluation metadata, source attribution, active status.

### assessments
`id`, `user_id`, title, mode (practice/assessment), selected topics, status, start/completion timestamps.

### assessment_attempts
`id`, `user_id`, assessment ID, question ID, submitted answer or submission reference, result/correctness, coding test summary, relevant time metadata, feedback, created time. Do not expose answer keys or hidden tests to clients.

### goals
`id`, `user_id`, goal type (placement/career/project/learning), title, description, optional target date, status, timestamps.

### job_matches
`id`, `user_id`, optional goal ID, role title, job description/source reference, extracted requirements, match breakdown, estimated score, limitations, created time.

### roadmaps
`id`, `user_id`, optional goal ID, title, description, status, generated and updated timestamps.

### roadmap_milestones
`id`, `user_id`, roadmap ID, title, description, resources, ordering, status, optional due/completed times.

### user_activity
`id`, `user_id`, activity type, related record type/ID, metadata, created time.

## Relationships
A user can have many resumes, analyses, connected accounts, projects, evidence records, capability records, assessments/attempts, goals, matches, roadmaps, and milestones. A project or resume can have multiple analysis runs. All child resources require owner checks.

## Privacy and Retention
Keep private files private; use opaque storage keys; define deletion for accounts, files, tokens, and derived analyses; avoid unnecessary personal data; never log resume contents, tokens, passwords, or private source code.
