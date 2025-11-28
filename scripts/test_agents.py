import traceback
import uuid
import sys
import argparse
import asyncio
import sys

from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.application.agents.base import Metadata
from shopassist_api.application.agents.escalation_agent import EscalationAgent
from shopassist_api.application.settings.config import settings

from shopassist_api.application.agents.product_search_agent import ProductSearchAgent
from shopassist_api.application.agents.policy_agent import PolicyAgent
from shopassist_api.application.agents.supervisor_agent import SupervisorAgent
from shopassist_api.logging_config import setup_logging
from shopassist_api.logging_config import get_logger

setup_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        log_to_console=settings.log_to_console
    )

logger = get_logger(__name__)


async def test_policy_agent():
    
    session_Id = uuid.uuid4().hex[:12]

    test_queries = [
        #"What is your return policy for electronics?",
        "how long does shipping take for orders over $50?",
    ]
    print(" * Testing Policy Agent: %s",session_Id)
    policy_agent = PolicyAgent()
    
    for query in test_queries:
        print(f"\nUser Query: {query}")
        try:
            response = await policy_agent.ainvoke({
                "user_query": query,
                "session_Id": session_Id
            })
            print(f"Agent Response: {response.message[0:400]}...")  # Print first 400 chars of response
            print(f"Sources: {response.sources}")

            if response.metadata:
                metadata:Metadata = response.metadata
                print(f"Metadata:\n  Input Tokens={metadata.input_token},\n  Output Tokens={metadata.output_token},\n  Total Tokens={metadata.total_token}")

        except Exception as e:
            logger.error(f"Error invoking policy agent: {e}")
            traceback.print_exc()
    return session_Id

async def test_history_agent(session_id:str):
    policy_agent = PolicyAgent()
    history = await policy_agent.get_history(session_id=session_id)
    print(f"history for {session_id}:")
    for entry in history:
        print(f"{entry.get('role',"").upper()}: {entry.get('content')[0:300]}...\n")
        print(f"Metadata: {entry.get('metadata')}\n")

async def test_supervisor_agent():
    
    print("Testing Supervisor Agent")
    supervisor = SupervisorAgent()
    test_queries = [
        {
            "query": "Can I return a product after 30 days?",
            "expected": "policy"
        },
        # {
        #     "query": "Help me find a smartphone with a good camera for less than $600",
        #     "expected": "product_search"
        # },
        # {
        #     "query": "What are the specs of the latest iPad?",
        #     "expected": "product_detail"
        # },
        # {
        #     "query": "Compare the Samsung Galaxy S21 and iPhone 12.",
        #     "expected": "comparison"
        # },
        # {
        #     "query": "I have an issue with my recent order #12345.",
        #     "expected": "escalation"
        # },
    ]
    for item in test_queries:
        query = item["query"]
        excepted_agent = item["expected"]
        print(f"\nUser Query: {query}")
        try:
            decision = await supervisor.route(user_query=query)
            print(f"Routing Decision: Agent={decision.agent}, Confidence={decision.confidence}, match={(excepted_agent==decision.agent)} Reasoning={decision.reasoning}")
            if decision.metadata:
                metadata:Metadata = decision.metadata
                print(f"Metadata:\n  Input Tokens={metadata.input_token},\n  Output Tokens={metadata.output_token},\n  Total Tokens={metadata.total_token}")
            
        except Exception as e:
            logger.error(f"Error invoking supervisor agent: {e}")
            traceback.print_exc()

async def test_product_search_agent():
    print("Testing Product Search Agent")
    product_search_agent = ProductSearchAgent()
    test_queries = [
        #"Find me a laptop with at least 16GB RAM and 512GB SSD.",
        "Show me smartphones with good cameras under $700.",
    ]
    session_id = uuid.uuid4().hex[:12]
    for query in test_queries:
        print(f"\nUser Query: {query}")
        try:
            response = await product_search_agent.ainvoke({
                "user_query": query,                
                "session_Id": session_id
            })
            print(f"Agent Response: {response.message}[end]") 
            print(f"Products Found: {response.sources}")
            #print metadata
            if response.metadata:
                print(f"Metadata:\n  Input Tokens={response.metadata.input_token},\n  Output Tokens={response.metadata.output_token},\n  Total Tokens={response.metadata.total_token}")

        except Exception as e:
            logger.error(f"Error invoking product search agent: {e}")
            traceback.print_exc()
    
    # history = await product_search_agent.get_history(session_id=session_id)
    # print(f"\nProduct Search Agent history for session {session_id}:")
    # for entry in history:
    #     print(f"{entry.get('role',"").upper()}: {entry.get('content')[0:300]}...\n")

async def test_history_product_agent(session_id:str):
    policy_agent = ProductSearchAgent()
    history = await policy_agent.get_history(session_id=session_id)
    print(f"product history for {session_id}:")
    for entry in history:
        print(f"{entry.get('role',"").upper()}: {entry.get('content')[0:300]}...\n")
        print(f"Metadata: {entry.get('metadata')}\n")

async def test_escalation_agent():
    print("Testing Escalation Agent")
    escalation_agent = EscalationAgent()
    test_queries = [
        "I need help with my recent order #98765. The product arrived damaged and I want to file a complaint.",
    ]
    session_id = uuid.uuid4().hex[:12]
    for query in test_queries:
        print(f"\nUser Query: {query}")
        try:
            response = await escalation_agent.ainvoke({
                "user_query": query,                
                "session_Id": session_id
            })
            print(f"Agent Response: {response.message}...") 
            print(f"Ticket ID: {response.ticket_id}, Contact Info: {response.contact_info}")

        except Exception as e:
            logger.error(f"Error invoking escalation agent: {e}")
            traceback.print_exc()

async def main(arg:str):
    if arg == "supervisor":
        await test_supervisor_agent()        
    elif arg == "policy":
        await test_policy_agent()
    elif arg == "policy_history":
        session_id = "71d191aee33e" # "245c93fe0679"
        await test_history_agent(session_id)
    elif arg == "product":
        await test_product_search_agent()
    elif arg == "product_history":
        session_id = "ad8370c90393" #"3404bdb0b7de"
        await test_history_product_agent(session_id)
    elif arg == "escalation":
        await test_escalation_agent()
    else:
        print("Unknown agent type. Use 'policy' or 'supervisor' or 'product'.")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Test Agent ")
    parser.add_argument("agent", type=str, help="Agent to test: 'policy' or 'supervisor', or 'product'")
    args = parser.parse_args()
    
    asyncio.run(main(args.agent))