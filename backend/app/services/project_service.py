import re
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.errors import NotFoundException
from app.models.project import Project, ProjectAnalysis
from app.models.skill import Skill, EvidenceRecord, UserCapability
from app.models.activity import UserActivity

TECH_KEYWORDS = {
    "fastapi": "framework", "django": "framework", "flask": "framework", "react": "framework",
    "next.js": "framework", "vue": "framework", "angular": "framework", "node": "framework",
    "express": "framework", "python": "language", "typescript": "language", "javascript": "language",
    "postgresql": "database", "sqlite": "database", "mysql": "database", "redis": "database",
    "mongodb": "database", "docker": "devops", "kubernetes": "devops", "alembic": "tool",
    "sqlalchemy": "tool", "pytest": "tool", "pydantic": "tool", "jwt": "security",
}


class ProjectService:
    @staticmethod
    def analyze_project(project_id: str, user_id: str, db: Session) -> ProjectAnalysis:
        project = db.query(Project).filter_by(id=project_id, user_id=user_id).first()
        if not project:
            raise NotFoundException("Project not found or access denied.")

        text_content = f"{project.name} {project.description or ''} {project.repository_url or ''}".lower()

        # 1. Detect Technologies
        detected_tech = []
        for keyword, cat in TECH_KEYWORDS.items():
            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
            if re.search(pattern, text_content):
                detected_tech.append(keyword.title() if len(keyword) > 3 else keyword.upper())

        # If minimal, infer basic technologies
        if not detected_tech:
            if "api" in text_content or "backend" in text_content:
                detected_tech.extend(["Python", "FastAPI"])
            if "web" in text_content or "frontend" in text_content:
                detected_tech.append("React")

        purpose = f"Technical software implementation designed for: {project.name}. {project.description or 'Custom application build.'}"
        arch_summary = (
            f"Modular client-server or standalone service utilizing {', '.join(detected_tech[:4]) or 'modern languages'}. "
            f"Repository source: {project.source_type.title()}."
        )

        demonstrated_skills = detected_tech.copy()
        if "Python" in detected_tech:
            demonstrated_skills.append("Object-Oriented Programming")
        if any(d in detected_tech for d in ["FastAPI", "Express", "Django"]):
            demonstrated_skills.append("REST API Design")

        missing_requirements = [
            "Comprehensive automated unit and end-to-end integration test suites.",
            "Containerized Dockerfile and CI/CD deployment configuration pipeline.",
            "API documentation specification (OpenAPI / Swagger) and architectural diagrams.",
        ]

        recommendations = [
            "Add unit tests using pytest or jest to verify core business logic.",
            "Include a detailed README detailing system architecture, prerequisites, and setup instructions.",
            "Implement containerization with Docker for reproducible deployment environments.",
        ]

        # Create or update analysis record
        analysis = db.query(ProjectAnalysis).filter_by(project_id=project.id, user_id=user_id).first()
        if not analysis:
            analysis = ProjectAnalysis(project_id=project.id, user_id=user_id)
            db.add(analysis)

        analysis.status = "completed"
        analysis.purpose = purpose
        analysis.detected_technologies = detected_tech
        analysis.architecture_summary = arch_summary
        analysis.demonstrated_skills = demonstrated_skills
        analysis.missing_requirements = missing_requirements
        analysis.recommendations = recommendations
        analysis.completed_at = datetime.now(timezone.utc)

        # Ingest practical project evidence
        for skill_name in demonstrated_skills:
            canonical = skill_name.title() if len(skill_name) > 3 else skill_name.upper()
            skill = db.query(Skill).filter_by(canonical_name=canonical).first()
            if not skill:
                skill = Skill(canonical_name=canonical, category="concept")
                db.add(skill)
                db.flush()

            # Record evidence
            evidence = EvidenceRecord(
                user_id=user_id,
                skill_id=skill.id,
                source_type="project",
                source_record_id=project.id,
                summary=f"Practical implementation evidence observed in project '{project.name}'.",
                confidence=0.7,
                quality_metadata={"source_type": project.source_type, "project_name": project.name},
            )
            db.add(evidence)

            # Update capability
            capability = db.query(UserCapability).filter_by(user_id=user_id, skill_id=skill.id).first()
            if not capability:
                capability = UserCapability(
                    user_id=user_id,
                    skill_id=skill.id,
                    estimated_band="claimed",
                    score=65.0,
                    confidence=0.7,
                    evidence_count=1,
                )
                db.add(capability)
            else:
                capability.evidence_count += 1
                capability.score = round(min(100.0, max(capability.score, 65.0)), 1)
                capability.confidence = min(0.95, capability.confidence + 0.05)

        # Audit activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="project_analyzed",
            related_record_type="project",
            related_record_id=project.id,
            details={"project_name": project.name, "skills_detected": len(demonstrated_skills)},
        )
        db.add(activity)

        db.commit()
        db.refresh(analysis)
        return analysis


project_service = ProjectService()

