from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.errors import NotFoundException, ValidationException
from app.models.assistant import AssistantConversation, AssistantMessage
from app.models.user import UserProfile
from app.models.skill import UserCapability
from app.models.assessment import Assessment
from app.models.project import Project
from app.models.goal import Goal
from app.models.roadmap import Roadmap
from app.models.activity import UserActivity
from app.ai import get_llm_provider


class AssistantService:
    @staticmethod
    def get_user_workspace_context(user_id: str, db: Session) -> Dict[str, Any]:
        profile = db.query(UserProfile).filter_by(user_id=user_id).first()
        capabilities = (
            db.query(UserCapability)
            .filter_by(user_id=user_id)
            .order_by(desc(UserCapability.score))
            .limit(10)
            .all()
        )
        recent_assessments = (
            db.query(Assessment)
            .filter_by(user_id=user_id)
            .order_by(desc(Assessment.started_at))
            .limit(3)
            .all()
        )
        recent_projects = (
            db.query(Project)
            .filter_by(user_id=user_id)
            .order_by(desc(Project.created_at))
            .limit(3)
            .all()
        )
        active_goals = (
            db.query(Goal)
            .filter_by(user_id=user_id, status="active")
            .limit(3)
            .all()
        )
        active_roadmaps = (
            db.query(Roadmap)
            .filter_by(user_id=user_id, status="active")
            .limit(2)
            .all()
        )

        return {
            "candidate_name": profile.display_name if profile else None,
            "headline": profile.headline if profile else None,
            "preferred_domains": profile.preferred_domains if profile else [],
            "top_skills": [
                {
                    "skill": c.skill.canonical_name if c.skill else "Skill",
                    "score": c.score,
                    "band": c.estimated_band,
                    "confidence": c.confidence,
                }
                for c in capabilities
            ],
            "recent_assessments": [
                {
                    "title": a.title,
                    "mode": a.mode,
                    "status": a.status,
                    "topics": a.selected_topics,
                }
                for a in recent_assessments
            ],
            "projects": [{"name": p.name, "source": p.source_type} for p in recent_projects],
            "active_goals": [{"title": g.title, "type": g.goal_type} for g in active_goals],
            "active_roadmaps": [{"title": r.title, "milestones_count": len(r.milestones)} for r in active_roadmaps],
        }

    @staticmethod
    def send_message(
        user_id: str,
        message_text: str,
        conversation_id: Optional[str] = None,
        db: Session = None,
    ) -> AssistantConversation:
        clean_msg = message_text.strip()
        if not clean_msg:
            raise ValidationException("Message content cannot be blank.")

        # Resolve or create conversation
        if conversation_id:
            conv = db.query(AssistantConversation).filter_by(id=conversation_id, user_id=user_id).first()
            if not conv:
                raise NotFoundException("Conversation not found or access denied.")
        else:
            title = clean_msg[:45] + ("..." if len(clean_msg) > 45 else "")
            conv = AssistantConversation(user_id=user_id, title=title)
            db.add(conv)
            db.flush()

        # Save user message
        user_msg = AssistantMessage(
            conversation_id=conv.id,
            role="user",
            content=clean_msg,
        )
        db.add(user_msg)
        db.flush()

        # Gather user authorized context
        context = AssistantService.get_user_workspace_context(user_id, db)

        # Generate intelligent assistant response
        llm = get_llm_provider()
        bot_response_text = llm.generate_chat_response(clean_msg, context)

        # Enhance with personalized answers if fallback provider is used
        if "FallbackAIProvider" in type(llm).__name__ or "fallback" in type(llm).__name__.lower():
            lower_msg = clean_msg.lower()
            if any(k in lower_msg for k in ["gap", "skill", "capabilities", "know"]):
                if context["top_skills"]:
                    skills_summary = ", ".join([f"{s['skill']} ({s['band']}: {s['score']}%)" for s in context["top_skills"][:5]])
                    bot_response_text = (
                        f"Based on your capability profile, your current tracked skills are: {skills_summary}. "
                        "To close gaps for top placement roles, prioritize validating your claimed skills with adaptive quizzes "
                        "and building practical project evidence."
                    )
                else:
                    bot_response_text = (
                        "You currently have no skills tracked in your profile. "
                        "Upload your resume to extract claimed skills or take an assessment to demonstrate your capabilities."
                    )
            elif any(k in lower_msg for k in ["roadmap", "milestone", "plan"]):
                if context["active_roadmaps"]:
                    r_info = context["active_roadmaps"][0]
                    bot_response_text = f"You are currently progressing on the roadmap '{r_info['title']}' with {r_info['milestones_count']} milestones. Complete pending milestones to advance your capability score!"
                else:
                    bot_response_text = "You don't have an active roadmap yet. You can generate a personalized roadmap targeting your career goal in the Roadmaps module."

        # Save assistant message
        bot_msg = AssistantMessage(
            conversation_id=conv.id,
            role="assistant",
            content=bot_response_text,
        )
        db.add(bot_msg)

        # Audit activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="assistant_message_sent",
            related_record_type="conversation",
            related_record_id=conv.id,
        )
        db.add(activity)

        db.commit()
        db.refresh(conv)
        return conv


assistant_service = AssistantService()

