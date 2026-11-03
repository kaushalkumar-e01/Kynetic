import re
from sqlalchemy.orm import Session

from app.models.goal import JobMatch
from app.models.skill import UserCapability
from app.models.activity import UserActivity

JOB_SKILL_PATTERNS = {
    # Core engineering & languages
    "python": "language", "javascript": "language", "typescript": "language", "golang": "language",
    "java": "language", "c++": "language", "c#": "language", "rust": "language", "sql": "language",
    # Frameworks & libraries
    "fastapi": "framework", "django": "framework", "flask": "framework", "react": "framework",
    "next.js": "framework", "node": "framework", "express": "framework", "spring boot": "framework",
    # Databases & Caching
    "postgresql": "database", "mysql": "database", "redis": "database", "mongodb": "database",
    # DevOps & Infrastructure
    "docker": "devops", "kubernetes": "devops", "aws": "cloud", "ci/cd": "devops", "git": "tool",
    # Concepts
    "data structures": "concept", "algorithms": "concept", "rest api": "concept",
    "microservices": "concept", "system design": "concept", "oop": "concept",
}


class MatchingService:
    @staticmethod
    def match_job_description(
        user_id: str,
        role_title: str,
        job_description: str,
        goal_id: str = None,
        source_reference: str = None,
        db: Session = None,
    ) -> JobMatch:
        text_lower = job_description.lower()

        # 1. Extract required skills from description
        detected_reqs = []
        for kw, cat in JOB_SKILL_PATTERNS.items():
            pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
            if re.search(pattern, text_lower):
                detected_reqs.append({
                    "skill": kw.title() if len(kw) > 3 else kw.upper(),
                    "category": cat,
                })

        if not detected_reqs:
            detected_reqs = [
                {"skill": "Python", "category": "language"},
                {"skill": "REST API", "category": "concept"},
                {"skill": "SQL", "category": "language"},
            ]

        # 2. Query user's current capabilities
        user_caps = db.query(UserCapability).filter_by(user_id=user_id).all()
        user_cap_map = {c.skill.canonical_name.lower(): c for c in user_caps if c.skill}

        matched_skills = []
        partial_skills = []
        missing_skills = []

        for req in detected_reqs:
            s_name = req["skill"]
            s_key = s_name.lower()

            if s_key in user_cap_map:
                cap = user_cap_map[s_key]
                if cap.score >= 60.0:
                    matched_skills.append({
                        "skill": s_name,
                        "category": req["category"],
                        "status": "matched",
                        "user_score": cap.score,
                        "band": cap.estimated_band,
                    })
                else:
                    partial_skills.append({
                        "skill": s_name,
                        "category": req["category"],
                        "status": "partial",
                        "user_score": cap.score,
                        "band": cap.estimated_band,
                    })
            else:
                missing_skills.append({
                    "skill": s_name,
                    "category": req["category"],
                    "status": "missing",
                    "user_score": 0.0,
                    "band": "unverified",
                })

        total = len(detected_reqs)
        score_val = (len(matched_skills) * 1.0 + len(partial_skills) * 0.5) / total * 100.0
        final_score = round(score_val, 1)

        limitations = [
            "Match scores are capability estimates based solely on saved evidence, not a guaranteed employer ATS outcome.",
            "Demonstrated assessment evidence provides significantly higher reliability than resume self-claims.",
            "Unverified and missing skills can be tested through Kynetic assessments or demonstrated in projects.",
        ]

        extracted_requirements = {
            "total_skills_detected": total,
            "skills": [r["skill"] for r in detected_reqs],
        }

        match_breakdown = {
            "matched_skills": matched_skills,
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "matched_count": len(matched_skills),
            "partial_count": len(partial_skills),
            "missing_count": len(missing_skills),
        }

        # Persist JobMatch
        job_match = JobMatch(
            user_id=user_id,
            goal_id=goal_id,
            role_title=role_title,
            job_description=job_description,
            source_reference=source_reference,
            extracted_requirements=extracted_requirements,
            match_breakdown=match_breakdown,
            estimated_score=final_score,
            limitations=limitations,
        )
        db.add(job_match)

        # Audit activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="job_matched",
            related_record_type="job_match",
            details={"role": role_title, "match_score": final_score},
        )
        db.add(activity)

        db.commit()
        db.refresh(job_match)
        return job_match


matching_service = MatchingService()

