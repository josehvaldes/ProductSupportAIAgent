from typing import List, Dict


class TestPromptTemplates:
    """
    Test prompt templates for different query types
    """
    SYSTEM_PROMPT = """You are a test assistant designed to help with evaluating prompt templates.

Your role is to:
- Provide consistent and clear responses based on the prompts given
- End response with a haiku about topic of the query
    """
    @staticmethod
    def sample_prompt(
        query: str,
        context: str = "",
        conversation_history: str = ""
    ) -> List[Dict[str, str]]:
        """
        Sample prompt for testing
        """
        user_message = f"""topic: {query}"""

        return [
            {"role": "system", "content": TestPromptTemplates.SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]


class PromptTemplates:
    """
    Prompt templates for different query types
    """
    
    SYSTEM_PROMPT = """You are ShopAssist, an intelligent product support assistant for an electronics store.

Your role is to:
- Help customers discover products that meet their needs
- Provide accurate product information (specifications, pricing, availability)
- Answer questions about policies (returns, shipping, warranty)
- Compare products when asked
- Be concise, helpful, and friendly

Guidelines:
- ONLY use information provided in the context below
- If information isn't in the context, say "I don't have that information" and offer to help differently
- Never make up product details, prices, or specifications
- Format product information clearly with bullet points
- Include product names, prices, and key features
- When unsure, offer to connect customer with human support
- Use markdown formatting for better readability

CRITICAL: Never fabricate information. If you don't know, admit it."""

    @staticmethod
    def product_query_prompt(
        query: str,
        context: str,
        conversation_history: str = ""
    ) -> List[Dict[str, str]]:
        """
        Prompt for product-related queries
        """
        user_message = f"""Customer query: {query}

Product Information (Retrieved from database):
{context}

{f"Conversation history:\n{conversation_history}" if conversation_history else ""}

Based on the product information above, provide a helpful response to the customer's query.

Format your response with:
1. A brief answer to their question
2. Product recommendations (if applicable) with:
   - Product name
   - Price
   - Key features (2-3 bullets)
3. Ask if they need more information

Keep your response concise (max 200 words) and friendly."""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    
    @staticmethod
    def policy_query_prompt(
        query: str,
        context: str,
        conversation_history: str = ""
    ) -> List[Dict[str, str]]:
        """
        Prompt for policy-related queries
        """
        user_message = f"""Customer query: {query}

Policy Information (Retrieved from knowledge base):
{context}

{f"Conversation history:\n{conversation_history}" if conversation_history else ""}

Based on the policy information above, provide a clear and concise answer to the customer's question.

Format your response:
1. Direct answer to their question
2. Key policy details (bullet points)
3. Any relevant exceptions or conditions
4. Contact information if they need more help

Keep it concise and easy to understand."""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    
    @staticmethod
    def comparison_prompt(
        query: str,
        products: List[Dict],
        conversation_history: str = ""
    ) -> List[Dict[str, str]]:
        """
        Prompt for product comparison
        """
        # Format products for comparison
        product_details = []
        for i, product in enumerate(products, 1):
            details = f"""Product {i}: {product['title']}
- Price: ${product['price']:.2f}
- Category: {product['category']}
- Description: {product.get('description', 'N/A')[:200]}"""
            product_details.append(details)
        
        products_text = "\n\n".join(product_details)
        
        user_message = f"""Customer wants to compare products: {query}

Products to compare:
{products_text}

{f"Conversation history:\n{conversation_history}" if conversation_history else ""}

Create a helpful comparison focusing on:
1. Key differences in features
2. Price comparison
3. Which product is better for specific use cases
4. Your recommendation based on their needs

Use a table or bullet points for clarity."""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    
    @staticmethod
    def no_results_prompt(query: str) -> List[Dict[str, str]]:
        """
        Prompt when no results found
        """
        user_message = f"""Customer query: {query}

Unfortunately, no matching products were found in our database.

Provide a helpful response:
1. Apologize for not finding exact matches
2. Suggest alternative search terms or categories
3. Offer to help with a different query
4. Mention they can contact support for special requests

Keep it friendly and helpful."""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    

    
class ClassificationPrompts:
    """
    Prompts for classification tasks
    """
    INTENT_CLASSIFICATION_PROMPT = """You are an intent classification system for ShopAssist, an electronics store assistant.

Analyze the user's message and classify it into ONE of these intent categories:

1. product_search - User wants to find products by features/needs
   Examples: "I need a full frame camera", "which smartphones have cameras with zoom higher than 10x"

2. product_details - User asks about specific product specifications
   Examples: "does the Samsung z flip 5 have camera stabilization", "what characteristics have the bose smart soundbar"

3. product_comparison - User wants to compare multiple products
   Examples: "what alternatives do I have to a Bose Smart Sound bar", "compare the smartTVs TCL vs xiaomi"

4. policy_question - User asks about return/shipping/warranty policies
   Examples: "when will my package arrive", "what if I want to return the product"

5. general_support - User needs help with troubleshooting or how-to
   Examples: "The TCL smart TV has black dots in the screen", "the carrier came but I was not at home"

6. chitchat - Greetings, small talk, or off-topic conversation
   Examples: "Hello", "Are you a RAG agent?", "where is the company located?"

7. out_of_scope - Order management, account issues (requires human support)
   Examples: "The Order page is empty, why?", "who is going to deliver the package?"

Respond with ONLY the intent category name and a confidence score (0-100).
Format: intent_name|confidence_score

Example response: product_search|95"""

    @staticmethod
    def intent_classification_prompt(user_message: str) -> List[Dict[str, str]]:
        """
        Prompt for intent classification
        """
        
        return [
            {"role": "system", "content": ClassificationPrompts.INTENT_CLASSIFICATION_PROMPT},
            {"role": "user", "content": user_message}
        ]

