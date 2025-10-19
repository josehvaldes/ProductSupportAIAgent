"""
Shop Assistant AI Agent - Main agent orchestrator.
"""
from typing import Dict, Optional, List
from shopassist_api.application.settings.config import settings
from shopassist_api.application.ai.models.llm_client import LLMClient
from shopassist_api.application.ai.retrieval.product_retriever import ProductRetriever
from shopassist_api.application.ai.prompts.shop_assistant_prompts import ShopAssistantPrompts


class ShopAssistantAgent:
    """
    Main Shop Assistant AI Agent that orchestrates different AI components.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.product_retriever = ProductRetriever()
        self.prompts = ShopAssistantPrompts()
        
    async def process_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Process a user message and return AI response.
        
        Args:
            message: User's input message
            conversation_id: Optional conversation ID for context
            user_id: Optional user ID for personalization
            
        Returns:
            Dict containing response message and metadata
        """
        try:
            # 1. Analyze user intent
            intent = await self._analyze_intent(message)
            
            # 2. Retrieve relevant product information if needed
            context = await self._get_relevant_context(message, intent)
            
            # 3. Generate response using LLM
            response = await self._generate_response(message, context, intent)
            
            # 4. Generate suggestions
            suggestions = await self._generate_suggestions(message, intent)
            
            return {
                "message": response,
                "conversation_id": conversation_id or "new_conversation",
                "suggestions": suggestions,
                "intent": intent
            }
            
        except Exception as e:
            return {
                "message": "I'm sorry, I encountered an error while processing your request. Please try again.",
                "conversation_id": conversation_id or "error",
                "suggestions": [],
                "error": str(e)
            }
    
    async def _analyze_intent(self, message: str) -> str:
        """Analyze user intent from the message."""
        # TODO: Implement intent classification
        # For now, return a simple classification
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["price", "cost", "expensive", "cheap"]):
            return "price_inquiry"
        elif any(word in message_lower for word in ["recommend", "suggest", "best", "looking for"]):
            return "product_recommendation"
        elif any(word in message_lower for word in ["compare", "difference", "vs", "versus"]):
            return "product_comparison"
        elif any(word in message_lower for word in ["available", "stock", "in stock"]):
            return "availability_check"
        else:
            return "general_inquiry"
    
    async def _get_relevant_context(self, message: str, intent: str) -> str:
        """Retrieve relevant context for the user's query."""
        try:
            # Use the product retriever to find relevant products
            relevant_products = await self.product_retriever.search(message, top_k=5)
            return relevant_products
        except Exception:
            return "No specific product information available."
    
    async def _generate_response(self, message: str, context: str, intent: str) -> str:
        """Generate AI response using LLM."""
        try:
            prompt = self.prompts.get_response_prompt(message, context, intent)
            response = await self.llm_client.generate_response(prompt)
            return response
        except Exception:
            return "I'm here to help you with product questions and recommendations. How can I assist you today?"
    
    async def _generate_suggestions(self, message: str, intent: str) -> List[str]:
        """Generate follow-up suggestions."""
        # TODO: Implement intelligent suggestion generation
        suggestions = {
            "price_inquiry": [
                "Would you like to see similar products in different price ranges?",
                "Do you want to know about current promotions?"
            ],
            "product_recommendation": [
                "Would you like to see customer reviews?",
                "Do you need help comparing options?"
            ],
            "general_inquiry": [
                "Can I help you find a specific product?",
                "Would you like to see our featured items?"
            ]
        }
        
        return suggestions.get(intent, [
            "How else can I help you today?",
            "Would you like to explore our product categories?"
        ])
