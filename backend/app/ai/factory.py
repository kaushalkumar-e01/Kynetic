from typing import Optional
from app.core.config import settings
from app.ai.base import BaseLLMProvider
from app.ai.fallback_provider import FallbackAIProvider
from app.ai.gemini_provider import GeminiProvider


def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    provider_name = (provider_type or settings.LLM_PROVIDER or "").lower().strip()
    api_key = settings.effective_gemini_api_key
    model_name = settings.effective_gemini_model

    # Use Gemini if specified or if an API key is available and provider is not explicitly set to fallback
    if api_key and provider_name != "fallback":
        return GeminiProvider(api_key=api_key, model_name=model_name)

    # Defaults to deterministic fallback provider if no key or fallback explicitly chosen
    return FallbackAIProvider()

