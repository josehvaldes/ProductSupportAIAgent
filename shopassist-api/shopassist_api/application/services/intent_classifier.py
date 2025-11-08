from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface
from shopassist_api.application.prompts.templates import ClassificationPrompts
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)


class IntentClassifier:    
    """Classify user intent using LLM.
        Deprecated - use ContextAnalysisPrompts and LLMSufficiencyBuilder instead.
    """

    VALID_INTENTS = [
                    "product_search",
                    "product_details", 
                    "product_comparison",
                    "policy_question", 
                    "general_support", 
                    "chitchat", 
                    "out_of_scope"
                ]                

    def __init__(self, llm_service: LLMServiceInterface):
        self.llm_service = llm_service

    async def classify(self, user_message: str) -> tuple[str, float]:
        # Placeholder implementation

        """
        Classify user intent using LLM.
        
        Returns:
            tuple: (intent_name, confidence_score)
        """
        logger.info(f"Classifying intent for message: {user_message}")
        messages = ClassificationPrompts.intent_classification_prompt(user_message)
        
        response = await self.llm_service.generate_response(
            messages=messages,
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=20     # Only need short response
        )

        logger.info(f"LLM classification response: {response}")
        # Parse response: "product_search|95"
        return self.parse_classification_response(response['response'])
        
    def parse_classification_response(self, response: str) -> tuple[str, float]:
        """Parse LLM response into intent and confidence."""
        try:
            parts = response.strip().split('|')
            if len(parts) == 2:
                intent = parts[0].strip()
                confidence = float(parts[1].strip())
                
                # Validate intent is one of expected values

                if intent in IntentClassifier.VALID_INTENTS and 0 <= confidence <= 100:
                    return intent, confidence
            
            # Fallback if parsing fails
            return "general_support", 50.0
            
        except Exception as e:
            # Log the error
            return "general_support", 50.0