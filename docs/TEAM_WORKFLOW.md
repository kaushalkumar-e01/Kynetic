# Kynetic — Team Workflow

## 1. Team Structure

### Project Coordinator — repository, documentation, integration
- Maintain repository and documentation.
- Coordinate tasks and milestones.
- Track API contract changes.
- Coordinate integration testing, PRs, and releases.
- Verify end-to-end flows and user isolation.
- Keep `main` stable.

### Backend and AI Developer
- FastAPI, database schema, migrations, authentication, and authorization.
- Persistent workspace and user data isolation.
- Resume analysis and adaptive assessment.
- Safe coding evaluation integration.
- GitHub and permitted profile integrations.
- Project analysis, placement matching, and roadmap APIs.
- Backend tests and API documentation.

### Frontend Developer
- Next.js app, landing/authentication, personalized dashboard/navigation.
- Resume, assessment, project, capability, placement, roadmap, analytics, and settings screens.
- API integration, responsive design, loading/error/empty states.

## 2. Branch Strategy
- `main`: stable reviewed code.
- `develop`: shared integration.
- `feature/backend-foundation`: backend foundation.
- `feature/frontend-foundation`: frontend foundation.
- `docs/<short-description>`: documentation.

Do not commit directly to `main`. If `main` has no commit, first commit the project foundation on an agreed initial branch, merge it, then create `develop` from `main`. Feature branches normally start from `develop` and merge back through PRs.

## 3. Collaboration Rules
- Pull the latest agreed base before starting.
- Work in owned folders where possible.
- Coordinate changes to shared files/API contracts.
- Never commit `.env`, credentials, personal resumes, uploaded files, database dumps, or generated secrets.
- Keep commits focused and descriptive.
- PRs include summary, testing notes, and screenshots where useful.
- Review before merging; coordinate conflict resolution.

## 4. Parallel Work
Before dependent work begins, agree on endpoint names/methods, request/response schemas, authentication/session design, error format, CORS/local origins, and shared terminology. Frontend may use clearly labelled mock data until APIs are ready.

## 5. Suggested First Milestone

### Backend
- FastAPI skeleton.
- PostgreSQL and Alembic.
- Register/login/logout/current-user endpoints.
- Profile read/update.
- User ownership checks.
- Tests proving one user cannot access another user's records.
- OpenAPI documentation.

### Frontend
- Next.js skeleton.
- Landing and authentication pages.
- Persistent dashboard shell/navigation.
- Shared API client and session handling.
- Profile page and dashboard empty states.
- Mock data only where APIs are not ready.

### Integration acceptance test
1. Register a user.
2. Log in.
3. Create/update profile.
4. View personalized dashboard.
5. Log out and log in again.
6. Confirm profile/workspace data remains.
7. Confirm a different user cannot access the first user's private records.

## 6. Definition of Ready for Integration
Feature owner has tested locally; environment variables are documented without real secrets; API contract is updated; authorization and validation exist; errors/empty states are handled; tests pass or known gaps are documented; no private data or secrets are included.
