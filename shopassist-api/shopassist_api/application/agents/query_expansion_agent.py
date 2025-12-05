from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from contextlib import contextmanager
from langchain_community.callbacks import get_openai_callback
from langsmith import traceable

from shopassist_api.application.agents.base import AgentDecision, Metadata
from shopassist_api.application.interfaces.di_container import get_retrieval_service
from shopassist_api.application.prompts.agent_templates import QueryExpansionTemplates
from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager


from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)

@contextmanager
def track_tokens():
    """Context manager to track token usage for any LLM call"""
    with get_openai_callback() as cb:
        yield cb

async def get_categories_for_queries(queries:list[str]) -> list[str]:
    """Extract categories from a list of queries."""
    all_categories = set()
    retrieval = get_retrieval_service()
    for query in queries:
        #TODO send batch requests to improve performance
        categories = await retrieval.retrieve_top_categories(query, top_k=settings.TOP_K_CATEGORIES)
        cat_names = [ cat["name"] for cat in categories ]
        all_categories.update(cat_names)
    
    logger.info(f"Extracted categories for queries {queries}: {all_categories}")
    return list(all_categories)

class QueryExpansionAgent:
    
    def __init__(self, model_deployment:str = None):
        self.llm = None
        self.prompt = None
        self.model_deployment = model_deployment or settings.azure_openai_nano_model_deployment
        self._initialize_llm()


    def _initialize_llm(self):
        if self.llm is None:
            credential_manager = get_credential_manager()
            token_provider = credential_manager.get_openai_token_provider()

            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
                deployment_name=self.model_deployment,
                azure_ad_token_provider=token_provider,
                temperature=0
            ).with_structured_output(AgentDecision)
        


    @traceable(name="query_expansion_agent.expand_query", tags=["query_expansion", "agent"], metadata={"version": "2.0"})
    async def expand_query(self, user_query: str, context:dict= None) -> dict:
        """Decide whether to expand the user query."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", QueryExpansionTemplates.SYSTEM_PROMPT),
            ("human", "Query: {query}\n\nContext: {context}")
            ])
        
        messages = prompt.format_messages(query=user_query, context=context or "")

        with track_tokens() as token_tracker:
            decision = self.llm.invoke(messages)
        
        logger.info(f"Expansion decision: {decision}")
        return {
            "results": decision.results,
            "reasoning": decision.reasoning,
            "metadata": {
                "input_token": token_tracker.prompt_tokens,
                "output_token": token_tracker.completion_tokens,
                "total_token": token_tracker.total_tokens
            }
        }
    
    @traceable(name="query_expansion_agent.select_categories", tags=["query_expansion", "category_selection", "agent"], metadata={"version": "2.0"})
    async def select_categories(self, queries:list[str], categories:list[str], top_k:int=3) -> AgentDecision:
        """Select relevant categories from the extracted list."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", QueryExpansionTemplates.CATEGORY_SELECTION_SYSTEM_PROMPT),
            ("human", "Queries: {queries}\n\ntop_k:{top_k}\n\nExtracted Categories: {categories}")
            ])
        
        messages = prompt.format_messages(queries=queries, categories=categories, top_k=top_k)

        with track_tokens() as token_tracker:
            decision = self.llm.invoke(messages)
        
        logger.info(f"Category selection decision: {decision}")
        return {
            "results": decision.results,
            "reasoning": decision.reasoning,
            "metadata": {
                "input_token": token_tracker.prompt_tokens,
                "output_token": token_tracker.completion_tokens,
                "total_token": token_tracker.total_tokens
            }
        }

    @traceable(name="query_expansion_agent.ainvoke", tags=["query_expansion", "ainvoke"], metadata={"version": "2.0"})
    async def ainvoke(self, state: dict) -> dict:
        """Expand the user query based on context."""
        user_query: str = state.get("user_query", "")
        context: dict = state.get("context", {})
        variations = context.get("num_variations", settings.query_expansion_max_variations)
        context = {
            "num_variations": variations,
        }

        if user_query is None or user_query.strip() == "":
            raise ValueError("query cannot be empty.")

        logger.info(f"QueryExpansionAgent: Expanding query: [{user_query}] with context: [{context}]")

        decision = await self.expand_query(
            user_query=user_query,
            context=context
        )

        expanded_queries = decision["results"] or [user_query]

        logger.info(f"Expanded queries: {expanded_queries}")
        
        categories = await get_categories_for_queries(expanded_queries)
        
        category_decision: AgentDecision = await self.select_categories(
            queries=expanded_queries,
            categories=categories,
            top_k=settings.top_k_query_expansion_categories
        )
        
        selected_categories = category_decision["results"] or []
        
        logger.info(f"Selected categories: {selected_categories}. Reasoning: {category_decision['reasoning']}")
        
        return {
            "agent_name": f"query_expansion_agent_{self.model_deployment}",
            "original_query": user_query,
            "expanded_queries": expanded_queries,
            "categories": selected_categories,
            "metadata": Metadata(
                id="query_expansion_agent",
                input_token=decision["metadata"]["input_token"] + category_decision["metadata"]["input_token"],
                output_token=decision["metadata"]["output_token"] + category_decision["metadata"]["output_token"],
                total_token=decision["metadata"]["total_token"] + category_decision["metadata"]["total_token"]
            )   
        }