from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMProvider(ABC):
    @abstractmethod
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyzes resume text and extracts structured information:
        - extracted_profile: name, email, education, experience, projects, skills
        - strengths: list of notable candidate strengths
        - suggestions: list of actionable improvement suggestions
        - claimed_skills: list of skill dicts (name, category)
        """
        pass

    @abstractmethod
    def generate_chat_response(self, user_prompt: str, context: Dict[str, Any]) -> str:
        """Generates an assistant response given user prompt and authorized workspace context."""
        pass

