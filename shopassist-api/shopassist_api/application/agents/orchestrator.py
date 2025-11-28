import json
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from typing import Annotated, TypedDict

from langchain.messages import AnyMessage
import operator

from shopassist_api.application.agents.base import Metadata
from shopassist_api.application.agents.escalation_agent import EscalationAgent
from shopassist_api.application.agents.policy_agent import PolicyAgent
from shopassist_api.application.agents.product_comparison_agent import ProductComparisonAgent
from shopassist_api.application.agents.product_detail_agent import ProductDetailAgent
from shopassist_api.application.agents.product_search_agent import ProductSearchAgent
from shopassist_api.application.agents.supervisor_agent import SupervisorAgent

from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

class OrchestratorState(TypedDict):
    messages: list
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    session_Id: str
    current_agent: str
    response: str
    sources: list
    metadatas: list[Metadata]


class AgentOrchestrator:
    
    def __init__(self):
        
        self.supervisor = SupervisorAgent()
        self.policy_agent = PolicyAgent()
        self.product_search_agent = ProductSearchAgent()
        self.product_detail_agent = ProductDetailAgent()
        self.product_comparison_agent = ProductComparisonAgent()
        self.escalation_agent = EscalationAgent()

        self.graph = self._build_graph()

    def _build_graph(self)-> CompiledStateGraph:
        workflow  = StateGraph(OrchestratorState)
        # Define states and transitions here
        
        #nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("policy", self._policy_node)
        workflow.add_node("product_search", self._product_search_node)
        workflow.add_node("product_detail", self._product_detail_node)
        workflow.add_node("product_comparison", self._product_comparison_node)
        workflow.add_node("escalation", self._escalation_node)

        #entry point
        workflow.set_entry_point("supervisor")

        #transitions
        workflow.add_conditional_edges(
            "supervisor",
            self._route_to_agent,
            {
                "policy": "policy",
                "product_search": "product_search",
                "product_detail": "product_detail",
                "comparison":"product_comparison",
                "escalation": "escalation",
                "END": END
            }
        )

        workflow.add_edge("policy", END)
        workflow.add_edge("product_search", END)
        workflow.add_edge("product_detail", END)
        workflow.add_edge("product_comparison", END)
        workflow.add_edge("escalation", END)

        return workflow.compile()

    async def _supervisor_node(self, state: OrchestratorState):
        """Route the query"""
        logger.info("Orchestrator invoking SupervisorAgent for routing. User Query: %s, Session: %s", state["user_query"], state["session_Id"]) 
        decision = await self.supervisor.route(
            user_query=state["user_query"],
            context={"messages": state["messages"]}
        )
        state["current_agent"] = decision.agent
        logger.info("Orchestrator routed to agent: %s", decision.agent)
        return state

    async def _policy_node(self, state: OrchestratorState):
        """Execute policy agent"""
        logger.info("Orchestrator invoking PolicyAgent. User Query: %s , Session: %s", state["user_query"], state["session_Id"])
        result = await self.policy_agent.ainvoke(input={
            "user_query": state["user_query"],
            "session_Id": state["session_Id"]
        })
        state["response"] = result.message
        state["sources"] = result.sources
        metadatalist = state.get("metadatas", [])
        if result.metadata:
            result.metadata.id = "policy_agent"
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist
        return state
    
    async def _product_search_node(self, state: OrchestratorState):
        """Execute product discovery agent"""
        logger.info("Orchestrator invoking ProductSearchAgent. User Query: %s, Session: %s ", state["user_query"], state["session_Id"])
        result = await self.product_search_agent.ainvoke(state=state)
        state["response"] = result.message
        state["sources"] = result.sources
        metadatalist = state.get("metadatas", [])
        if result.metadata:
            result.metadata.id = "product_search_agent"
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist
        return state

    async def _product_detail_node(self, state: OrchestratorState):
        """Execute product detail agent"""
        
        logger.info("Orchestrator invoking ProductDetailAgent. User Query: %s, Session: %s ", state["user_query"], state["session_Id"])
        result = await self.product_detail_agent.ainvoke(state=state)
        state["response"] = result.message
        state["sources"] = result.sources
        metadatalist = state.get("metadatas", [])
        if result.metadata:
            result.metadata.id = "product_detail_agent"
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist
        return state
    
    async def _product_comparison_node(self, state: OrchestratorState):
        """Execute product comparison agent"""
        
        logger.info("Orchestrator invoking ProductComparisonAgent. User Query: %s, Session: %s ", state["user_query"], state["session_Id"])
        result = await self.product_comparison_agent.ainvoke(state=state)
        state["response"] = result.message
        state["sources"] = result.sources
        metadatalist = state.get("metadatas", [])
        if result.metadata:
            result.metadata.id = "product_comparison_agent"
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist
        return state

    async def _escalation_node(self, state: OrchestratorState):
        """Execute escalation agent"""
        logger.info("Orchestrator invoking EscalationAgent. User Query: %s, Session: %s ", state["user_query"], state["session_Id"])
        result = await self.escalation_agent.ainvoke(state=state)
        print("EscalationAgent result:", result)
        state["response"] = result.message

        metadatalist = state.get("metadatas", [])        
        if result.metadata:
            result.metadata.id = "escalation_agent"
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist

        return state    

    def _route_to_agent(self, state: OrchestratorState) -> str:
        """Determine which agent to execute"""
        logger.info("Orchestrator routing to agent: %s", state["current_agent"])
        return state["current_agent"]
    

    async def ainvoke(self, input: dict):
        """Orchestrate the agents based on user query
        input: dict
            user_query: str
            session_Id: str
        """
        user_query: str = input.get("user_query", "")
        session_Id: str = input.get("session_Id", "")
        
        if not user_query or not session_Id:
            raise ValueError("user_query and session_Id are required inputs")

        """Main entry point"""
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "session_Id": session_Id,
            "current_agent": "",
            "response": "",
            "sources": [],
            "metadatas": []
        }

        logger.info("Orchestrator starting execution for session_Id: %s and user_query %s", session_Id, user_query)
        result = await self.graph.ainvoke(initial_state)
        return result