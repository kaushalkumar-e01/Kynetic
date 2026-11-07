import re
from enum import Enum
from typing import Set, Optional
from dataclasses import dataclass, field


class QueryType(str, Enum):
    CASUAL = "casual"                    # Type A: Casual conversation, greetings, thanks, farewells
    GENERAL_KNOWLEDGE = "general_knowledge"  # Type B: General software, concepts, programming questions without personal context
    WORKSPACE_SPECIFIC = "workspace_specific"  # Type C: Targeted inquiries on user's skills, resume, assessments, projects, etc.
    COMPLEX_ANALYSIS = "complex_analysis"      # Type D: Career readiness, roadmaps, multi-faceted analysis, or ambiguous requests


@dataclass
class RoutingDecision:
    query_type: QueryType
    scope: Set[str] = field(default_factory=set)  # E.g. {"skills"}, {"resume"}, {"assessments"}, {"projects"}, {"all"}
    filter_tech: Optional[str] = None
    direct_response: Optional[str] = None
    confidence: float = 1.0
    reason: str = ""


# Pre-compiled regex patterns for zero-latency deterministic classification
_PUNCT_CLEAN_RE = re.compile(r"^[^\w]+|[^\w]+$")
_WHITESPACE_RE = re.compile(r"\s+")

_GREETINGS = {
    "hi", "hello", "hey", "heyy", "heya", "howdy", "sup", "yo", "greetings",
    "good morning", "good afternoon", "good evening", "good day",
    "hi there", "hello there", "hey there",
    "hi assistant", "hello assistant", "hey assistant",
    "hi kynetic", "hello kynetic", "hey kynetic",
}

_STATUS_QUERIES = {
    "how are you", "how are you doing", "how r u", "how is it going", "how's it going",
    "how do you do", "who are you", "what can you do", "what are you", "tell me about yourself",
}

_GRATITUDE_QUERIES = {
    "thanks", "thank you", "thanks a lot", "thank you so much", "thanks so much",
    "thx", "ty", "appreciate it", "many thanks", "thanks for the help", "thank you for the help",
    "thank you very much", "thanks a bunch",
}

_FAREWELL_QUERIES = {
    "bye", "goodbye", "cya", "see you", "see ya", "have a good day", "have a nice day",
    "good night", "take care", "bye bye",
}

_CONFIRMATION_QUERIES = {
    "ok", "okay", "cool", "great", "awesome", "perfect", "got it", "understood",
    "sounds good", "nice", "alright", "sure thing",
}

_PERSONAL_PRONOUNS_RE = re.compile(
    r"\b(my|mine|me|i|i'm|am i|myself|our|we)\b", re.IGNORECASE
)

_WORKSPACE_NOUNS_RE = re.compile(
    r"\b(resume|cv|profile|portfolio|score|scores|capability|capabilities|"
    r"roadmap|roadmaps|milestone|milestones|goal|goals|assessment|assessments|"
    r"quiz|quizzes|readiness|placement|placements|gap|gaps|interview|interviewing|"
    r"tier|bands|evidence)\b",
    re.IGNORECASE,
)

_COMPLEX_STRATEGY_PHRASES = [
    "career readiness", "overall readiness", "overall career", "comprehensive",
    "six-month", "six month", "6-month", "6 month", "strategic roadmap", "career roadmap",
    "placement strategy", "career path", "career transition", "gap analysis", "skill gap", "skill gaps",
    "deep dive", "suitability", "full evaluation", "complete analysis",
    "what should i do next", "what to do next", "where should i start",
    "am i ready", "how to improve my score", "where do i stand", "what is my next step",
]

_GENERAL_INQUIRY_PATTERNS = [
    re.compile(r"^what (is|are|does) (a |an |the )?[\w\s\+\#\.\-]+(\?|\.)?$", re.IGNORECASE),
    re.compile(r"^explain (a |an |the )?[\w\s\+\#\.\-]+(\?|\.)?$", re.IGNORECASE),
    re.compile(r"^(define|describe|overview of) [\w\s\+\#\.\-]+(\?|\.)?$", re.IGNORECASE),
    re.compile(r"^how (does|do) [\w\s\+\#\.\-]+ work(\?|\.)?$", re.IGNORECASE),
    re.compile(r"^(what is the )?difference between [\w\s\+\#\.\-]+ and [\w\s\+\#\.\-]+(\?|\.)?$", re.IGNORECASE),
    re.compile(r"^(how to|how do i) (write|implement|create|use|install) [\w\s\+\#\.\-]+(\?|\.)?$", re.IGNORECASE),
    re.compile(r"^(syntax of|example of) [\w\s\+\#\.\-]+(\?|\.)?$", re.IGNORECASE),
]

