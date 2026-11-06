import re
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.goal import JobMatch
from app.models.skill import UserCapability, EvidenceRecord
from app.models.activity import UserActivity
from app.ai.factory import get_llm_provider

JOB_SKILL_PATTERNS = {
    # Core engineering & languages
    "python": ("Python", "language"),
    "javascript": ("JavaScript", "language"),
    "typescript": ("TypeScript", "language"),
    "golang": ("Go", "language"),
    "go": ("Go", "language"),
    "java": ("Java", "language"),
    "c++": ("C++", "language"),
    "c#": ("C#", "language"),
    "rust": ("Rust", "language"),
    "sql": ("SQL", "language"),
    "html": ("HTML", "language"),
    "css": ("CSS", "language"),
    # Frameworks & libraries
    "fastapi": ("FastAPI", "framework"),
    "django": ("Django", "framework"),
    "flask": ("Flask", "framework"),
    "react": ("React", "framework"),
    "next.js": ("Next.js", "framework"),
    "nextjs": ("Next.js", "framework"),
    "node": ("Node.js", "framework"),
    "node.js": ("Node.js", "framework"),
    "express": ("Express.js", "framework"),
    "express.js": ("Express.js", "framework"),
    "spring boot": ("Spring Boot", "framework"),
    "vue": ("Vue.js", "framework"),
    "angular": ("Angular", "framework"),
    "tailwind": ("Tailwind CSS", "framework"),
    # Databases & Caching
    "postgresql": ("PostgreSQL", "database"),
    "postgres": ("PostgreSQL", "database"),
    "mysql": ("MySQL", "database"),
    "sqlite": ("SQLite", "database"),
    "redis": ("Redis", "database"),
    "mongodb": ("MongoDB", "database"),
    "prisma": ("Prisma", "database"),
    # DevOps & Infrastructure
    "docker": ("Docker", "devops"),
    "kubernetes": ("Kubernetes", "devops"),
    "aws": ("AWS", "cloud"),
    "azure": ("Azure", "cloud"),
    "gcp": ("Google Cloud", "cloud"),
    "ci/cd": ("CI/CD", "devops"),
    "git": ("Git", "tool"),
    "linux": ("Linux", "tool"),
    # Concepts & Architecture
    "rest api": ("REST API", "concept"),
    "restful": ("REST API", "concept"),
    "microservices": ("Microservices", "concept"),
    "system design": ("System Design", "concept"),
    "data structures": ("Data Structures", "concept"),
    "algorithms": ("Algorithms", "concept"),
    "oop": ("Object-Oriented Programming", "concept"),
    "unit testing": ("Unit Testing", "concept"),
    "pytest": ("Pytest", "tool"),
    "jest": ("Jest", "tool"),
    # Soft skills & Methodologies
    "agile": ("Agile", "concept"),
    "scrum": ("Scrum", "concept"),
    "communication": ("Communication", "concept"),
    "problem solving": ("Problem Solving", "concept"),
}


