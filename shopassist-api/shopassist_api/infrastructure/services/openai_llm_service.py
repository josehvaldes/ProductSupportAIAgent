from typing import List, Dict, Generator
from langsmith import traceable
from openai import AsyncAzureOpenAI
import tiktoken
from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.logging_config import get_logger
from shopassist_api.application.settings.config import settings
from threading import RLock

logger = get_logger(__name__)

class OpenAILLMService(LLMServiceInterface):
    """Service for generating responses using Azure OpenAI"""
    
    # Class-level singleton for Azure OpenAI client
    _client = None
    _client_lock = RLock()
    
    def __init__(self, model_name:str = None, deployment_name: str = None):
        self.model_name = model_name or settings.azure_openai_model
        self.deployment = deployment_name or settings.azure_openai_model_deployment
        logger.info(f"Using model: {self.model_name}, deployment: {self.deployment}")
        self.encoding = tiktoken.encoding_for_model(self.model_name)
        self.total_tokens_used = 0
        self.total_cost = 0.0
        
        self.input_cost = 0.0
        self.output_cost = 0.0

        # Initialize singleton client
        self._initialize_client()
        self.client = OpenAILLMService._client
        
    def _initialize_client(self):
        """Initialize the Azure OpenAI client as singleton."""

        if self.model_name == "gpt-4.1-mini":
            logger.info("Configuring for gpt-4.1-mini pricing")
            self.input_cost = 0.40
            self.output_cost = 1.60
        elif self.model_name == "gpt-4.1-nano":
            logger.info("Configuring for gpt-4.1-nano pricing")
            self.input_cost = 0.1
            self.output_cost = 0.4

        if OpenAILLMService._client is None:
            with OpenAILLMService._client_lock:
                # Double-check after acquiring lock
                if OpenAILLMService._client is None:
                    logger.info("Initializing singleton Azure OpenAI client")
                    
                    # Use shared credential manager
                    credential_manager = get_credential_manager()
                    token_provider = credential_manager.get_openai_token_provider()
                    logger.info(f"Using Azure OpenAI endpoint: {settings.azure_openai_endpoint}")
                    OpenAILLMService._client = AsyncAzureOpenAI(
                        api_version=settings.azure_openai_api_version or "2024-02-01",
                        azure_endpoint=settings.azure_openai_endpoint,
                        azure_ad_token_provider=token_provider
                    )
                else:
                    logger.info("Using existing singleton Azure OpenAI client")
    
    @traceable(name="llm.generate_response", tags=["llm", "openai", "azure"], metadata={"version": "1.0"})
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> Dict:
        """
        Generate a response from the LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Max tokens in response
            
        Returns:
            Dict with response text, tokens used, and cost
        """
        try:
            
            if self.client is None:
                raise ValueError("Azure OpenAI client is not initialized.")
            if not messages:
                logger.error("Cannot generate response: messages list is empty")
                raise ValueError("Messages list cannot be empty. At least one message is required to generate a response.")

            # Count input tokens
            input_text = "\n".join([m['content'] for m in messages])
            input_tokens = len(self.encoding.encode(input_text))
            
            logger.info(f"Generating response (input tokens: {input_tokens}) for deployment {self.deployment}")
            # Call Azure OpenAI
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            # Token usage
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            # Cost calculation            
            input_cost = (prompt_tokens / 1_000_000) * self.input_cost
            output_cost = (completion_tokens / 1_000_000) * self.output_cost
            total_cost = input_cost + output_cost
            
            self.total_tokens_used += total_tokens
            self.total_cost += total_cost
            
            logger.info(
                f"Response generated: {completion_tokens} tokens, "
                f"${total_cost:.6f}, finish: {finish_reason}"
            )
            
            return {
                "response": assistant_message,
                "finish_reason": finish_reason,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens
                },
                "cost": total_cost
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    @traceable(name="llm.streaming_response", tags=["llm", "openai", "azure"], metadata={"version": "1.0"})    
    def streaming_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response (for better UX)
        
        Yields:
            Chunks of response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content # Here Yield content chunks
                    
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
            "avg_cost_per_call": self.total_cost / max(1, self.total_tokens_used / 1000)
        }

    async def health_check(self) -> bool:
        """Ping the service to check connectivity"""
        try:
            # Simple test call
            if self.client is None:
                return False

            response = self.client.models.list()
            if response:
                return True
            return False
        except Exception as e:
            logger.error(f"OpenAI LLM health check failed: {e}")
            return False