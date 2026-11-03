from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.roadmap import Roadmap, RoadmapMilestone
from app.models.skill import UserCapability, Skill
from app.models.activity import UserActivity

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
                    f"Implement automated tests and performance optimizations adhering to industry standards.",
                ],
            },
            {
                "type": "practice",
                "title": f"Verify {skill} via Kynetic Assessment",
                "action": "assessment",
                "skill": skill,
            },
        ]
        if user_cap_score and user_cap_score >= 60.0:
            resources.append({
                "type": "status_note",
                "title": "Baseline Verified",
                "note": f"You have already demonstrated {user_cap_score:.0f}% proficiency in {skill}. Focus on advanced production architecture.",
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
        # Determine skills
        if target_skills and len(target_skills) > 0:
            skills = target_skills
        else:
            skills = RoadmapService._detect_default_skills(title, description)

        # Query user capabilities to understand baseline proficiency
        user_caps = db.query(UserCapability).filter_by(user_id=user_id).all() if db else []
        cap_score_by_name = {
            c.skill.canonical_name.lower(): c.score
            for c in user_caps if c.skill
        }

        roadmap = Roadmap(
            user_id=user_id,
            goal_id=goal_id,
            title=title,
            description=description or f"Tailored skill progression roadmap targeting: {', '.join(skills)}",
            status="active",
        )
        db.add(roadmap)
        db.flush()

        # Generate sequenced milestones
        for idx, skill in enumerate(skills, start=1):
            user_score = cap_score_by_name.get(skill.lower())
            resources = RoadmapService._generate_milestone_resources(skill, user_score)

            desc = (
                f"Master fundamental concepts, practical idioms, design patterns, and enterprise best practices for {skill}."
            )
            if user_score and user_score >= 60.0:
                desc += f" (Current demonstrated baseline: {user_score:.0f}%)."

            ms = RoadmapMilestone(
                user_id=user_id,
                roadmap_id=roadmap.id,
                title=f"Milestone {idx}: Core & Advanced {skill}",
                description=desc,
                ordering=idx,
                status="in_progress" if idx == 1 else "pending",
                resources=resources,
            )
            db.add(ms)

        # Capstone project milestone
        capstone_idx = len(skills) + 1
        capstone_title = f"Milestone {capstone_idx}: Integrated Portfolio Project"
        capstone_desc = (
            f"Synthesize your mastery by architecting, testing, and deploying an end-to-end production application "
            f"integrating {', '.join(skills[:3])} with automated testing and documentation."
        )
        capstone = RoadmapMilestone(
            user_id=user_id,
            roadmap_id=roadmap.id,
            title=capstone_title,
            description=capstone_desc,
            ordering=capstone_idx,
            status="pending",
            resources=[
                {
                    "type": "project",
                    "title": "Register & Analyze Project in Kynetic",
                    "action": "project",
                    "suggested_stack": skills[:4],
                },
                {
                    "type": "documentation",
                    "title": "Production Deployment & Architecture Checklist",
                    "url": "https://github.com",
                },
            ],
        )
        db.add(capstone)

        # Audit activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="roadmap_created",
            related_record_type="roadmap",
            related_record_id=roadmap.id,
            details={"title": title, "milestones_count": len(skills) + 1, "skills": skills},
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
