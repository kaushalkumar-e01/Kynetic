from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.roadmap import Roadmap, RoadmapMilestone
from app.models.skill import UserCapability
from app.models.activity import UserActivity
from app.ai.factory import get_llm_provider

DOC_URLS = {
    "fastapi": "https://fastapi.tiangolo.com/",
    "react": "https://react.dev/",
    "next.js": "https://nextjs.org/docs",
    "postgresql": "https://www.postgresql.org/docs/",
    "python": "https://docs.python.org/3/",
    "typescript": "https://www.typescriptlang.org/docs/",
    "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "docker": "https://docs.docker.com/",
    "kubernetes": "https://kubernetes.io/docs/",
    "redis": "https://redis.io/docs/",
    "node.js": "https://nodejs.org/en/docs",
    "express": "https://expressjs.com/",
    "django": "https://docs.djangoproject.com/",
    "flask": "https://flask.palletsprojects.com/",
    "tailwindcss": "https://tailwindcss.com/docs",
    "tailwind css": "https://tailwindcss.com/docs",
    "pytest": "https://docs.pytest.org/",
    "aws": "https://docs.aws.amazon.com/",
    "graphql": "https://graphql.org/learn/",
    "pandas": "https://pandas.pydata.org/docs/",
    "pytorch": "https://pytorch.org/docs/stable/index.html",
}

ROLE_DEFAULTS = {
    "frontend": ["TypeScript", "React", "Next.js", "Tailwind CSS"],
    "backend": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "fullstack": ["TypeScript", "React", "FastAPI", "PostgreSQL"],
    "devops": ["Docker", "Kubernetes", "AWS", "CI/CD"],
    "datascience": ["Python", "Pandas", "Scikit-Learn", "PyTorch"],
    "mobile": ["TypeScript", "React Native", "Mobile Architecture", "REST API"],
}


