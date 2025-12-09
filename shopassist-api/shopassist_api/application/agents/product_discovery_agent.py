import json
import operator
from typing import Annotated, Optional, TypedDict
import uuid
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langsmith import traceable
from pydantic import BaseModel, Field
from shopassist_api.application.agents.agent_utils import AgentTools
from shopassist_api.application.agents.base import AgentResponse, Metadata, PriceFilter
from shopassist_api.application.agents.token_monitor import token_monitor_dec
from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.application.prompts.agent_templates import ProductSearchTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.interfaces.di_container import get_retrieval_service

from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)

   
#region ProductDiscoveryAgentState
class ProductDiscoveryAgentState(TypedDict):
    """State schema for ProductDiscoveryAgentState"""
    messages: Annotated[list, operator.add]
    user_query: Optional[str] = None
    top_k: int = 3
    price_filter: Optional[PriceFilter] = None
    categories: Optional[list[str]] = None

@tool(name_or_callable="search_categories")
@traceable(name="product_discovery.search_categories", tags=["search", "agent_tool","categories"], metadata={"version": "2.0"})
async def search_categories(query:str) -> list[str]:
    """Extract categories from a query.
    Args:
        query (str): The user's search query.
    """
    retrieval = get_retrieval_service()
    logger.info(f"Extracting categories for query: [{query}], top_k={settings.top_k_categories}, radius={settings.threshold_category_similarity}")  
    categories = await retrieval.retrieve_top_categories(query, top_k=settings.top_k_categories, radius=settings.threshold_category_similarity)
    cat_names = [ cat["name"] for cat in categories ]
    
    logger.info(f"Extracted categories for query [{query}]: {cat_names}")
    return cat_names

@tool(name_or_callable="search_products")
@traceable(name="product_discovery.search_product", tags=["search", "agent_tool","products"], metadata={"version": "2.0"})
async def search_products(state:ProductDiscoveryAgentState) -> dict:
    """Tool to search products based on user query.
    Args:
        state (ProductDiscoveryAgentState): The current state of the agent.
        state includes:
            - user_query: The user's search query.
            - top_k: Number of top products to retrieve.
            - categories: List of categories to filter the search.
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

    logger.info(f"Searching products for query: [{query}] with top_k={top_k}, filters={filters}")
    # Identify categories first
    retrieval = get_retrieval_service()

    categories = state.get("categories", [])
    print(f"Categories from state: {categories}")
    products = []
    if categories and len(categories) > 0:
        # Use categories to filter products
        cat_filters = {**filters, **{'categories': categories}}
        logger.info(f"Identified filters with categories: {cat_filters} for query: [{query}]")
        products = await retrieval.retrieve_products(query,
                    enriched=True,
                    top_k=top_k, 
                    filters=cat_filters)

    # If no products found with categories, do a general search 
    if not products or len(products) == 0:
        logger.info(f"No products found with categories [{categories}]. Performing general search for query: [{query}]")
        products = await retrieval.retrieve_products(query,
                    enriched=True,
                    top_k=top_k, 
                    filters=filters)
    
    if not products or len(products) == 0:
        logger.info(f"No products found for query: [{query}] with filters: {filters}")
        return {
            "products": [],
            "context": "No products found matching your query."
        }
    
    context_builder = ContextBuilder()
    context = context_builder.build_product_context(products)
    formatted_products = [ {
        "id": prod['id'],
        "name": prod['name'],
        "category": prod['category'],
        "price": prod['price'],
        "brand": prod['brand'],
        "availability": prod['availability'],
        "image_url": prod['image_url'],
        "product_url": prod['product_url'],
        "distance": prod.get('distance', None)
    } for prod in products ]
    logger.info(f"Retrieved {formatted_products} products for query: [{query}]")
    return {
        "context": context,
        "products": formatted_products
    }

class ProductDiscoveryAgent:

    cache_checkpointer = None

    def __init__(self):
        
        credential_manager = get_credential_manager()
        token_provider = credential_manager.get_openai_token_provider()
        self.model_deployment = settings.azure_openai_model_deployment
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
                deployment_name=self.model_deployment,
                azure_ad_token_provider=token_provider,
                temperature=0
        )
        self.agent = None
        
    
    async def _get_agent(self):
        if ProductDiscoveryAgent.cache_checkpointer is None:
            logger.info(f"Initializing Redis Checkpointer for ProductDiscoveryAgent: {settings.redis_url}")
            async with AsyncRedisSaver.from_conn_string(settings.redis_url, ttl={ "default_ttl":1440, "refresh_on_read": True }) as checkpointer:
                await checkpointer.asetup()
                ProductDiscoveryAgent.cache_checkpointer = checkpointer

        agent = create_agent(
                model=self.llm,
                tools=[search_products, search_categories],
                checkpointer= ProductDiscoveryAgent.cache_checkpointer,  
                system_prompt= ProductSearchTemplates.SYSTEM_PROMPT_DISCOVERY,
                state_schema=ProductDiscoveryAgentState,
            )
        return agent

    @token_monitor_dec
    @traceable(name="product_discovery_agent.ainvoke", tags=["search", "ainvoke","products"], metadata={"version": "2.0"})
    async def ainvoke(self, state: dict) -> AgentResponse:
        
        user_query: str = state.get("user_query", "")
        session_Id: Optional[str] = state.get("session_Id", None)
        
        if user_query is None or user_query.strip() == "":
            raise ValueError("user_query cannot be empty.")

        if session_Id is  None:
            session_Id = uuid.uuid4().hex[:12]

        if self.agent is None:
            self.agent = await self._get_agent()

        logger.info(f"Invoking with session_Id: {session_Id} and user_query: {user_query}")
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
            if isinstance(msg, ToolMessage):
                if msg.name == "search_products":
                    if not msg.content or not isinstance(msg.content, str):
                        logger.warning(f"Invalid tool message content: {msg.content}")
                        continue
                    
                    content = msg.content.strip()
                    try:
                        if not content:
                            logger.warning("Tool message content is empty.")
                            continue
                        jsonobj = json.loads(content)
                        products = jsonobj.get("products", [])
                        sources.extend(products)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error while parsing tool message content: {e}")
                        logger.error(f"Content was: {content} \n end")  # Log first 200 chars of content
                        continue
            
            if isinstance(msg, AIMessage):
                metadata = msg.usage_metadata
                if metadata:
                    sum_input_tokens += metadata.get("input_tokens") or 0
                    sum_output_tokens += metadata.get("output_tokens") or 0
                    sum_total_tokens += metadata.get("total_tokens") or 0

        
        return AgentResponse (
            message=response, 
            sources=sources, 
            agent_name=f"product_discovery_agent",
            model=self.model_deployment,
            metadata= Metadata(
                id=f"product_discovery_agent",
                input_token=sum_input_tokens,
                output_token=sum_output_tokens,
                total_token=sum_total_tokens
            )
        )

    async def get_history(self, session_id: str) -> list[dict]:
        """Retrieve the message history for a given session ID."""
        if self.agent is None:
            self.agent = await self._get_agent()
        return await AgentTools.get_history(self.agent, session_id)
    
#endregion ProductSearchAgent

