import uuid
import json
import operator
import time

from typing import Optional, TypedDict, Annotated

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
from langgraph.runtime import Runtime
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.agents.middleware import before_model
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.redis import RedisSaver, RunnableConfig, CheckpointTuple
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from langsmith import traceable
from shopassist_api.application.agents.agent_utils import AgentTools
from shopassist_api.application.agents.base import Metadata, PolicyResponse
from shopassist_api.application.agents.token_monitor import token_monitor_dec
from shopassist_api.application.settings.config import settings
from shopassist_api.infrastructure.services.azure_credential_manager import get_credential_manager
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService
from shopassist_api.application.prompts.agent_templates import PolicyTemplates
from shopassist_api.infrastructure.services.milvus_service import MilvusService

from shopassist_api.logging_config import get_logger
logger = get_logger(__name__)

class PolicyAgentState(TypedDict):
    messages: Annotated[list, operator.add]
    user_query: str = ""
    top_k: int = 2

@tool
@traceable(name="policy_agent.search_knowledge_base", tags=["policy", "agent_tool"], metadata={"version": "2.0"})
async def search_knowledge_base(state: PolicyAgentState) -> dict:
    """Tool to search knowledge base in Milvus and return context and IDs of the sources.
        the results include information about Return Policy, Shipping Information, Warranty Details, etc.
    Args:
        state (PolicyAgentState): The current state of the agent.
    Returns:
        dict: context and document IDs
    """

    milvus = MilvusService( settings.milvus_host, settings.milvus_port)
    embedder = TransformersEmbeddingService(settings.transformers_embedding_model)

    user_query = state.get("user_query", "")
    top_k =2 # state.get("top_k", 2)
    
    logger.info(f"PolicyAgent: Searching knowledge base with query: [{user_query}] Top K: {top_k}")

    query_embedding = await embedder.generate_embedding(user_query)
    docs = milvus.search_knowledge_base(query_embedding= query_embedding, top_k=top_k)
    context_parts = []
    doc_names = []
    for i, chunk in enumerate(docs, 1):
        chunk_text = f"Source {i} [{chunk['doc_id']}]:\n{chunk['text']}"
        context_parts.append(chunk_text)
        doc_names.append(chunk['doc_id'])
    
    context = "\n\n".join(context_parts)
    logger.info(f"PolicyAgent: Retrieved {doc_names} from knowledge base for query: [{user_query}]")
    return { "context": context, "doc_ids": doc_names }

@before_model
async def trim_message_history(state: PolicyAgentState, runtime:Runtime) -> PolicyAgentState:
    """Middleware to trim message history if it exceeds a certain length.
    Used to control memory usage for in-memory checkpointer.
    """
    messages = state["messages"]
    if len(messages) <= 10:
        return None

    first_msg = messages[0]
    recent_messages = messages[-9:] if len(messages) % 10 == 0 else messages[-10:]
    new_messages = [first_msg] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }


#region PolicyAgent wrapper class
class PolicyAgent:

    def __init__(self):
        
        credential_manager = get_credential_manager()
        token_provider = credential_manager.get_openai_token_provider()
        self.deployment_name = settings.azure_openai_model_deployment
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            deployment_name=self.deployment_name,
            azure_ad_token_provider=token_provider,
            temperature=0.3
        )
        self.agent = None
        
    async def _get_agent(self):

        agent = create_agent (
                model=self.llm,
                tools=[search_knowledge_base],
                system_prompt= PolicyTemplates.SYSTEM_PROMPT,
                state_schema=PolicyAgentState,
            )
        return agent

    @token_monitor_dec
    @traceable(name="policy_agent.ainvoke", tags=["policy", "agent"], metadata={"version": "2.0"})
    async def ainvoke(self, input: dict) -> PolicyResponse:
        
        user_query: str = input.get("user_query", "")

        
        if user_query is None or user_query.strip() == "":
            raise ValueError("user_query cannot be empty.")

        #policy agent doesn't need session id from outside, generate a new one
        #this is to ensure each invocation is stateless from outside and save tokens

        if self.agent is None:
            self.agent = await self._get_agent()

        result = await self.agent.ainvoke(
                { 
                "messages": [ HumanMessage(content=user_query) ],
                },
                
            )

        response = "__No AI Message__"
        messages = result["messages"]
        response = messages[-1].content

        sum_input_tokens = 0
        sum_output_tokens = 0
        sum_total_tokens = 0
        
        doc_ids = []
        for msg in messages:
            if isinstance(msg, ToolMessage) and msg.name == "search_knowledge_base":
                content = msg.content
                jsonobj = json.loads(content)                        
                doc_ids = jsonobj["doc_ids"] if "doc_ids" in content else []
            if isinstance(msg, AIMessage):
                metadata = msg.usage_metadata
                if metadata:
                    sum_input_tokens += metadata.get("input_tokens") or 0
                    sum_output_tokens += metadata.get("output_tokens") or 0
                    sum_total_tokens += metadata.get("total_tokens") or 0
                
        return PolicyResponse(
            message=response,
            sources=doc_ids,
            needs_escalation=False,
            agent_name=f"policy_agent",
            model=self.deployment_name,
            metadata= Metadata(
                input_token=sum_input_tokens,
                output_token=sum_output_tokens,
                total_token=sum_total_tokens
            )
        )

    def get_agent(self):
        return self.agent

    async def get_history(self, session_id: str) -> list[dict]:
        """Retrieve the message history for a given session ID."""
        if self.agent is None:
            self.agent = await self._get_agent()
        return await AgentTools.get_history(self.agent, session_id)
    
