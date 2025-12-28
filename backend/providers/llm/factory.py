"""
LLM Provider Factory.
Creates LLM provider instances based on configuration.
"""
from backend.providers.llm.interface import LLMInterface
from backend.providers.llm.gemini_provider import GeminiProvider
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    @staticmethod
    def create_provider(provider_name: str = None) -> LLMInterface:
        """
        Create LLM provider instance.
        
        Args:
            provider_name: Name of provider ('gemini', 'openai', etc.)
                          Defaults to settings.llm_provider
        
        Returns:
            LLM provider instance
            
        Raises:
            ValueError: If provider name is not supported
        """
        provider_name = provider_name or settings.llm_provider
        provider_name = provider_name.lower()
        
        if provider_name == "gemini":
            logger.info("Creating Gemini LLM provider")
            return GeminiProvider()
        
        # Add more providers here as needed
        # elif provider_name == "openai":
        #     return OpenAIProvider()
        # elif provider_name == "cohere":
        #     return CohereProvider()
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available provider names."""
        return ["gemini"]  # Add more as implemented
