from typing import Dict, Any, Optional, Set
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import desc

from app.core.errors import NotFoundException, ValidationException
from app.models.assistant import AssistantConversation, AssistantMessage
from app.models.user import UserProfile
from app.models.skill import UserCapability, Skill
from app.models.assessment import Assessment
from app.models.project import Project
from app.models.goal import Goal
from app.models.roadmap import Roadmap
from app.models.resume import ResumeAnalysis
from app.models.activity import UserActivity
from app.ai import get_llm_provider
from app.services.assistant_router import classify_query, QueryType


class AssistantService:
    @staticmethod
    def get_user_workspace_context(
        user_id: str,
        db: Session,
        scope: Optional[Set[str]] = None,
        filter_tech: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves user workspace context.
        If scope is None, retrieves full context (backwards compatible).
        If scope is provided, selectively queries only requested entities for optimal performance.
        """
        retrieve_all = scope is None or "all" in scope

        # 1. Candidate Profile
        profile = None
        if retrieve_all or "profile" in scope:
            profile = db.query(UserProfile).filter_by(user_id=user_id).first()

        # 2. Capabilities (with joinedload to eliminate N+1 queries)
        capabilities = []
        if retrieve_all or "skills" in scope:
            cap_query = (
                db.query(UserCapability)
                .options(joinedload(UserCapability.skill))
                .filter_by(user_id=user_id)
            )
            if filter_tech:
                cap_query = cap_query.join(UserCapability.skill).filter(
                    Skill.canonical_name.ilike(f"%{filter_tech}%")
                )
            capabilities = (
                cap_query
                .order_by(desc(UserCapability.score))
                .limit(10)
                .all()
            )

        # 3. Recent Assessments
        recent_assessments = []
        if retrieve_all or "assessments" in scope:
            recent_assessments = (
                db.query(Assessment)
                .filter_by(user_id=user_id)
                .order_by(desc(Assessment.started_at))
                .limit(3)
                .all()
            )

        # 4. Recent Projects
        recent_projects = []
        if retrieve_all or "projects" in scope:
            recent_projects = (
                db.query(Project)
                .filter_by(user_id=user_id)
                .order_by(desc(Project.created_at))
                .limit(3)
                .all()
            )

        # 5. Active Goals
        active_goals = []
        if retrieve_all or "goals" in scope:
            active_goals = (
                db.query(Goal)
                .filter_by(user_id=user_id, status="active")
                .limit(3)
                .all()
            )

        # 6. Active Roadmaps (with selectinload to eagerly fetch milestones)
        active_roadmaps = []
        if retrieve_all or "roadmaps" in scope:
            active_roadmaps = (
                db.query(Roadmap)
                .options(selectinload(Roadmap.milestones))
                .filter_by(user_id=user_id, status="active")
                .limit(2)
                .all()
            )

        # 7. Resume Analysis
        resume_summary = None
        if scope is not None and ("resume" in scope or "all" in scope):
            analysis = (
                db.query(ResumeAnalysis)
                .filter_by(user_id=user_id, status="completed")
                .order_by(desc(ResumeAnalysis.completed_at))
                .first()
            )
            if analysis:
                resume_summary = {
                    "strengths": (analysis.strengths or [])[:3],
                    "suggestions": (analysis.suggestions or [])[:3],
                    "claimed_skills": [
                        s.get("name") if isinstance(s, dict) else str(s)
                        for s in ((analysis.extracted_profile or {}).get("skills", []))[:8]
                    ],
                }

        context_dict: Dict[str, Any] = {
            "candidate_name": profile.display_name if profile else None,
            "headline": profile.headline if profile else None,
            "preferred_domains": profile.preferred_domains if profile else [],
            "top_skills": [
                {
                    "skill": c.skill.canonical_name if c.skill else "Skill",
                    "score": c.score,
                    "mastery_score": round(c.score / 10.0, 1),
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
                    "mastery_score": (a.summary_result or {}).get("mastery_score"),
                    "mastery_band": (a.summary_result or {}).get("mastery_band"),
                    "highest_tier_passed": (a.summary_result or {}).get("highest_tier_passed"),
                }
                for a in recent_assessments
            ],
            "projects": [{"name": p.name, "source": p.source_type} for p in recent_projects],
            "active_goals": [{"title": g.title, "type": g.goal_type} for g in active_goals],
            "active_roadmaps": [{"title": r.title, "milestones_count": len(r.milestones)} for r in active_roadmaps],
        }

        if resume_summary:
            context_dict["resume_summary"] = resume_summary

        return context_dict

    @staticmethod
    def _apply_fallback_personalization_if_needed(
        llm: Any,
        clean_msg: str,
        context: Dict[str, Any],
        bot_response_text: str,
    ) -> str:
        """Personalizes fallback provider answers with real user context if fallback is active."""
        if "FallbackAIProvider" in type(llm).__name__ or "fallback" in type(llm).__name__.lower():
            lower_msg = clean_msg.lower()
            if any(k in lower_msg for k in ["gap", "skill", "capabilities", "know"]):
                if context.get("top_skills"):
                    skills_summary = ", ".join(
                        [f"{s['skill']} ({s['band']}: {s['score']}%)" for s in context["top_skills"][:5]]
                    )
                    return (
                        f"Based on your capability profile, your current tracked skills are: {skills_summary}. "
                        "To close gaps for top placement roles, prioritize validating your claimed skills with adaptive quizzes "
                        "and building practical project evidence."
                    )
                else:
                    return (
                        "You currently have no skills tracked in your profile. "
                        "Upload your resume to extract claimed skills or take an assessment to demonstrate your capabilities."
                    )
            elif any(k in lower_msg for k in ["roadmap", "milestone", "plan"]):
                if context.get("active_roadmaps"):
                    r_info = context["active_roadmaps"][0]
                    return f"You are currently progressing on the roadmap '{r_info['title']}' with {r_info['milestones_count']} milestones. Complete pending milestones to advance your capability score!"
                else:
                    return "You don't have an active roadmap yet. You can generate a personalized roadmap targeting your career goal in the Roadmaps module."
            elif any(k in lower_msg for k in ["resume", "cv"]):
                if context.get("resume_summary"):
                    r_sum = context["resume_summary"]
                    skills_txt = ", ".join(r_sum.get("claimed_skills", [])[:5]) or "general engineering skills"
                    return f"Your resume highlights experience with {skills_txt}. To strengthen credibility for recruiters, validate these claimed skills with Kynetic assessments."
                return "Your resume claims have been ingested. Make sure to ground them with technical evidence in Assessments and Projects to make them credible to recruiters."

        return bot_response_text

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

        # -------------------------------------------------------------
        # Lightweight Intelligent Query Routing
        # -------------------------------------------------------------
        profile = db.query(UserProfile).filter_by(user_id=user_id).first()
        user_name = profile.display_name if profile else None

        decision = classify_query(clean_msg, user_name=user_name)

        if decision.query_type == QueryType.CASUAL and decision.direct_response:
            # FAST-PATH: Instant casual response without LLM latency or DB retrieval
            bot_response_text = decision.direct_response
        elif decision.query_type == QueryType.GENERAL_KNOWLEDGE:
            # FAST-PATH: Direct LLM call with 0 workspace context DB queries
            llm = get_llm_provider()
            bot_response_text = llm.generate_chat_response(clean_msg, context={})
            bot_response_text = AssistantService._apply_fallback_personalization_if_needed(llm, clean_msg, {}, bot_response_text)
        elif decision.query_type == QueryType.WORKSPACE_SPECIFIC:
            # SELECTIVE RETRIEVAL: Query only the requested workspace entities
            context = AssistantService.get_user_workspace_context(
                user_id=user_id,
                db=db,
                scope=decision.scope,
                filter_tech=decision.filter_tech,
            )
            llm = get_llm_provider()
            bot_response_text = llm.generate_chat_response(clean_msg, context)
            bot_response_text = AssistantService._apply_fallback_personalization_if_needed(llm, clean_msg, context, bot_response_text)
        else:
            # COMPLEX ANALYSIS / SAFETY FALLBACK: Full workspace context
            context = AssistantService.get_user_workspace_context(user_id=user_id, db=db)
            llm = get_llm_provider()
            bot_response_text = llm.generate_chat_response(clean_msg, context)
            bot_response_text = AssistantService._apply_fallback_personalization_if_needed(llm, clean_msg, context, bot_response_text)

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
