import logging
from typing import Any, Dict, List, Optional

from groq import Groq

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    A service class to interact with various Large Language Models (LLMs),
    starting with Groq.

    This class centralizes LLM API calls, manages API keys, and provides
    a consistent interface for different LLM providers.
    """

    _groq_client: Optional[Groq] = None

    def __init__(self):
        """
        Initializes the LLMService.
        Lazy-loads clients for LLM providers as needed.
        """
        if settings.GROQ_API_KEY:
            self._groq_client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info("Groq client initialized.")
        else:
            logger.warning("GROQ_API_KEY is not set. Groq client will not be available.")

    async def get_groq_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama3-8b-8192",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 1.0,
        stream: bool = False,
        **kwargs: Any,
    ) -> Optional[Any]:
        """
        Gets a completion from the Groq API.

        Args:
            messages: A list of message dictionaries for the conversation.
            model: The LLM model to use (e.g., "llama3-8b-8192").
            temperature: Controls randomness in the output.
            max_tokens: The maximum number of tokens to generate.
            top_p: Controls diversity via nucleus sampling.
            stream: If True, returns a streaming response.
            **kwargs: Additional parameters for the Groq API call.

        Returns:
            The completion response from Groq, or None if the client is not initialized.
        """
        if not self._groq_client:
            logger.error("Groq client not initialized. Cannot get completion.")
            return None

        try:
            chat_completion = await self._groq_client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=stream,
                **kwargs,
            )
            return chat_completion
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return None


# Export an instance for easy access throughout the application
llm_service = LLMService()