_COMMON_TECH_TERMS = {
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust",
    "sql", "postgresql", "mysql", "mongodb", "redis", "docker", "kubernetes",
    "react", "next.js", "nextjs", "vue", "angular", "fastapi", "django", "flask",
    "git", "github", "linux", "rest api", "rest apis", "graphql", "grpc", "aws", "azure", "gcp",
    "machine learning", "deep learning", "neural network", "llm", "ai", "data science",
    "recursion", "binary search", "sorting", "dynamic programming", "data structures",
    "solid principles", "design patterns", "microservices", "ci/cd", "unit testing",
}


def _normalize_text(text: str) -> str:
    cleaned = _PUNCT_CLEAN_RE.sub("", text.strip().lower())
    return _WHITESPACE_RE.sub(" ", cleaned)


def _generate_casual_response(normalized: str, user_name: Optional[str] = None) -> str:
    name_clause = f", {user_name}" if user_name else ""

    if normalized in _GREETINGS or normalized.startswith(("hi ", "hello ", "hey ", "heyy ")):
        return f"Hey{name_clause}! Great to see you. How can I help you with your career goals, skills, or workspace today?"

    if normalized in _STATUS_QUERIES:
        if "who" in normalized or "what can you" in normalized or "what are you" in normalized or "about yourself" in normalized:
            return (
                "I am Kynetic's Career & Capability Co-Pilot. I help you track verified skills, "
                "analyze assessment outcomes, review project evidence, and build step-by-step career roadmaps."
            )
        return (
            "I'm doing great, thank you! Ready to help you review skills, explore projects, "
            "or prepare for assessments. What would you like to focus on?"
        )

    if normalized in _GRATITUDE_QUERIES or normalized.startswith(("thanks", "thank you", "thx", "ty")):
        return "You're very welcome! Let me know if you need any more advice on your skills, goals, or assessments."

    if normalized in _FAREWELL_QUERIES:
        return "Goodbye! Keep up the great work on your learning journey. I'll be here whenever you need guidance."

    if normalized in _CONFIRMATION_QUERIES:
        return "Awesome! What would you like to explore next?"

    return f"Hey{name_clause}! What can I help you with today?"