class RoadmapService:
    @staticmethod
    def _detect_default_skills(title: str, description: Optional[str] = None) -> List[str]:
        combined = f"{title} {description or ''}".lower()
        if any(w in combined for w in ["frontend", "react", "ui", "client"]):
            return ROLE_DEFAULTS["frontend"]
        elif any(w in combined for w in ["devops", "cloud", "infra", "sre", "kubernetes"]):
            return ROLE_DEFAULTS["devops"]
        elif any(w in combined for w in ["data", "machine learning", "ml", "ai"]):
            return ROLE_DEFAULTS["datascience"]
        elif any(w in combined for w in ["full stack", "fullstack"]):
            return ROLE_DEFAULTS["fullstack"]
        elif any(w in combined for w in ["mobile", "android", "ios"]):
            return ROLE_DEFAULTS["mobile"]
        else:
            return ROLE_DEFAULTS["backend"]

    @staticmethod
    def _get_skill_doc_url(skill: str) -> str:
        key = skill.lower().strip()
        if key in DOC_URLS:
            return DOC_URLS[key]
        return f"https://devdocs.io/{key.replace(' ', '-').replace('.', '')}"

    @staticmethod
    def _generate_milestone_resources(skill: str, user_cap_score: Optional[float] = None) -> List[Dict[str, Any]]:
        doc_url = RoadmapService._get_skill_doc_url(skill)
        resources = [
            {
                "type": "documentation",
                "title": f"Official {skill} Documentation & Reference",
                "url": doc_url,
            },
            {
                "type": "learning_objectives",
                "title": f"Key Competency Objectives for {skill}",
                "objectives": [
                    f"Understand core paradigms, standard libraries, and architectural patterns of {skill}.",
                    f"Design modular, reusable, and type-safe components or services using {skill}.",
                    "Implement automated tests and performance optimizations adhering to industry standards.",
                ],
            },
            {
                "type": "practice",
                "title": f"Verify {skill} via Kynetic Assessment",
                "action": "assessment",
                "skill": skill,
            },
        ]
        if user_cap_score:
            if user_cap_score >= 85.0:
                rec_level = "Level 6 (Expert)"
                target_focus = "solve advanced algorithmic problems, edge-case optimizations, and production concurrency challenges to achieve 10/10 mastery."
            elif user_cap_score >= 65.0:
                rec_level = "Level 4–5 (Hard to Very Hard)"
                target_focus = "deepen algorithmic reasoning, dynamic programming, and systems optimization."
            elif user_cap_score >= 45.0:
                rec_level = "Level 3 (Medium)"
                target_focus = "reinforce data structure manipulation and multi-step algorithmic problem solving."
            else:
                rec_level = "Level 1–2 (Very Easy to Easy)"
                target_focus = "solidify core language syntax, control structures, and basic operations."

            resources.append({
                "type": "adaptive_recommendation",
                "title": f"Target Assessment Level: {rec_level}",
                "note": f"Current calibrated baseline: {user_cap_score:.0f}%. Next milestone focus: {target_focus}",
            })
        return resources

    @staticmethod
    def generate_roadmap(
        user_id: str,
        title: str,
        description: Optional[str] = None,
        goal_id: Optional[str] = None,
        target_skills: Optional[List[str]] = None,
        db: Session = None,
    ) -> Roadmap:
        # 1. Query user capabilities
        user_caps = db.query(UserCapability).filter_by(user_id=user_id).all() if db else []
        cap_list = [
            {"skill_name": c.skill.canonical_name, "score": c.score, "estimated_band": c.estimated_band}
            for c in user_caps if c.skill
        ]

        # 2. Query LLM provider (Gemini or Fallback)
        llm = get_llm_provider()
        ai_roadmap = llm.generate_personalized_roadmap(title, description, cap_list, target_skills)
        milestones_data = ai_roadmap.get("milestones", []) if ai_roadmap else []

        # If LLM didn't return milestones, fall back to deterministic skills
        if not milestones_data:
            skills = target_skills if (target_skills and len(target_skills) > 0) else RoadmapService._detect_default_skills(title, description)
            cap_score_by_name = {c.skill.canonical_name.lower(): c.score for c in user_caps if c.skill}
            for idx, skill in enumerate(skills, start=1):
                user_score = cap_score_by_name.get(skill.lower())
                resources = RoadmapService._generate_milestone_resources(skill, user_score)
                milestones_data.append({
                    "title": f"Milestone {idx}: Core & Advanced {skill}",
                    "description": f"Master fundamental concepts, practical idioms, design patterns, and enterprise best practices for {skill}." + (f" (Current baseline: {user_score:.0f}%)" if user_score and user_score >= 60 else ""),
                    "ordering": idx,
                    "resources": resources,
                })
            capstone_idx = len(skills) + 1
            milestones_data.append({
                "title": f"Milestone {capstone_idx}: Integrated Portfolio Project",
                "description": f"Synthesize your mastery by architecting, testing, and deploying an end-to-end production application integrating {', '.join(skills[:3])} with automated testing and documentation.",
                "ordering": capstone_idx,
                "resources": [
                    {"type": "project", "title": "Register & Analyze Project in Kynetic", "action": "project", "suggested_stack": skills[:4]},
                    {"type": "documentation", "title": "Production Deployment & Architecture Checklist", "url": "https://github.com"},
                ],
            })

        # Attach model metadata to milestone 1 resources for visibility
        model_metadata = ai_roadmap.get("model_metadata", {"provider": "deterministic-fallback", "version": "1.0.0"})
        if milestones_data and "resources" in milestones_data[0]:
            milestones_data[0]["resources"].append({
                "type": "model_metadata",
                "provider": model_metadata.get("provider", "deterministic-fallback"),
                "note": model_metadata.get("note", "Curriculum generated via capability signals."),
            })

        roadmap = Roadmap(
            user_id=user_id,
            goal_id=goal_id,
            title=title,
            description=description or f"Tailored skill progression roadmap targeting {title}",
            status="active",
        )
        db.add(roadmap)
        db.flush()

        # Persist milestones
        for idx, ms_item in enumerate(milestones_data, start=1):
            ms = RoadmapMilestone(
                user_id=user_id,
                roadmap_id=roadmap.id,
                title=ms_item.get("title", f"Milestone {idx}"),
                description=ms_item.get("description", ""),
                ordering=idx,
                status="in_progress" if idx == 1 else "pending",
                resources=ms_item.get("resources", []),
            )
            db.add(ms)

        # Audit activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="roadmap_created",
            related_record_type="roadmap",
            related_record_id=roadmap.id,
            details={"title": title, "milestones_count": len(milestones_data), "provider": model_metadata.get("provider")},
        )
        db.add(activity)

        db.commit()
        db.refresh(roadmap)
        return roadmap

    @staticmethod
    def calculate_progress(roadmap: Roadmap) -> float:
        if not roadmap.milestones:
            return 0.0
        completed = sum(1 for m in roadmap.milestones if m.status == "completed")
        return round(completed / len(roadmap.milestones) * 100.0, 1)


roadmap_service = RoadmapService()
