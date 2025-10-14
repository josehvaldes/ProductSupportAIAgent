"""
Tests for AI components.
"""
import pytest
from shopassist_api.ai.agents.shop_assistant import ShopAssistantAgent
from shopassist_api.ai.prompts.shop_assistant_prompts import ShopAssistantPrompts
from shopassist_api.ai.embeddings.embedding_service import EmbeddingService


@pytest.mark.asyncio
async def test_shop_assistant_agent():
    """Test the main shop assistant agent."""
    agent = ShopAssistantAgent()
    
    # Test basic message processing
    response = await agent.process_message("I'm looking for headphones")
    
    assert isinstance(response, dict)
    assert "message" in response
    assert "conversation_id" in response
    assert "suggestions" in response
    assert isinstance(response["suggestions"], list)


def test_intent_analysis():
    """Test intent analysis functionality."""
    agent = ShopAssistantAgent()
    
    # Test different intents
    price_intent = agent._analyze_intent("How much does this cost?")
    assert "price" in price_intent.lower()
    
    recommendation_intent = agent._analyze_intent("Can you recommend something?")
    assert "recommend" in recommendation_intent.lower()


def test_prompt_generation():
    """Test prompt template generation."""
    prompts = ShopAssistantPrompts()
    
    # Test response prompt
    prompt = prompts.get_response_prompt(
        user_message="I need headphones",
        context="Available headphones: Sony, Bose",
        intent="product_recommendation"
    )
    
    assert "headphones" in prompt
    assert "Sony" in prompt
    assert "Bose" in prompt
    assert "product_recommendation" in prompt


def test_embedding_service():
    """Test embedding service functionality."""
    service = EmbeddingService()
    
    # Test cosine similarity
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    vec3 = [0.0, 1.0, 0.0]
    
    similarity_identical = service.cosine_similarity(vec1, vec2)
    similarity_different = service.cosine_similarity(vec1, vec3)
    
    assert similarity_identical == 1.0
    assert similarity_different == 0.0
