
from typing import Any, TypeAlias
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.redis import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langchain.agents.middleware import AgentState


CompiledAgent: TypeAlias = CompiledStateGraph[AgentState, Any, Any, Any]

class AgentTools:

    @staticmethod
    def get_agent_tool_names() -> list[str]:
        return [
            "policy_agent",
            "supervisor_agent",
            "product_search_agent",
            "product_detail_agent",
            "product_comparison_agent",
        ]
    

    @staticmethod
    async def get_history(agent:CompiledAgent, session_id:str) -> list[dict]:
        """Retrieve the message history for a given session ID."""
        
        config:RunnableConfig = {
            "configurable": {
            "thread_id": session_id,
            }
        }

        state = await agent.aget_state(config)         
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