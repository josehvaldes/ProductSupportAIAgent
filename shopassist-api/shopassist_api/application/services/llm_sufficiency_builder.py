from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface
from shopassist_api.application.prompts.templates import ContextAnalysisPrompts
from shopassist_api.logging_config import get_logger
import traceback

logger = get_logger(__name__)

class LLMSufficiencyBuilder:
    
    def __init__(self, llm_service):
        self.llm_service:LLMServiceInterface = llm_service
    
    async def analyze_sufficiency(self, query: str, history:str) -> dict:
        """
        Use LLM to analyze context sufficiency for the query.
        Returns:
        Respond with this JSON structure:
        {
            "intent_query": "<one of: product_search|product_details|product_comparison|policy_question|general_support|chitchat|out_of_scope>",
            "is_sufficient": "<yes or no>",
            "reason": "<brief explanation in 1-2 sentences>",
            "confidence": <float 0.0-1.0>,
            "query_retrieval_hint": "<refined search query or empty string>"
        }
        """
        try:
            print(f"Generating context analysis prompt [{history[0:100]}...]")
            messages = ContextAnalysisPrompts.context_analysis_prompt(query, history)

            llm_response = await self.llm_service.generate_response(messages=messages,
                                            temperature=0.1, max_tokens=500)
            response_text = llm_response['response']
            response = eval(response_text)
            return response
            
        except Exception as e:
            logger.error(f"Error parsing context analysis response: {e}")
            traceback.print_exc()
            return {}
        