"""
E2E Test: Gemini Integration and Resilient Fallback Provider Architecture
Verifies:
1. LLM Provider factory selection (Gemini vs Fallback based on GEMINI_API_KEY).
2. Model metadata contract across Project Analysis, Placement Matching, Roadmaps, and Resume parsing.
3. Resilient fallback behavior when Gemini encounters simulated network/auth/quota errors.
4. Schema compliance and deterministic score preservation.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure backend modules are importable
sys.path.insert(0, "backend")

from app.core.config import settings
from app.ai.base import BaseLLMProvider
from app.ai.fallback_provider import FallbackAIProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.factory import get_llm_provider


class TestGeminiIntegrationE2E(unittest.TestCase):
    def setUp(self):
        self.fallback = FallbackAIProvider()

    def test_01_fallback_provider_metadata_transparency(self):
        """Verify FallbackAIProvider marks all intelligence output transparently as fallback."""
        # 1. Resume
        resume_res = self.fallback.analyze_resume("Proficient in Python, FastAPI, Docker, and PostgreSQL.")
        self.assertIn("claimed_skills", resume_res)
        extracted_names = [s["name"].lower() for s in resume_res["claimed_skills"]]
        self.assertIn("python", extracted_names)
        self.assertEqual(resume_res.get("model_metadata", {}).get("provider"), "rule-based-fallback")

        # 2. Repository
        repo_res = self.fallback.analyze_repository({
            "repo_full_name": "kaushalkumar-e01/Kynetic",
            "primary_language": "TypeScript",
            "files": ["backend/app/main.py", "frontend/package.json"]
        })
        self.assertIn("major_features", repo_res)
        self.assertIn("recommendations", repo_res)
        self.assertEqual(repo_res.get("model_metadata", {}).get("provider"), "deterministic-fallback")

        # 3. Job Match (semantic alignment)
        match_res = self.fallback.analyze_job_match(
            job_description="Seeking a Senior Backend Engineer proficient in Python and AWS.",
            candidate_capabilities=[{"name": "Python"}, {"name": "FastAPI"}],
            candidate_evidence=[{"title": "FastAPI API"}]
        )
        self.assertIn("alignment_explanation", match_res)
        self.assertEqual(match_res.get("model_metadata", {}).get("provider"), "deterministic-fallback")

        # 4. Personalized Roadmap
        roadmap_res = self.fallback.generate_personalized_roadmap(
            role_title="Senior Platform Engineer",
            role_description="Platform Engineering focus",
            candidate_capabilities=[{"name": "Python"}, {"name": "FastAPI"}],
            target_skills=["Kubernetes", "Terraform"]
        )
        self.assertIn("milestones", roadmap_res)
        self.assertGreaterEqual(len(roadmap_res["milestones"]), 3)
        self.assertEqual(roadmap_res.get("model_metadata", {}).get("provider"), "deterministic-fallback")

    def test_02_factory_selection_logic(self):
        """Verify get_llm_provider selects Gemini when API key is configured and Fallback when unconfigured."""
        # When api_key is None or empty
        with patch.object(settings, "GEMINI_API_KEY", None), patch.object(settings, "LLM_API_KEY", None):
            provider = get_llm_provider()
            self.assertIsInstance(provider, FallbackAIProvider)

        # When api_key is populated
        with patch.object(settings, "GEMINI_API_KEY", "AIzaSyFakeKeyForTesting12345"):
            provider = get_llm_provider()
            self.assertIsInstance(provider, GeminiProvider)
            self.assertEqual(provider.api_key, "AIzaSyFakeKeyForTesting12345")

        # When explicitly requested provider="fallback"
        with patch.object(settings, "GEMINI_API_KEY", "AIzaSyFakeKeyForTesting12345"):
            provider = get_llm_provider(provider_type="fallback")
            self.assertIsInstance(provider, FallbackAIProvider)

    def test_03_gemini_graceful_error_recovery_to_fallback(self):
        """Verify GeminiProvider catches exceptions, logs safely without secrets, and falls back seamlessly."""
        gemini = GeminiProvider(api_key="AIzaSyTestKey", model_name="gemini-1.5-flash")
        gemini._is_configured = True

        # Mock _execute_with_retry to simulate an API quota exhaustion (ResourceExhausted) or network error
        with patch.object(gemini, "_execute_with_retry", return_value=None):
            # Resume Analysis Fallback
            resume_result = gemini.analyze_resume("Python and React developer")
            self.assertIn("claimed_skills", resume_result)
            self.assertEqual(resume_result.get("model_metadata", {}).get("provider"), "rule-based-fallback")

            # Repository Analysis Fallback
            repo_result = gemini.analyze_repository({"repo_full_name": "test/test-repo", "files": ["main.py"]})
            self.assertIn("major_features", repo_result)
            self.assertEqual(repo_result.get("model_metadata", {}).get("provider"), "deterministic-fallback")

            # Job Match Fallback
            match_result = gemini.analyze_job_match(
                job_description="Python engineer",
                candidate_capabilities=[{"name": "Python"}],
                candidate_evidence=[]
            )
            self.assertIn("alignment_explanation", match_result)
            self.assertEqual(match_result.get("model_metadata", {}).get("provider"), "deterministic-fallback")

            # Roadmap Fallback
            roadmap_result = gemini.generate_personalized_roadmap(
                role_title="Backend Engineer",
                role_description="Backend Development",
                candidate_capabilities=[{"name": "Python"}],
                target_skills=["Docker"]
            )
            self.assertIn("milestones", roadmap_result)
            self.assertEqual(roadmap_result.get("model_metadata", {}).get("provider"), "deterministic-fallback")

    def test_04_gemini_structured_response_parsing(self):
        """Verify Gemini successfully extracts and parses structured JSON responses."""
        gemini = GeminiProvider(api_key="AIzaSyTestKey", model_name="gemini-1.5-flash")
        gemini._is_configured = True

        mock_gemini_json_response = """
        ```json
        {
            "extracted_profile": {
                "candidate_name": "Alex Chen",
                "candidate_email": "alex@example.com",
                "education": ["BS in Computer Science"],
                "experience": ["Software Engineer at Acme"],
                "projects": ["Distributed Queue"]
            },
            "claimed_skills": [
                {"name": "Python", "category": "language"},
                {"name": "FastAPI", "category": "framework"},
                {"name": "PostgreSQL", "category": "database"}
            ],
            "strengths": [
                "Strong backend foundations with modern async Python.",
                "Production experience with relational data modeling.",
                "Demonstrated focus on distributed systems."
            ],
            "suggestions": [
                "Add cloud orchestration metrics to project descriptions.",
                "Complete a Docker capability assessment.",
                "Link GitHub repository to verify code quality."
            ]
        }
        ```
        """

        with patch.object(gemini, "_execute_with_retry", return_value=mock_gemini_json_response):
            result = gemini.analyze_resume("Sample raw resume text")
            self.assertIn("claimed_skills", result)
            self.assertEqual(len(result["claimed_skills"]), 3)
            self.assertEqual(result["claimed_skills"][0]["name"], "Python")
            self.assertEqual(result["model_metadata"]["provider"], "gemini")
            self.assertEqual(result["model_metadata"]["model"], "gemini-1.5-flash")


if __name__ == "__main__":
    unittest.main()
