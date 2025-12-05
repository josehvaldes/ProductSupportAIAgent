
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
from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.application.prompts.agent_templates import ProductSearchTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.interfaces.di_container import get_retrieval_service

from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)


#region ProductSearchAgent
class ProductSearchExpandedAgentState(TypedDict):
    """State schema for ProductSearchAgent"""
    messages: Annotated[list, operator.add]
    user_queries: Optional[list[str]] = None
    categories: Optional[list[str]] = None
    top_k: int = 3
    price_filter: Optional[PriceFilter] = None



@tool
@traceable(name="search_agent.search_product", tags=["search", "agent_tool","products"], metadata={"version": "2.0"})
async def search_products(state:ProductSearchExpandedAgentState) -> dict:
    """Tool to search products based on user query.
    Args:
        state (ProductSearchAgentState): The current state of the agent.
        state includes:
            - user_queries: The user's search queries.
            - categories: List of categories to filter the search.
            - top_k: Number of top products to retrieve.
            - price_filter: Optional price filter extracted from the query.
    Returns:
        dict: A dictionary containing the search results and context.
    """
    queries = state.get("user_queries", "")
    #hardcode top_k for now
    top_k = 3 #state.get("top_k", 3)
    
    price_filter = state.get("price_filter", None)

    filters = {}
    if price_filter:
        if price_filter.min_price is not None:
            filters['min_price'] = price_filter.min_price
        if price_filter.max_price is not None:
            filters['max_price'] = price_filter.max_price

    categories = state.get("categories", [])
    

    # Identify categories first
    retrieval = get_retrieval_service()    

    if categories and len(categories) > 0:
        filters = {**filters, **{'categories': categories}}

    logger.info(f"Searching products for query: {queries} with top_k={top_k}, filters={filters} and categories={categories}")
    products = await retrieval.retrieve_products_query_list(queries,
                enriched=True,
                top_k=top_k, 
                filters=filters)

    if not products or len(products) == 0:
        logger.warning(f"No products found for query: [{queries}] with filters={filters}")
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
    logger.info(f"Retrieved {formatted_products} products for query: [{queries}]")
    return {
        "context": context,
        "products": formatted_products
    }

class ProductSearchExpandedAgent:

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
        if ProductSearchExpandedAgent.cache_checkpointer is None:
            logger.info(f"Initializing Redis Checkpointer for ProductSearchAgent: {settings.redis_url}")
            async with AsyncRedisSaver.from_conn_string(settings.redis_url, ttl={ "default_ttl":1440, "refresh_on_read": True }) as checkpointer:
                await checkpointer.asetup()
                ProductSearchExpandedAgent.cache_checkpointer = checkpointer

        agent = create_agent(
                model=self.llm,
                tools=[search_products],
                checkpointer= ProductSearchExpandedAgent.cache_checkpointer,  
                system_prompt= ProductSearchTemplates.SYSTEM_PROMPT_EXPANDED,
                state_schema=ProductSearchExpandedAgentState,
            )
        return agent

    @traceable(name="search_agent.ainvoke", tags=["search", "ainvoke","products"], metadata={"version": "2.0"})
    async def ainvoke(self, state: dict) -> AgentResponse:

        session_Id: Optional[str] = state.get("session_Id", None)
        if session_Id is  None:
            session_Id = uuid.uuid4().hex[:12]

        if self.agent is None:
            self.agent = await self._get_agent()
        
        user_query: str = state.get("user_query", None)
        expanded_queries: list[str] = state.get("expanded_queries", [])

        if len(expanded_queries) == 0 and user_query:
            expanded_queries = [user_query]

        if len(expanded_queries) == 0:
            raise ValueError("expanded_queries cannot be empty. Add the original user_query if no expansion is available.")

        categories: list[str] = state.get("categories", [])

        logger.info(f"Invoking agent with session_Id: {session_Id}, expanded_queries: {expanded_queries}, categories: {categories}")

        result = await self.agent.ainvoke(
            {"messages": [ HumanMessage(content=f"user_queries: {expanded_queries}\n\n categories: {categories}") ],},
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

        
        return AgentResponse (
            message=response, 
            sources=sources, 
            agent_name=f"product_search_expanded_{self.model_deployment}",
            metadata= Metadata(
                id=f"product_search_expanded_agent",
                input_token=sum_input_tokens,
                output_token=sum_output_tokens,
                total_token=sum_total_tokens
            )
        )
#endregion



  
        