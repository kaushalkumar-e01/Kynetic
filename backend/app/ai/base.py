from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseLLMProvider(ABC):
    @abstractmethod
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyzes resume text and extracts structured information:
        - extracted_profile: name, email, education, experience, projects, skills
        - strengths: list of notable candidate strengths
        - suggestions: list of actionable improvement suggestions
        - claimed_skills: list of skill dicts (name, category)
        - model_metadata: provider, model
        """
        pass

    @abstractmethod
    def analyze_repository(self, repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deeply analyzes structured repository context (manifests, source files, structure, tests):
        - purpose: project purpose
        - detected_technologies: list of identified tech/libraries
        - demonstrated_skills: list of verified skills
        - architecture_summary: multi-tier architectural breakdown
        - major_features: list of key features observed
        - technical_strengths: list of strengths with evidence
        - architectural_weaknesses: list of architectural risks/weaknesses
        - missing_requirements: list of production gaps
        - recommendations: grounded recommendations with file paths
        - inspected_files: list of files examined
        - model_metadata: provider, model
        """
        pass

    @abstractmethod
    def analyze_job_match(
        self,
        job_description: str,
        candidate_capabilities: List[Dict[str, Any]],
        candidate_evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Extracts structured job requirements and provides semantic matching insights:
        - extracted_requirements: mandatory_skills, preferred_skills, languages, frameworks, databases, tools, soft_skills
        - semantic_equivalences: mapping of candidate skills to job requirements
        - action_plan: tailored recommendations and practical projects to close gaps
        - alignment_explanation: explanation of match strengths and gaps
        - model_metadata: provider, model
        """
        pass

    @abstractmethod
    def generate_personalized_roadmap(
        self,
        role_title: str,
        role_description: Optional[str],
        candidate_capabilities: List[Dict[str, Any]],
        target_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generates structured, personalized career curriculum:
        - milestones: sequenced milestones with titles, descriptions, learning objectives, docs, challenges, prerequisites
        - model_metadata: provider, model
        """
        pass

    @abstractmethod
    def generate_chat_response(self, user_prompt: str, context: Dict[str, Any]) -> str:
        """Generates an assistant response given user prompt and authorized workspace context."""
        pass

    def generate_question_batch(
        self,
        skill_or_topic: str,
        category: str,
        difficulty: str,
        question_type: str,
        batch_size: int,
        programming_language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generates a batch of technical questions with schema metadata."""
        return []
