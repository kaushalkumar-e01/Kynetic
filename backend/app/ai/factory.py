from app.core.config import settings
from app.ai.base import BaseLLMProvider
from app.ai.fallback_provider import FallbackAIProvider
from app.ai.gemini_provider import GeminiProvider


def get_llm_provider() -> BaseLLMProvider:
    provider_name = (settings.LLM_PROVIDER or "").lower().strip()
    api_key = settings.LLM_API_KEY or settings.GEMINI_API_KEY

    # Use Gemini if specified or if an API key is available and provider is not set to something else
    if (provider_name == "gemini" or (api_key and not provider_name)) and api_key:
        return GeminiProvider(api_key=api_key, model_name=settings.LLM_MODEL)

    # Defaults to deterministic fallback provider if no provider or key configured
    return FallbackAIProvider()

