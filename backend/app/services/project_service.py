import re
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.errors import NotFoundException
from app.models.project import Project, ProjectAnalysis, ConnectedAccount
from app.models.skill import Skill, EvidenceRecord, UserCapability
from app.models.activity import UserActivity
from app.services.repo_inspector import repo_inspector

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

        # Check for GitHub Connected Account token
        access_token = None
        conn = db.query(ConnectedAccount).filter_by(user_id=user_id, provider="github").first()
        if conn and conn.encrypted_token:
            access_token = conn.encrypted_token

        detected_tech = []
        demonstrated_skills = []
        major_features = []
        strengths = []
        missing_reqs = []
        recommendations = []
        inspected_files = []
        arch_summary = ""
        purpose = ""
        is_code_verified = False

        # If repository URL is present and contains github.com
        if project.repository_url and "github.com" in project.repository_url:
            try:
                inspection = repo_inspector.inspect_repository(
                    repository_url=project.repository_url,
                    access_token=access_token,
                )
                if inspection.get("accessible", True) and inspection.get("detected_technologies"):
                    is_code_verified = True
                    purpose = inspection.get("purpose") or ""
                    detected_tech = inspection.get("detected_technologies", [])
                    arch_summary = inspection.get("architecture_summary", "")
                    demonstrated_skills = inspection.get("demonstrated_skills", [])
                    major_features = inspection.get("major_features", [])
                    strengths = inspection.get("technical_strengths", [])
                    missing_reqs = inspection.get("missing_requirements", [])
                    recommendations = inspection.get("recommendations", [])
                    inspected_files = inspection.get("inspected_files", [])
            except Exception:
                pass

        # If not code verified, fall back to manual metadata + keyword detection
        if not is_code_verified:
            manual_techs = []
            if project.access_metadata and isinstance(project.access_metadata, dict):
                manual_techs = project.access_metadata.get("technologies", [])

            text_content = f"{project.name} {project.description or ''}".lower()
            detected = set(manual_techs)
            for keyword, cat in TECH_KEYWORDS.items():
                pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
                if re.search(pattern, text_content):
                    detected.add(keyword.title() if len(keyword) > 3 else keyword.upper())

            detected_tech = sorted(list(detected))
            if not detected_tech:
                if "api" in text_content or "backend" in text_content:
                    detected_tech.extend(["Python", "FastAPI"])
                if "web" in text_content or "frontend" in text_content:
                    detected_tech.append("React")

            purpose = f"Technical project: {project.name}. {project.description or 'Custom application build.'}"
            arch_summary = (
                f"Application utilizing {', '.join(detected_tech[:4]) or 'modern technologies'}. "
                f"Source mode: {project.source_type.title()}."
            )
            demonstrated_skills = detected_tech.copy()
            if "Python" in detected_tech:
                demonstrated_skills.append("Object-Oriented Programming")
            if any(d in detected_tech for d in ["FastAPI", "Express", "Django"]):
                demonstrated_skills.append("REST API Design")

            major_features = [
                f"Core service architecture built with {', '.join(detected_tech[:3]) or 'specified stack'}.",
                "Modular component structure and data handling layer.",
                "Custom business logic implementation.",
            ]
            strengths = [
                f"Demonstrated technology stack: {', '.join(detected_tech[:4]) or 'project architecture'}.",
                "Modular structural organization.",
            ]
            missing_reqs = [
                "Comprehensive automated test coverage (unit & integration tests).",
                "Containerized deployment configuration (Dockerfile / Compose).",
                "Automated CI/CD pipeline definition.",
            ]
            recommendations = [
                "Add automated test suites to validate business logic and edge cases.",
                "Implement Docker containerization for reliable reproducible local execution.",
                "Document API endpoints and architecture design decisions in a README.",
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
        analysis.missing_requirements = missing_reqs
        analysis.recommendations = recommendations
        analysis.source_snapshot = {
            "major_features": major_features,
            "technical_strengths": strengths,
            "inspected_files": inspected_files,
            "is_code_verified": is_code_verified,
        }
        analysis.completed_at = datetime.now(timezone.utc)

        # Ingest practical project evidence into UserCapability
        evidence_confidence = 0.7
        target_score = 75.0 if is_code_verified else 65.0
        target_band = "foundational" if is_code_verified else "claimed"

        for skill_name in demonstrated_skills:
            canonical = skill_name.title() if len(skill_name) > 3 else skill_name.upper()
            skill = db.query(Skill).filter_by(canonical_name=canonical).first()
            if not skill:
                skill = Skill(canonical_name=canonical, category="concept")
                db.add(skill)
                db.flush()

            summary_text = (
                f"Verified repository code in '{project.name}' (inspected {len(inspected_files)} manifests/source files)."
                if is_code_verified
                else f"Project stack evidence reported in '{project.name}'."
            )
            evidence = EvidenceRecord(
                user_id=user_id,
                skill_id=skill.id,
                source_type="project",
                source_record_id=project.id,
                summary=summary_text,
                confidence=evidence_confidence,
                quality_metadata={
                    "source_type": project.source_type,
                    "project_name": project.name,
                    "code_verified": is_code_verified,
                    "files_count": len(inspected_files),
                },
            )
            db.add(evidence)

            capability = db.query(UserCapability).filter_by(user_id=user_id, skill_id=skill.id).first()
            if not capability:
                capability = UserCapability(
                    user_id=user_id,
                    skill_id=skill.id,
                    estimated_band=target_band,
                    score=target_score,
                    confidence=evidence_confidence,
                    evidence_count=1,
                )
                db.add(capability)
            else:
                capability.evidence_count += 1
                capability.score = round(min(100.0, max(capability.score, target_score)), 1)
                capability.confidence = min(0.95, capability.confidence + 0.05)
                if is_code_verified and capability.estimated_band in ["unverified", "claimed"]:
                    capability.estimated_band = "foundational"

        # Audit activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="project_analyzed",
            related_record_type="project",
            related_record_id=project.id,
            details={
                "project_name": project.name,
                "skills_detected": len(demonstrated_skills),
                "code_verified": is_code_verified,
            },
        )
        db.add(activity)

        db.commit()
        db.refresh(analysis)
        return analysis


project_service = ProjectService()
