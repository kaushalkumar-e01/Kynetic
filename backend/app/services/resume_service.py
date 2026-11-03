from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.errors import NotFoundException
from app.models.resume import Resume, ResumeAnalysis
from app.models.skill import Skill, EvidenceRecord, UserCapability
from app.models.activity import UserActivity
from app.services.storage import storage_service
from app.services.resume_parser import extract_text_from_pdf
from app.ai import get_llm_provider


class ResumeService:
    @staticmethod
    def analyze_resume_for_user(resume_id: str, user_id: str, db: Session) -> ResumeAnalysis:
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise NotFoundException("Resume not found or access denied.")

        file_path = storage_service.get_file_path(resume.file_storage_key)
        resume_text = extract_text_from_pdf(file_path)

        llm = get_llm_provider()
        analysis_data = llm.analyze_resume(resume_text)

        analysis = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == resume.id, ResumeAnalysis.user_id == user_id)
            .first()
        )
        if not analysis:
            analysis = ResumeAnalysis(
                user_id=user_id,
                resume_id=resume.id,
            )
            db.add(analysis)

        analysis.status = "completed"
        analysis.extracted_profile = analysis_data.get("extracted_profile", {})
        analysis.strengths = analysis_data.get("strengths", [])
        analysis.suggestions = analysis_data.get("suggestions", [])
        analysis.model_metadata = analysis_data.get("model_metadata", {})
        analysis.completed_at = datetime.now(timezone.utc)

        # Update resume status
        resume.status = "analyzed"

        # Ingest claimed skills and create initial evidence records
        claimed_skills = analysis_data.get("claimed_skills", [])
        for item in claimed_skills:
            skill_name = item.get("name", "").strip()
            category = item.get("category", "concept").strip()
            if not skill_name:
                continue

            canonical_name = skill_name.title() if len(skill_name) > 3 else skill_name.upper()

            # Find or create skill
            skill = db.query(Skill).filter(Skill.canonical_name == canonical_name).first()
            if not skill:
                skill = Skill(canonical_name=canonical_name, category=category)
                db.add(skill)
                db.flush()

            # Add Evidence Record (marked as resume claim with 0.5 confidence)
            evidence = EvidenceRecord(
                user_id=user_id,
                skill_id=skill.id,
                source_type="resume",
                source_record_id=resume.id,
                summary=f"Claimed in resume '{resume.original_filename}'.",
                confidence=0.5,
                quality_metadata={"claimed": True, "verified": False},
            )
            db.add(evidence)

            # Update or create user capability
            capability = (
                db.query(UserCapability)
                .filter(UserCapability.user_id == user_id, UserCapability.skill_id == skill.id)
                .first()
            )
            if not capability:
                capability = UserCapability(
                    user_id=user_id,
                    skill_id=skill.id,
                    estimated_band="claimed",
                    score=50.0,
                    confidence=0.5,
                    evidence_count=1,
                    last_evaluated_at=datetime.now(timezone.utc),
                )
                db.add(capability)
            else:
                capability.evidence_count += 1

        # Audit activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="resume_analyzed",
            related_record_type="resume",
            related_record_id=resume.id,
            details={"skills_extracted": len(claimed_skills)},
        )
        db.add(activity)

        db.commit()
        db.refresh(analysis)
        return analysis


resume_service = ResumeService()