class MatchingService:
    @classmethod
    def _parse_job_sections(cls, job_description: str) -> tuple[str, str]:
        """Separates job description into mandatory requirements text and preferred text."""
        lines = job_description.split("\n")
        req_lines = []
        pref_lines = []
        current_section = "mandatory"

        pref_headers = ["preferred", "nice to have", "bonus", "plus", "desired", "good to have", "pluses"]
        req_headers = ["requirements", "qualifications", "must have", "required", "minimum qualifications", "what you bring", "basic qualifications", "role responsibilities"]

        for line in lines:
            line_lower = line.strip().lower()
            if any(h in line_lower for h in pref_headers) and len(line_lower) < 45:
                current_section = "preferred"
                continue
            elif any(h in line_lower for h in req_headers) and len(line_lower) < 45:
                current_section = "mandatory"
                continue

            if current_section == "preferred":
                pref_lines.append(line)
            else:
                req_lines.append(line)

        return "\n".join(req_lines), "\n".join(pref_lines)

    @classmethod
    def _extract_skills_from_text(cls, text: str) -> List[tuple[str, str]]:
        found = []
        seen = set()
        text_lower = text.lower()
        for kw, (canon, cat) in JOB_SKILL_PATTERNS.items():
            pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
            if re.search(pattern, text_lower):
                if canon not in seen:
                    seen.add(canon)
                    found.append((canon, cat))
        return found

    @staticmethod
    def match_job_description(
        user_id: str,
        role_title: str,
        job_description: str,
        goal_id: Optional[str] = None,
        source_reference: Optional[str] = None,
        db: Session = None,
    ) -> JobMatch:
        # 1. Query user's capabilities and evidence records
        user_caps = db.query(UserCapability).filter_by(user_id=user_id).all() if db else []
        user_cap_map = {c.skill.canonical_name.lower(): c for c in user_caps if c.skill}

        evidence_records = db.query(EvidenceRecord).filter_by(user_id=user_id).all() if db else []
        evidence_by_skill_name: Dict[str, List[EvidenceRecord]] = {}
        for ev in evidence_records:
            if ev.skill:
                name_key = ev.skill.canonical_name.lower()
                evidence_by_skill_name.setdefault(name_key, []).append(ev)

        cap_list = [
            {"skill_name": c.skill.canonical_name, "score": c.score, "estimated_band": c.estimated_band}
            for c in user_caps if c.skill
        ]
        ev_list = [
            {"skill_name": e.skill.canonical_name, "source_type": e.source_type, "confidence": e.confidence}
            for e in evidence_records if e.skill
        ]

        # 2. Extract skills deterministically
        req_text, pref_text = MatchingService._parse_job_sections(job_description)
        deterministic_req = MatchingService._extract_skills_from_text(req_text)
        deterministic_pref = MatchingService._extract_skills_from_text(pref_text)

        # 3. Query LLM Provider (Gemini if key configured, or FallbackAIProvider)
        llm = get_llm_provider()
        ai_match = llm.analyze_job_match(job_description, cap_list, ev_list)

        mandatory_skill_names = set(s[0] for s in deterministic_req)
        preferred_skill_names = set(s[0] for s in deterministic_pref)

        if ai_match and isinstance(ai_match, dict):
            for m_skill in ai_match.get("mandatory_skills", []):
                canon = m_skill.title() if len(m_skill) > 3 else m_skill.upper()
                mandatory_skill_names.add(canon)
            for p_skill in ai_match.get("preferred_skills", []):
                canon = p_skill.title() if len(p_skill) > 3 else p_skill.upper()
                if canon not in mandatory_skill_names:
                    preferred_skill_names.add(canon)

        # Fallback if no skills extracted
        if not mandatory_skill_names and not preferred_skill_names:
            mandatory_skill_names = {"Python", "REST API", "SQL"}

        # Prevent duplicate skills between mandatory and preferred
        preferred_skill_names = preferred_skill_names - mandatory_skill_names

        # Map to category tuples
        def resolve_category(skill_name: str) -> str:
            lower = skill_name.lower()
            if lower in JOB_SKILL_PATTERNS:
                return JOB_SKILL_PATTERNS[lower][1]
            return "concept"

        req_skills = [(s, resolve_category(s)) for s in sorted(list(mandatory_skill_names))]
        pref_skills = [(s, resolve_category(s)) for s in sorted(list(preferred_skill_names))]

        matched_skills = []
        partial_skills = []
        missing_skills = []

        total_weighted_score = 0.0
        total_possible_weight = 0.0

        all_target_skills = [(s, cat, "mandatory", 3.0) for s, cat in req_skills] + [
            (s, cat, "preferred", 1.0) for s, cat in pref_skills
        ]

        action_plan: List[str] = ai_match.get("action_plan", []) if ai_match else []

        for s_name, cat, req_type, weight in all_target_skills:
            total_possible_weight += weight * 1.0
            s_key = s_name.lower()
            cap = user_cap_map.get(s_key)
            ev_sublist = evidence_by_skill_name.get(s_key, [])

            has_assessment = any(e.source_type == "assessment" for e in ev_sublist)
            has_project = any(e.source_type == "project" for e in ev_sublist)
            has_resume = any(e.source_type == "resume" for e in ev_sublist)

            # Build evidence provenance text
            provenance_parts = []
            if has_assessment:
                provenance_parts.append("Passed skill assessment")
            if has_project:
                provenance_parts.append("Demonstrated in project code")
            if has_resume:
                provenance_parts.append("Claimed on resume")

            if cap:
                user_score = cap.score
                band = cap.estimated_band

                if user_score >= 60.0 or has_assessment:
                    confidence_mult = 1.0 if has_assessment else 0.8
                    provenance = f"Verified: {', '.join(provenance_parts)} ({user_score}% score, {band})."
                    matched_skills.append({
                        "skill": s_name,
                        "category": cat,
                        "status": "matched",
                        "user_score": user_score,
                        "band": band,
                        "requirement_type": req_type,
                        "provenance": provenance,
                    })
                    total_weighted_score += weight * confidence_mult
                else:
                    confidence_mult = 0.5
                    provenance = f"Developing: {', '.join(provenance_parts) or 'Foundational evidence'} ({user_score}% score, {band}). Assessment verification needed."
                    partial_skills.append({
                        "skill": s_name,
                        "category": cat,
                        "status": "partial",
                        "user_score": user_score,
                        "band": band,
                        "requirement_type": req_type,
                        "provenance": provenance,
                    })
                    total_weighted_score += weight * confidence_mult
                    if req_type == "mandatory" and len(action_plan) < 5:
                        action_plan.append(f"Complete the practical assessment for {s_name} to upgrade your foundational {user_score}% score to proficient.")
            else:
                provenance = "Missing: Not detected in verified assessments, projects, or uploaded resume."
                missing_skills.append({
                    "skill": s_name,
                    "category": cat,
                    "status": "missing",
                    "user_score": 0.0,
                    "band": "unverified",
                    "requirement_type": req_type,
                    "provenance": provenance,
                })
                if req_type == "mandatory" and len(action_plan) < 5:
                    action_plan.append(f"Add a project demonstrating {s_name} or complete an assessment to fulfill this mandatory requirement.")

        final_score = round((total_weighted_score / total_possible_weight * 100.0) if total_possible_weight > 0 else 0.0, 1)

        limitations = [
            "Match scores reflect capability-backed evidence (assessments, verified projects, resumes), not simple keyword stuffing.",
            "Mandatory requirements carry 3x weight compared to preferred qualifications.",
            "Demonstrated assessment and code verification carry significantly higher confidence than self-reported resume text.",
        ]

        extracted_requirements = {
            "total_skills_detected": len(all_target_skills),
            "mandatory_skills": [s[0] for s in req_skills],
            "preferred_skills": [s[0] for s in pref_skills],
            "skills": [s[0] for s in all_target_skills],
        }

        model_metadata = (
            ai_match.get("model_metadata")
            if (ai_match and isinstance(ai_match, dict))
            else {"provider": "deterministic-fallback", "version": "1.0.0"}
        )

        match_breakdown = {
            "matched_skills": matched_skills,
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "matched_count": len(matched_skills),
            "partial_count": len(partial_skills),
            "missing_count": len(missing_skills),
            "mandatory_matched": len([s for s in matched_skills if s["requirement_type"] == "mandatory"]),
            "mandatory_missing": len([s for s in missing_skills if s["requirement_type"] == "mandatory"]),
            "action_plan": action_plan[:5],
            "alignment_explanation": ai_match.get("alignment_explanation") if ai_match else None,
            "model_metadata": model_metadata,
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
