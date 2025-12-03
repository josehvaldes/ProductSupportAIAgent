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
from shopassist_api.application.agents.agent_utils import AgentTools
from shopassist_api.application.agents.base import AgentResponse, Metadata
from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.application.prompts.agent_templates import ProductDetailTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.interfaces.di_container import get_retrieval_service


from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)


#region ProductDetailAgent
class ProductDetailAgentState(TypedDict):

    """State schema for ProductDetailAgent"""
    messages: Annotated[list, operator.add]
    product_name: Optional[str] = None

@tool
@traceable(name="detail_agent.search_product", tags=["details", "agent_tool"], metadata={"version": "2.0"})
async def search_product(state:ProductDetailAgentState) -> dict:
    """Tool to search products based on user query.
    Args:
        state (ProductDetailAgentState): The current state of the agent.
        state includes:
            - product_name: The name of the product to get details for.
            - top_k: Number of top products to retrieve.
    Returns:
        dict: A dictionary containing the search results and context.
    """

    query = state.get("product_name", "")

    logger.info(f"Getting details for product: [{query}]")

    retrieval = get_retrieval_service()
    products = await retrieval.retrieve_products_adaptative(query,
            enriched=True,
            top_k=1)

    if not products or len(products) == 0:
        logger.info(f"No products found for query [{query}]")
        return {
            "products": [],
            "context": "No products found matching your query."
        }
    
    context_builder = ContextBuilder()
    context = context_builder.build_product_context(products)
    formatted_products = [ {
        "id": prod['id'],
        "name": prod['name'],
        "relevance_score": prod.get('relevance_score', 0),
        "category": prod['category'],
        "price": prod['price'],
        "brand": prod['brand'],
        "description": prod['description'],
        "availability": prod['availability'],
        "image_url": prod['image_url'],
        "product_url": prod['product_url']
    } for prod in products ]
    logger.info(f"Retrieved {formatted_products} products for query: [{query}]")
    return {
        "context": context,
        "products": formatted_products
    }


class ProductDetailAgent:

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
        if ProductDetailAgent.cache_checkpointer is None:
            logger.info(f"Initializing Redis Checkpointer for ProductDetailAgent: {settings.redis_url}")
            async with AsyncRedisSaver.from_conn_string(settings.redis_url, ttl={ "default_ttl":1440, "refresh_on_read": True }) as checkpointer:
                await checkpointer.asetup()
                ProductDetailAgent.cache_checkpointer = checkpointer

        agent = create_agent(
                model=self.llm,
                tools=[search_product],
                checkpointer= ProductDetailAgent.cache_checkpointer,  
                system_prompt= ProductDetailTemplates.SYSTEM_PROMPT,
                state_schema=ProductDetailAgentState,
            )
        return agent
    
    @traceable(name="detail_agent.ainvoke", tags=["details", "ainvoke"], metadata={"version": "2.0"})
    async def ainvoke(self, state: dict) -> AgentResponse:
        """Det products based on user query and product IDs."""
        user_query: str = state.get("user_query", "")
        session_Id: Optional[str] = state.get("session_Id", None)
        
        if user_query is None or user_query.strip() == "":
            raise ValueError("user_query cannot be empty.")

        if session_Id is  None:
            session_Id = uuid.uuid4().hex[:12]

        if self.agent is None:
            self.agent = await self._get_agent()

        logger.info(f"ProductDetailAgent: Invoking agent for query: [{user_query}] in session: {session_Id}")
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
            if isinstance(msg, ToolMessage) and msg.name == "search_product":
                jsonobj = json.loads(msg.content)
                products = jsonobj.get("products", [])
                sources.extend(products)
            
            if isinstance(msg, AIMessage):
                metadata = msg.usage_metadata
                if metadata:
                    sum_input_tokens += metadata.get("input_tokens") or 0
                    sum_output_tokens += metadata.get("output_tokens") or 0
                    sum_total_tokens += metadata.get("total_tokens") or 0
        

        return AgentResponse(
            message=response,
            sources=sources,
            agent_name="product_detail",
            metadata=Metadata(
                input_token=sum_input_tokens,
                output_token=sum_output_tokens,
                total_token=sum_total_tokens
            ))
    
    async def get_history(self, session_id: str) -> list[dict]:
        """Retrieve the message history for a given session ID."""
        if self.agent is None:
            self.agent = await self._get_agent()
        return await AgentTools.get_history(self.agent, session_id)