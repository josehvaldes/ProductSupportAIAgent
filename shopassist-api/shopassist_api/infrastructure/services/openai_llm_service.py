from typing import List, Dict, Optional, Generator
from openai import AzureOpenAI
import tiktoken
from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.logging_config import get_logger
from shopassist_api.application.settings.config import settings

logger = get_logger(__name__)

class OpenAILLMService(LLMServiceInterface):
    """Service for generating responses using Azure OpenAI"""
    
    def __init__(self):
        self.deployment = settings.azure_openai_model_deployment
        self.model_name = settings.azure_openai_model
        print(f"Using model: {self.model_name}, deployment: {self.deployment}")
        logger.info(f"Using model: {self.model_name}, deployment: {self.deployment}")
        self.encoding = tiktoken.encoding_for_model(self.model_name)
        self.total_tokens_used = 0
        self.total_cost = 0.0
        
        # Use shared credential manager
        credential_manager = get_credential_manager()
        token_provider = credential_manager.get_openai_token_provider()
        self.client = AzureOpenAI(
            api_version=settings.azure_openai_api_version or "2024-02-01",
            azure_endpoint=settings.azure_openai_endpoint,
            azure_ad_token_provider=token_provider
        )
        
    def generate_response(
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
            # Count input tokens
            input_text = "\n".join([m['content'] for m in messages])
            input_tokens = len(self.encoding.encode(input_text))
            
            logger.info(f"Generating response (input tokens: {input_tokens})")
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
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
            
            # Calculate cost (GPT-4o-mini pricing)
            # Input: $0.150 per 1M tokens
            # Output: $0.600 per 1M tokens
            input_cost = (prompt_tokens / 1_000_000) * 0.150
            output_cost = (completion_tokens / 1_000_000) * 0.600
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
