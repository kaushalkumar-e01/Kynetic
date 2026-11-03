import re
from typing import Dict, Any
from app.ai.base import BaseLLMProvider

COMMON_SKILLS = {
    # Languages
    "python": "language", "javascript": "language", "typescript": "language",
    "java": "language", "c++": "language", "c#": "language", "golang": "language",
    "ruby": "language", "rust": "language", "sql": "language", "html": "language", "css": "language",
    # Frameworks / Libraries
    "react": "framework", "next.js": "framework", "vue": "framework", "angular": "framework",
    "fastapi": "framework", "django": "framework", "flask": "framework", "express": "framework",
    "node.js": "framework", "spring boot": "framework", "tailwindcss": "framework",
    # Databases
    "postgresql": "database", "mysql": "database", "sqlite": "database",
    "mongodb": "database", "redis": "database", "cassandra": "database",
    # DevOps / Cloud
    "docker": "devops", "kubernetes": "devops", "aws": "cloud", "azure": "cloud", "gcp": "cloud",
    "git": "tool", "github": "tool", "ci/cd": "devops", "linux": "os",
    # Concepts
    "data structures": "concept", "algorithms": "concept", "rest api": "concept",
    "microservices": "concept", "oop": "concept", "machine learning": "concept",
}


class FallbackAIProvider(BaseLLMProvider):
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        text_lower = resume_text.lower()

        # Extract skills
        detected_skills = []
        for skill_name, category in COMMON_SKILLS.items():
            pattern = r"(?<!\w)" + re.escape(skill_name) + r"(?!\w)"
            if re.search(pattern, text_lower):
                detected_skills.append({
                    "name": skill_name.title() if len(skill_name) > 3 else skill_name.upper(),
                    "category": category,
                })

        # Basic email and phone extraction
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
        candidate_email = email_match.group(0) if email_match else None

        # Identify sections
        sections = {"education": [], "experience": [], "projects": []}
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]

        current_section = None
        for line in lines:
            lower = line.lower()
            if any(h in lower for h in ["education", "academic", "university", "college", "degree"]):
                current_section = "education"
                continue
            elif any(h in lower for h in ["experience", "employment", "work history", "internship"]):
                current_section = "experience"
                continue
            elif any(h in lower for h in ["projects", "personal projects", "academic projects"]):
                current_section = "projects"
                continue
            elif any(h in lower for h in ["skills", "technical skills", "certifications"]):
                current_section = None
                continue

            if current_section and len(line) > 3:
                sections[current_section].append(line)

        strengths = [
            f"Demonstrated background with {len(detected_skills)} identified technical competencies.",
            "Clear technical project and educational history provided in resume.",
        ]
        if any(s["category"] == "database" for s in detected_skills):
            strengths.append("Foundational database systems exposure.")
        if any(s["category"] == "framework" for s in detected_skills):
            strengths.append("Modern application framework knowledge.")

        suggestions = [
            "Validate claimed skills through Kynetic skill assessments to generate verified evidence.",
            "Connect related GitHub repositories to support project implementations with practical code evidence.",
            "Add measurable metric outcomes (e.g. % performance increase, latency reduction) to project descriptions.",
        ]

        return {
            "status": "completed",
            "extracted_profile": {
                "candidate_email": candidate_email,
                "education": sections["education"][:5],
                "experience": sections["experience"][:8],
                "projects": sections["projects"][:6],
                "claimed_skills_count": len(detected_skills),
            },
            "claimed_skills": detected_skills,
            "strengths": strengths,
            "suggestions": suggestions,
            "model_metadata": {
                "provider": "rule-based-fallback",
                "version": "1.0.0",
                "note": "Deterministic fallback extractor (no external LLM key required).",
            },
        }

    def generate_chat_response(self, user_prompt: str, context: Dict[str, Any]) -> str:
        return (
            "I am Kynetic's AI Assistant. Based on your current workspace profile, "
            "you can explore targeted skill assessments, connect your GitHub repositories, "
            "or compare your profile with target job roles."
        )

