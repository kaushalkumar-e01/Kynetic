from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.roadmap import Roadmap, RoadmapMilestone
from app.models.activity import UserActivity


class RoadmapService:
    @staticmethod
    def generate_roadmap(
        user_id: str,
        title: str,
        description: Optional[str] = None,
        goal_id: Optional[str] = None,
        target_skills: Optional[List[str]] = None,
        db: Session = None,
    ) -> Roadmap:
        skills = target_skills or ["Python", "FastAPI", "PostgreSQL", "Docker"]

        roadmap = Roadmap(
            user_id=user_id,
            goal_id=goal_id,
            title=title,
            description=description or f"Personalized capability roadmap targeting: {', '.join(skills[:3])}",
            status="active",
        )
        db.add(roadmap)
        db.flush()

        # Generate sequenced milestones
        for idx, skill in enumerate(skills, start=1):
            ms = RoadmapMilestone(
                user_id=user_id,
                roadmap_id=roadmap.id,
                title=f"Milestone {idx}: Master Core {skill}",
                description=f"Understand fundamental concepts, best practices, and practical application of {skill}.",
                ordering=idx,
                status="in_progress" if idx == 1 else "pending",
                resources=[
                    {"type": "documentation", "title": f"Official {skill} Documentation", "url": f"https://devdocs.io/{skill.lower()}"},
                    {"type": "practice", "title": f"Complete Kynetic {skill} Assessments", "action": "assessment"},
                ],
            )
            db.add(ms)

        # Capstone project milestone
        capstone = RoadmapMilestone(
            user_id=user_id,
            roadmap_id=roadmap.id,
            title=f"Milestone {len(skills) + 1}: Integrated Portfolio Project",
            description=f"Design and build a complete end-to-end practical application connecting {', '.join(skills[:3])}.",
            ordering=len(skills) + 1,
            status="pending",
            resources=[
                {"type": "project", "title": "GitHub Repository Deployment", "action": "project"},
            ],
        )
        db.add(capstone)

        # Audit activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="roadmap_created",
            related_record_type="roadmap",
            related_record_id=roadmap.id,
            details={"title": title, "milestones_count": len(skills) + 1},
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

