from app.core.config import settings
from app.ai.base import BaseLLMProvider
from app.ai.fallback_provider import FallbackAIProvider
from app.ai.gemini_provider import GeminiProvider


def get_llm_provider() -> BaseLLMProvider:
    provider_name = (settings.LLM_PROVIDER or "").lower().strip()
    api_key = settings.LLM_API_KEY

    if provider_name == "gemini" and api_key:
        return GeminiProvider(api_key=api_key, model_name=settings.LLM_MODEL)

    # Defaults to deterministic fallback provider if no provider or key configured
    return FallbackAIProvider()

