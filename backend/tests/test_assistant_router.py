from app.services.assistant_router import classify_query, QueryType


def test_query_classification():
    test_cases = [
        # Type A: Casual
        ("Hi", QueryType.CASUAL),
        ("Hello", QueryType.CASUAL),
        ("Hey!", QueryType.CASUAL),
        ("Good morning", QueryType.CASUAL),
        ("How are you?", QueryType.CASUAL),
        ("Thanks", QueryType.CASUAL),
        ("Thank you", QueryType.CASUAL),
        ("Bye", QueryType.CASUAL),
        # Type B: General Knowledge
        ("What is Python?", QueryType.GENERAL_KNOWLEDGE),
        ("Explain REST APIs.", QueryType.GENERAL_KNOWLEDGE),
        ("What is Git?", QueryType.GENERAL_KNOWLEDGE),
        ("What is machine learning?", QueryType.GENERAL_KNOWLEDGE),
        ("Explain SQL joins.", QueryType.GENERAL_KNOWLEDGE),
        # Type C: Workspace-Specific
        ("What are my strongest skills?", QueryType.WORKSPACE_SPECIFIC),
        ("Review my resume.", QueryType.WORKSPACE_SPECIFIC),
        ("Which projects have I completed?", QueryType.WORKSPACE_SPECIFIC),
        ("What does my latest assessment say?", QueryType.WORKSPACE_SPECIFIC),
        ("Which roles match my capabilities?", QueryType.WORKSPACE_SPECIFIC),
        ("What are my Python skills?", QueryType.WORKSPACE_SPECIFIC),
        # Type D: Complex Analysis
        ("Analyze my overall career readiness.", QueryType.COMPLEX_ANALYSIS),
        ("Build a six-month career roadmap.", QueryType.COMPLEX_ANALYSIS),
        ("Compare my suitability for multiple career paths.", QueryType.COMPLEX_ANALYSIS),
        ("Identify my technical skill gaps.", QueryType.COMPLEX_ANALYSIS),
        ("Develop a comprehensive placement strategy.", QueryType.COMPLEX_ANALYSIS),
        # Safety Fallback
        ("What should I do next?", QueryType.COMPLEX_ANALYSIS),
        ("Am I ready for backend development?", QueryType.COMPLEX_ANALYSIS),
    ]

    for text, expected in test_cases:
        decision = classify_query(text)
        assert decision.query_type == expected, f"Failed on '{text}': got {decision.query_type}, expected {expected} ({decision.reason})"