#endregion

#region Helper functions for testing

def get_message_history_from_checkpoints(session_Id: str):

    messages = []
    config:RunnableConfig = {
        "configurable": {
        "thread_id": session_Id,
        }
        }   

    with RedisSaver.from_conn_string(settings.redis_url) as checkpointer:
        checkpointer.setup()            
        checkpoints = checkpointer.list (
            config= config
        )

        print(f"Retrieved checkpoints for session_Id: {session_Id}")
        # Extract messages
        
        last:CheckpointTuple = None #deque(checkpoints, maxlen=4)
    
        try:
            last = next(checkpoints)
        except StopIteration :
            print("No more checkpoints.")
        except Exception as e:
            print(f"Error retrieving checkpoints: {e}")
            
        if not last:
            print("No checkpoints found.")
            return messages
        else:
            checkpoint = last.checkpoint
            messages = checkpoint.get("channel_values").get("messages", [])
            print(f"Returning {len(messages)} messages from history.")
            print("Messages:")
            for msg in messages:
                print(f"- {msg}")
    
    return messages

def invoke_policy_agent_test(user_query: str):

    credential_manager = get_credential_manager()
    token_provider = credential_manager.get_openai_token_provider()

    llm = AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        deployment_name=settings.azure_openai_model_deployment,
        azure_ad_token_provider=token_provider,
        temperature=0.3
    )
    
    agent = create_agent (
                model=llm,
                tools=[search_knowledge_base],
                # for testing purposes use in-memory checkpointer. trim_message_history for in-memory only
                checkpointer=InMemorySaver(), 
                middleware=[trim_message_history],
                system_prompt= PolicyTemplates.SYSTEM_PROMPT,
                state_schema=PolicyAgentState,
            )

    result = agent.invoke(
            { 
            "messages": [ HumanMessage(content=user_query)],
            },
            {"configurable": {"thread_id": "1"}},
        )
    
    print(result)

    messages = result["messages"]
    response = ""

    if not messages:
        return response
    
    msg = messages[-1]
    if isinstance(msg, AIMessage) and msg.content:
        print("Final Response Content:", msg.content)
        response = msg.content

    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    if tool_messages:
        print("Tool Messages:")
        for tm in tool_messages:
            print(f"- Tool Message Content: {tm.content}")
            content = tm.content
            #print type of content
            print(f"  Content Type: {type(content)}")
            jsonobj = json.loads(content)                        
            doc_ids = jsonobj["doc_ids"] if "doc_ids" in content else []
            print(f"  Associated Document IDs: {doc_ids}")

    print("Asking follow-up question...")
    time.sleep(3)  # Simulate some delay before follow-up question
    question = "what about shipping policy?"
    print(f"\nAsking follow-up question: {question}")
    result2 = agent.invoke(
            { 
            "messages": [ HumanMessage(content=question) ],
            },
            {"configurable": {"thread_id": "1"}}
        )
    
    print("========================")
    print(result2)
    print("========================")
    messages = result2["messages"]
    response = ""

    if not messages:
        return response
    
    msg = messages[-1]
    if isinstance(msg, AIMessage) and msg.content:
        print("Final Response Content:", msg.content)
        response = msg.content

#endregion