def classify_query(message_text: str, user_name: Optional[str] = None) -> RoutingDecision:
    """
    Lightweight, deterministic query classifier that categorizes requests into 4 types:
    - Type A (Casual): Greetings/acknowledgements -> Instant natural reply, 0 DB calls.
    - Type B (General Knowledge): Technical queries without personal context -> Direct LLM call, 0 DB calls.
    - Type C (Workspace-Specific): Targeted personal inquiries -> Selective DB retrieval.
    - Type D (Complex Analysis / Safety Fallback): Comprehensive analysis or ambiguous intent -> Full workspace context.
    """
    raw_text = message_text.strip()
    if not raw_text:
        return RoutingDecision(
            query_type=QueryType.CASUAL,
            direct_response="Hello! How can I assist you with your career capabilities today?",
            reason="Empty message",
        )

    norm = _normalize_text(raw_text)
    word_count = len(norm.split())

    # -------------------------------------------------------------
    # 1. Type A: Casual Conversation Check
    # -------------------------------------------------------------
    has_workspace_noun = bool(_WORKSPACE_NOUNS_RE.search(raw_text))
    has_personal_pronoun = bool(_PERSONAL_PRONOUNS_RE.search(raw_text))

    is_casual_match = (
        norm in _GREETINGS
        or (norm.startswith(("hi ", "hello ", "hey ", "heyy ")) and word_count <= 3)
        or norm in _STATUS_QUERIES
        or norm in _GRATITUDE_QUERIES
        or (norm.startswith(("thanks", "thank you", "thx", "ty")) and word_count <= 5)
        or norm in _FAREWELL_QUERIES
        or norm in _CONFIRMATION_QUERIES
    )

    if is_casual_match and not has_workspace_noun and word_count <= 6:
        return RoutingDecision(
            query_type=QueryType.CASUAL,
            direct_response=_generate_casual_response(norm, user_name),
            reason="Matched casual conversation pattern",
        )

    # -------------------------------------------------------------
    # 2. Check for Complex Analysis (Type D)
    # -------------------------------------------------------------
    # Any query with broad strategic phrases or ambiguous career advice triggers full context
    for phrase in _COMPLEX_STRATEGY_PHRASES:
        if phrase in norm:
            return RoutingDecision(
                query_type=QueryType.COMPLEX_ANALYSIS,
                scope={"all"},
                reason=f"Matched complex strategy phrase: '{phrase}'",
            )

    # -------------------------------------------------------------
    # 3. Type B: General Knowledge Check
    # -------------------------------------------------------------
    # Must NOT have personal pronouns ("my", "i", "me") or workspace entities
    if not has_personal_pronoun and not has_workspace_noun:
        # Check standard general inquiry patterns
        for pattern in _GENERAL_INQUIRY_PATTERNS:
            if pattern.match(norm) or pattern.match(raw_text):
                return RoutingDecision(
                    query_type=QueryType.GENERAL_KNOWLEDGE,
                    scope=set(),
                    reason="Matched general knowledge pattern without personal references",
                )

        # Check tech terms (e.g. "Python", "SQL joins", "Explain REST APIs")
        if any(tech in norm for tech in _COMMON_TECH_TERMS) and word_count <= 12:
            return RoutingDecision(
                query_type=QueryType.GENERAL_KNOWLEDGE,
                scope=set(),
                reason="Inquired about general technical topic without personal references",
            )

    # -------------------------------------------------------------
    # 4. Type C: Targeted Workspace-Specific Questions
    # -------------------------------------------------------------
    if has_personal_pronoun or has_workspace_noun:
        scope: Set[str] = set()
        filter_tech: Optional[str] = None

        # Check specific domains
        lower_raw = raw_text.lower()

        # Skills domain
        if any(k in lower_raw for k in ["skill", "capability", "capabilities", "proficien", "competenc"]):
            scope.add("skills")

        # Resume domain
        if any(k in lower_raw for k in ["resume", "cv"]):
            scope.add("resume")
            scope.add("profile")

        # Assessments domain
        if any(k in lower_raw for k in ["assessment", "quiz", "quizzes", "test", "score", "scores", "tier", "result"]):
            scope.add("assessments")

        # Projects domain
        if any(k in lower_raw for k in ["project", "projects", "repo", "github", "portfolio", "built"]):
            scope.add("projects")

        # Goals / Roadmaps domain
        if any(k in lower_raw for k in ["goal", "goals"]):
            scope.add("goals")
        if any(k in lower_raw for k in ["roadmap", "roadmaps", "milestone", "milestones"]):
            scope.add("roadmaps")

        # Role / Placement domain
        if any(k in lower_raw for k in ["role", "roles", "placement", "job match"]):
            scope.add("skills")
            scope.add("assessments")
            scope.add("profile")

        # Check for specific tech filter (e.g., "What are my Python skills?")
        for tech in ["python", "javascript", "typescript", "sql", "react", "fastapi", "docker", "java", "c++", "go"]:
            if re.search(r"\b" + re.escape(tech) + r"\b", lower_raw):
                filter_tech = tech
                scope.add("skills")
                break

        # If it specifically targets 1 or 2 domains, route as Workspace-Specific
        if 1 <= len(scope) <= 3:
            scope.add("profile")  # Always include profile name/headline for grounding
            return RoutingDecision(
                query_type=QueryType.WORKSPACE_SPECIFIC,
                scope=scope,
                filter_tech=filter_tech,
                reason=f"Targeted workspace domains: {sorted(list(scope))}",
            )

        # If it spans multiple domains or broad inquiry, route to Complex Analysis
        if len(scope) > 3:
            return RoutingDecision(
                query_type=QueryType.COMPLEX_ANALYSIS,
                scope={"all"},
                reason="Cross-domain workspace inquiry",
            )

    # -------------------------------------------------------------
    # 5. Safety Fallback: Default to Complex Analysis (Full Context)
    # -------------------------------------------------------------
    # If uncertain, always use the existing full Assistant processing pathway
    return RoutingDecision(
        query_type=QueryType.COMPLEX_ANALYSIS,
        scope={"all"},
        reason="Safety fallback: Ambiguous query intent routed to full context",
    )
