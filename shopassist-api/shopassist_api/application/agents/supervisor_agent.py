from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from contextlib import contextmanager
from langchain_community.callbacks import get_openai_callback

from shopassist_api.application.agents.base import Metadata, RouteDecision, RouteDecisionResponse
from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.application.prompts.agent_templates import RouteTemplates

from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)

@contextmanager
def track_tokens():
    """Context manager to track token usage for any LLM call"""
    with get_openai_callback() as cb:
        yield cb

#region SupervisorAgent
class SupervisorAgent:
    
    def __init__(self):
        self.llm = None
        self.prompt = None
        self._initialize_llm()

    def _initialize_llm(self):
        if self.llm is None:
            credential_manager = get_credential_manager()
            token_provider = credential_manager.get_openai_token_provider()

            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
                deployment_name=settings.azure_openai_model_deployment,
                azure_ad_token_provider=token_provider,
                temperature=0
            ).with_structured_output(RouteDecision)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", RouteTemplates.SYSTEM_PROMPT_SHORT),
            ("human", "Query: {query}\n\nContext: {context}")
            ])

    async def route(self, user_query: str, context:dict= None) -> RouteDecisionResponse:
        """Decide which agent to route the query to."""

        messages = self.prompt.format_messages(query=user_query, context=context or "")

        with track_tokens() as token_tracker:
            decision = await self.llm.ainvoke(messages)
        
        logger.info(f"SupervisorAgent: Routing decision: {decision}")
        return RouteDecisionResponse(
            agent=decision.agent,
            confidence=decision.confidence,
            reasoning=decision.reasoning,
            metadata=Metadata(
                input_token=token_tracker.prompt_tokens,
                output_token=token_tracker.completion_tokens,
                total_token=token_tracker.total_tokens)
        )

#endregion SupervisorAgent