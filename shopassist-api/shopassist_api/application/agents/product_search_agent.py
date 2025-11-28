import json
import operator
from typing import Annotated, Any, Optional, TypedDict
import uuid
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.redis import RunnableConfig
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from pydantic import BaseModel, Field
from shopassist_api.application.agents.base import Metadata, ProductSearchResponse
from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.application.prompts.agent_templates import ProductSearchTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.interfaces.di_container import get_retrieval_service

from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)

class PriceFilter(BaseModel):
    """Extracted price range from user query"""
    min_price: Optional[float] = Field(None, description="Minimum price in USD")
    max_price: Optional[float] = Field(None, description="Maximum price in USD")
    confidence: float = Field(description="Confidence in extraction (0-1)")
    
#region ProductSearchAgent
class ProductSearchAgentState(TypedDict):
    """State schema for ProductSearchAgent"""
    messages: Annotated[list, operator.add]
    user_query: Optional[str] = None
    top_k: int = 3
    price_filter: Optional[PriceFilter] = None


@tool
async def search_products(state:ProductSearchAgentState) -> dict:
    """Tool to search products based on user query.
    Args:
        state (ProductSearchAgentState): The current state of the agent.
        state includes:
            - user_query: The user's search query.
            - top_k: Number of top products to retrieve.
            - price_filter: Optional price filter extracted from the query.
    Returns:
        dict: A dictionary containing the search results and context.
    """
    query = state.get("user_query", "")
    #hardcode top_k for now
    top_k = 3 #state.get("top_k", 3)
    
    price_filter = state.get("price_filter", None)

    filters = {}
    if price_filter:
        if price_filter.min_price is not None:
            filters['min_price'] = price_filter.min_price
        if price_filter.max_price is not None:
            filters['max_price'] = price_filter.max_price

    context_builder = ContextBuilder()
    
    logger.info(f"ProductSearchAgent: Searching products for query: [{query}] with top_k={top_k}, filters={filters}")
    # Identify categories first
    retrieval = get_retrieval_service()
    categories = await retrieval.retrieve_top_categories(query, top_k=settings.TOP_K_CATEGORIES)

    if categories and len(categories) > 0:
        category_names = []
        for cat in categories:
            if cat['score'] > settings.threshold_category_similarity:
                category_names.append(cat['name'])
        filters = {**filters, **{'categories': category_names}}

    logger.info(f"ProductSearchAgent: Identified filters: {filters} for query: [{query}]")
    products = await retrieval.retrieve_products(query,
                enriched=True,
                top_k=top_k, 
                filters=filters)

    if not products or len(products) == 0:
        return {
            "products": [],
            "context": "No products found matching your query."
        }

    context = context_builder.build_product_context(products)
    formatted_products = [ {
        "id": prod['id'],
        "name": prod['name'],
        "relevance_score": prod.get('relevance_score', 0)
    } for prod in products ]
    logger.info(f"ProductSearchAgent: Retrieved {formatted_products} products for query: [{query}]")
    return {
        "context": context,
        "products": formatted_products
    }

class ProductSearchAgent:

    cache_checkpointer = None

    def __init__(self):
        
        credential_manager = get_credential_manager()
        token_provider = credential_manager.get_openai_token_provider()
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
                deployment_name=settings.azure_openai_model_deployment,
                azure_ad_token_provider=token_provider,
                temperature=0
        )
        self.agent = None
        
    
    async def _get_agent(self):
        if ProductSearchAgent.cache_checkpointer is None:
            logger.info(f"Initializing Redis Checkpointer for ProductSearchAgent: {settings.redis_url}")
            async with AsyncRedisSaver.from_conn_string(settings.redis_url) as checkpointer:
                await checkpointer.asetup()
                ProductSearchAgent.cache_checkpointer = checkpointer

        agent = create_agent(
                model=self.llm,
                tools=[search_products],
                checkpointer= ProductSearchAgent.cache_checkpointer,  
                system_prompt= ProductSearchTemplates.SYSTEM_PROMPT,
                state_schema=ProductSearchAgentState,
            )
        return agent

    async def ainvoke(self, input: dict) -> ProductSearchResponse:
        
        user_query: str = input.get("user_query", "")
        session_Id: Optional[str] = input.get("session_Id", None)
        
        if user_query is None or user_query.strip() == "":
            raise ValueError("user_query cannot be empty.")

        if session_Id is  None:
            session_Id = uuid.uuid4().hex[:12]

        if self.agent is None:
            self.agent = await self._get_agent()

        logger.info(f"Invoking ProductSearchAgent with session_Id: {session_Id} and user_query: {user_query}")
        result = await self.agent.ainvoke(
            {"messages": [ HumanMessage(content=user_query) ],},
            {"configurable": {"thread_id": session_Id}}
        )

        messages = result["messages"]

        response = messages[-1].content

        sources = []
        sum_input_tokens = 0
        sum_output_tokens = 0
        sum_total_tokens = 0

        for msg in messages:
            if isinstance(msg, ToolMessage) and msg.name == "search_products":
                jsonobj = json.loads(msg.content)
                products = jsonobj.get("products", [])
                sources.extend(products)
            
            if isinstance(msg, AIMessage):
                metadata = msg.usage_metadata
                if metadata:
                    sum_input_tokens += metadata.get("input_tokens") or 0
                    sum_output_tokens += metadata.get("output_tokens") or 0
                    sum_total_tokens += metadata.get("total_tokens") or 0

        
        return ProductSearchResponse (
            message=response, 
            sources=sources, 
            agent_name="product_search",
            metadata= Metadata(
                input_token=sum_input_tokens,
                output_token=sum_output_tokens,
                total_token=sum_total_tokens
            )
        )

    async def get_history(self, session_id: str) -> list[dict]:
        """Retrieve the message history for a given session ID."""
        config:RunnableConfig = {
            "configurable": {
            "thread_id": session_id,
            }
        }

        if self.agent is None:
            self.agent = await self._get_agent()
        
        state = await self.agent.aget_state(config)         
        messages = state.values.get("messages", [])
        response = []
        for msg in messages:
            metadata = None
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
                if isinstance(msg, AIMessage):
                    if msg.usage_metadata:
                        metadata = {
                            "input_tokens": msg.usage_metadata.get("input_tokens"),
                            "output_tokens": msg.usage_metadata.get("output_tokens"),
                            "total_tokens": msg.usage_metadata.get("total_tokens")
                        }
            elif isinstance(msg, ToolMessage):
                role = "tool"
            else:
                role = type(msg).__name__.lower()
            
            response.append({
                "role": role,
                "content": msg.content,
                "metadata": metadata
            })
        
        return response
    
#endregion ProductSearchAgent

