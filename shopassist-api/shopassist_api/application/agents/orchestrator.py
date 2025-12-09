import json
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from typing import Annotated, Optional, TypedDict

from langchain.messages import AnyMessage
import operator

from langsmith import traceable
from shopassist_api.application.agents.base import Metadata
from shopassist_api.application.agents.escalation_agent import EscalationAgent
from shopassist_api.application.agents.policy_agent import PolicyAgent
from shopassist_api.application.agents.product_comparison_agent import ProductComparisonAgent
from shopassist_api.application.agents.product_detail_agent import ProductDetailAgent
from shopassist_api.application.agents.product_discovery_agent import ProductDiscoveryAgent

from shopassist_api.application.agents.supervisor_agent import SupervisorAgent

from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)

class OrchestratorState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    session_Id: str
    current_agent: str

    route_request: Optional[any]
    current_route_index: int
    next_action: str
    response: Optional[str]
    route_responses: list[str]
    response_sources: list[list[dict]]
    
    metadatas: list[Metadata]


class AgentOrchestrator:
    
    def __init__(self):
        
        self.supervisor = SupervisorAgent()
        self.policy_agent = PolicyAgent()

        self.product_discovery_agent = ProductDiscoveryAgent()
        self.product_detail_agent = ProductDetailAgent()
        self.product_comparison_agent = ProductComparisonAgent()
        self.escalation_agent = EscalationAgent()

        self.graph = self._build_graph()

    def _build_graph(self)-> CompiledStateGraph:
        workflow  = StateGraph(OrchestratorState)
        # Define states and transitions here
        
        #nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("router", self._router_node)

        workflow.add_node("policy", self._policy_node)
        workflow.add_node("product_search", self._product_search_node)
        workflow.add_node("product_detail", self._product_detail_node)
        workflow.add_node("product_comparison", self._product_comparison_node)
        workflow.add_node("escalation", self._escalation_node)
        workflow.add_node("aggregate_responses", self.aggregate_responses)

        #entry point
        workflow.set_entry_point("supervisor")

        #transitions
        workflow.add_conditional_edges(
            "router",
            self.route_to_next,
            {
                "policy": "policy",
                "product_search": "product_search",
                "product_detail": "product_detail",
                "comparison":"product_comparison",
                "escalation": "escalation",
                "aggregate_responses": "aggregate_responses",
                "END": END
            }
        )

        workflow.add_edge("supervisor", "router")

        workflow.add_edge("policy", "router")
        workflow.add_edge("product_search", "router")
        workflow.add_edge("product_detail", "router")
        workflow.add_edge("product_comparison", "router")
        workflow.add_edge("escalation", "router")

        workflow.add_edge("aggregate_responses", END)

        return workflow.compile()

    
    def map_intent_to_agent(self, intent: str) -> str:
        """Map intent to agent node name"""
        mapping = {
            "product_search": "product_search",
            "product_detail": "product_detail",
            "comparison": "product_comparison",
            "policy": "policy",
            "escalation": "escalation"
        }
        return mapping.get(intent, "product_search")

    async def _supervisor_node(self, state: OrchestratorState):
        """Route the query"""
        logger.info("Orchestrator invoking SupervisorAgent for routing. User Query: %s, Session: %s", state["user_query"], state["session_Id"]) 
        route_request = await self.supervisor.route(
            user_query=state["user_query"],
            context={"messages": state["messages"]}
        )
        logger.info(f"Orchestrator routed to agent: {route_request}")
        
        state["route_request"] = route_request
        state["current_route_index"] = 0
        state["route_responses"] = []

        first_route = route_request.routes[0] if route_request.routes else None
        state["next_action"] = self.map_intent_to_agent(first_route.intent)

        return state

    async def _router_node(self, state: OrchestratorState):
        logger.info("Orchestrator at router node. Current route index: %d. Next action %s", state["current_route_index"], state["next_action"])

        return state

    def route_to_next(self, state: OrchestratorState) -> str:
        """
        Conditional edge function to route to next agent or finish
        """
        
        route_request = state["route_request"]
        current_idx = state["current_route_index"]
        # Check if we've processed all routes
        if current_idx >= len(route_request.routes):
            # All routes complete - aggregate if multiple
            if len(route_request.routes) > 1:
                return "aggregate_responses"
            else:
                return "END"
        
        # Route to next agent
        current_route = route_request.routes[current_idx]
        logger.info("Orchestrator routing to next agent based on intent: %s", current_route.intent)
        return self.map_intent_to_agent(current_route.intent)

    def _get_current_user_query(self, state: OrchestratorState) -> str:
        """Get the current user query based on route index"""
        route_request = state["route_request"]
        current_idx = state["current_route_index"]
        current_route = route_request.routes[current_idx]
        return current_route.query

    async def _policy_node(self, state: OrchestratorState):
        """Execute policy agent"""

        state["user_query"] = self._get_current_user_query(state)

        logger.info("Orchestrator invoking PolicyAgent. User Query: %s , Session: %s, RouteIndex: %d", state["user_query"], state["session_Id"], state["current_route_index"])

        result = await self.policy_agent.ainvoke(input={
            "user_query": state["user_query"],
            "session_Id": state["session_Id"]
        })
        state["response"] = result.message
        state["route_responses"].append(result.message)
        
        # Move to next route
        state["current_route_index"] += 1

        metadatalist = state.get("metadatas", [])
        if result.metadata:
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist
        
        logger.info("PolicyAgent completed. Updated state current_route_index to %d", state["current_route_index"])
        return state
    

    async def _product_search_node(self, state: OrchestratorState):
        """Execute product discovery agent"""

        state["user_query"] = self._get_current_user_query(state)

        logger.info("Orchestrator invoking ProductSearchAgent. User Query: %s, Session: %s ", state["user_query"], state["session_Id"])
        result = await self.product_discovery_agent.ainvoke(state=state)

        state["response"] = result.message
        state["route_responses"].append(result.message)
        state["response_sources"].append(result.sources)
        
        # Move to next route
        state["current_route_index"] += 1


        metadatalist = state.get("metadatas", [])
        if result.metadata:
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist
        return state

    async def _product_detail_node(self, state: OrchestratorState):
        """Execute product detail agent"""
        
        state["user_query"] = self._get_current_user_query(state)

        logger.info("Orchestrator invoking ProductDetailAgent. User Query: %s, Session: %s ", state["user_query"], state["session_Id"])
        result = await self.product_detail_agent.ainvoke(state=state)

        state["response"] = result.message
        state["route_responses"].append(result.message)
        state["response_sources"].append(result.sources)
        
        # Move to next route
        state["current_route_index"] += 1

        metadatalist = state.get("metadatas", [])
        if result.metadata:
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist
        return state
    
    async def _product_comparison_node(self, state: OrchestratorState):
        """Execute product comparison agent"""
        
        state["user_query"] = self._get_current_user_query(state)
        logger.info("Orchestrator invoking ProductComparisonAgent. User Query: %s, Session: %s ", state["user_query"], state["session_Id"])
        result = await self.product_comparison_agent.ainvoke(state=state)

        state["response"] = result.message
        state["route_responses"].append(result.message)
        state["response_sources"].append(result.sources)
        
        # Move to next route
        state["current_route_index"] += 1

        metadatalist = state.get("metadatas", [])
        if result.metadata:
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist
        return state

    async def _escalation_node(self, state: OrchestratorState):
        """Execute escalation agent"""
        state["user_query"] = self._get_current_user_query(state)
        logger.info("Orchestrator invoking EscalationAgent. User Query: %s, Session: %s ", state["user_query"], state["session_Id"])
        result = await self.escalation_agent.ainvoke(state=state)

        state["response"] = result.message
        state["route_responses"].append(result.message)
        
        # Move to next route
        state["current_route_index"] += 1

        metadatalist = state.get("metadatas", [])        
        if result.metadata:
            result.metadata.id = "escalation_agent"
            metadatalist.append(result.metadata)
            state["metadatas"] = metadatalist

        return state    

    
    async def aggregate_responses(self, state: OrchestratorState) -> OrchestratorState:
        """
        Combine responses from multiple routes into coherent answer
        """
        logger.info("Orchestrator aggregating responses from multiple agents.")
        combined_response = "\n\n".join(state["route_responses"])
        state["response"] = combined_response
        state["next_action"] = "END"
        
        return state

    def _route_to_agent(self, state: OrchestratorState) -> str:
        """Determine which agent to execute"""
        logger.info("Orchestrator routing to agent: %s", state["current_agent"])
        return state["current_agent"]
    

    @traceable(name="orchestrator.ainvoke", tags=["orchestration","entry-point"], metadata={"version": "2.0"})
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
            "route_request": None,
            "current_route_index": 0,
            "next_action": "",
            "route_responses": [],
            "response_sources": [],
            "response": "",

            "metadatas": []
        }

        logger.info("Orchestrator starting execution for session_Id: %s and user_query %s", session_Id, user_query)
        result = await self.graph.ainvoke(initial_state)
        return result