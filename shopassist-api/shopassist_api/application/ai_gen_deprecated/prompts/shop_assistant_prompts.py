"""
Prompt templates for the Shop Assistant AI.
"""
from typing import Dict, Any


class ShopAssistantPrompts:
    """
    Collection of prompt templates for different shop assistant scenarios.
    """
    
    def __init__(self):
        self.system_prompt = """
You are a helpful and knowledgeable shop assistant AI. Your role is to:

1. Help customers find products that meet their needs
2. Provide accurate product information including prices, features, and availability
3. Make personalized recommendations based on customer preferences
4. Compare products when requested
5. Answer questions about shipping, returns, and store policies
6. Maintain a friendly, professional, and helpful tone

Guidelines:
- Always be honest about product availability and limitations
- If you don't have specific information, say so rather than guessing
- Focus on helping the customer make informed decisions
- Be concise but thorough in your responses
- Ask clarifying questions when needed to better assist the customer
"""
    
    def get_response_prompt(self, user_message: str, context: str, intent: str) -> str:
        """
        Generate a response prompt based on user message, context, and intent.
        
        Args:
            user_message: The user's input message
            context: Relevant product/context information
            intent: Classified user intent
            
        Returns:
            Formatted prompt for the LLM
        """
        prompt = f"{self.system_prompt}\n\n"
        
        if context and context != "No specific product information available.":
            prompt += f"AVAILABLE PRODUCT INFORMATION:\n{context}\n\n"
        
        prompt += f"CUSTOMER INTENT: {intent}\n\n"
        prompt += f"CUSTOMER MESSAGE: {user_message}\n\n"
        prompt += "Please provide a helpful response to the customer:"
        
        return prompt
    
    def get_intent_classification_prompt(self, user_message: str) -> str:
        """
        Generate a prompt for intent classification.
        """
        return f"""
Classify the following customer message into one of these intents:
- price_inquiry: Questions about product pricing
- product_recommendation: Requests for product suggestions
- product_comparison: Comparing different products
- availability_check: Checking if products are in stock
- general_inquiry: General questions or conversations

Customer message: "{user_message}"

Intent:"""
    
    def get_product_search_prompt(self, user_query: str) -> str:
        """
        Generate a prompt for product search query enhancement.
        """
        return f"""
Extract key product search terms from this customer query. Focus on:
- Product types/categories
- Brand names
- Specific features or requirements
- Price ranges
- Use cases

Customer query: "{user_query}"

Search terms:"""
    
    def get_recommendation_prompt(self, user_preferences: Dict[str, Any], available_products: str) -> str:
        """
        Generate a prompt for product recommendations.
        """
        preferences_text = "\n".join([f"- {k}: {v}" for k, v in user_preferences.items()])
        
        return f"""
{self.system_prompt}

CUSTOMER PREFERENCES:
{preferences_text}

AVAILABLE PRODUCTS:
{available_products}

Based on the customer's preferences and the available products, provide personalized recommendations. 
Explain why each recommendation matches their needs:"""
    
    def get_comparison_prompt(self, products_to_compare: str, comparison_criteria: str = "") -> str:
        """
        Generate a prompt for product comparison.
        """
        prompt = f"""
{self.system_prompt}

PRODUCTS TO COMPARE:
{products_to_compare}

"""
        
        if comparison_criteria:
            prompt += f"COMPARISON CRITERIA: {comparison_criteria}\n\n"
        
        prompt += """
Please provide a detailed comparison of these products. Include:
- Key features and differences
- Price comparison
- Pros and cons of each
- Recommendation based on different use cases

Comparison:"""
        
        return prompt
