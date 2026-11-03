import json
from typing import Dict, Any
from app.ai.base import BaseLLMProvider
from app.core.config import settings

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model_name = model_name or settings.LLM_MODEL or "gemini-1.5-flash"
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        if not genai or not self.api_key:
            from app.ai.fallback_provider import FallbackAIProvider
            return FallbackAIProvider().analyze_resume(resume_text)

        prompt = f"""
        You are an expert technical resume evaluator for Kynetic.
        Analyze the following resume text and output a valid JSON object strictly matching this schema:
        {{
            "extracted_profile": {{
                "candidate_name": "string or null",
                "candidate_email": "string or null",
                "education": ["list of education details"],
                "experience": ["list of work experiences"],
                "projects": ["list of projects"]
            }},
            "claimed_skills": [
                {{"name": "Skill Name", "category": "language|framework|database|tool|cloud|concept"}}
            ],
            "strengths": ["list of 3 key strengths"],
            "suggestions": ["list of 3 actionable improvement suggestions"]
        }}

        Do NOT include markdown backticks or commentary, only valid JSON.
        Resume text:
        {resume_text[:12000]}
        """

        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            parsed = json.loads(cleaned_text.strip())
            parsed["status"] = "completed"
            parsed["model_metadata"] = {"provider": "gemini", "model": self.model_name}
            return parsed
        except Exception:
            from app.ai.fallback_provider import FallbackAIProvider
            return FallbackAIProvider().analyze_resume(resume_text)

    def generate_chat_response(self, user_prompt: str, context: Dict[str, Any]) -> str:
        if not genai or not self.api_key:
            from app.ai.fallback_provider import FallbackAIProvider
            return FallbackAIProvider().generate_chat_response(user_prompt, context)

        prompt = f"Context: {json.dumps(context)}\nUser question: {user_prompt}"
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            return "Kynetic assistant is currently operating with local context fallback."

