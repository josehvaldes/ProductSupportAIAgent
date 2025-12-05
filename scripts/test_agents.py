import traceback
from typing import Any
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
from shopassist_api.application.agents.product_detail_agent import ProductDetailAgent
from shopassist_api.application.agents.product_search_agent import ProductSearchAgent
from shopassist_api.application.agents.product_comparison_agent import ProductComparisonAgent
from shopassist_api.application.agents.policy_agent import PolicyAgent
from shopassist_api.application.agents.supervisor_agent import SupervisorAgent
from shopassist_api.application.agents.query_expansion_agent import QueryExpansionAgent
from shopassist_api.application.agents.product_search_expanded_agent import ProductSearchExpandedAgent
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

async def test_supervisor_agent():
    
    print("Testing Supervisor Agent")
    supervisor = SupervisorAgent( model_deployment=settings.azure_openai_nano_model_deployment ) # azure_openai_model_deployment
    test_queries = [
        # {
        #     "query": "Can I return a product after 30 days?",
        #     "expected": "policy"
        # },
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
        # {
        #     "query": "which one has HDMI connector?",
        #     "expected": "product_detail"
        # },
        {
            "query": "I live in the same town as the main store, in how many days can I receive the tv?",
            "expected": "policy"
        },
    ]
    for item in test_queries:
        query = item["query"]
        excepted_agent = item["expected"]
        print(f"\nUser Query: {query}")
        try:
            decision = await supervisor.route(user_query=query)
            print(f"Match={(excepted_agent==decision.agent)}, Routing Decision: Agent={decision.agent}, Confidence={decision.confidence}, Reasoning={decision.reasoning}")
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

async def test_history_agent(session_id:str, agent:PolicyAgent|ProductSearchAgent|ProductDetailAgent):
    #agent = ProductSearchAgent()
    history = await agent.get_history(session_id=session_id)
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

async def test_product_detail_agent():
    print("Testing Product Detail Agent")
    product_detail_agent = ProductDetailAgent()
    test_queries = [
        "What are the specifications of the Canon PIXMA E477?",
    ]
    session_id = uuid.uuid4().hex[:12]
    for query in test_queries:
        print(f"\nUser Query: {query}")
        try:
            response = await product_detail_agent.ainvoke({
                "user_query": query,                
                "session_Id": session_id
            })
            print(f"Agent Response: {response.message}...") 
            print(f"Product Details: {response.sources}")
            #print metadata
            if response.metadata:
                print(f"Metadata:\n  Input Tokens={response.metadata.input_token},\n  Output Tokens={response.metadata.output_token},\n  Total Tokens={response.metadata.total_token}")

        except Exception as e:
            logger.error(f"Error invoking product detail agent: {e}")
            traceback.print_exc()


async def test_product_comparison_agent():
    print("Testing Product Comparison Agent")
    product_comparison_agent = ProductComparisonAgent()
    test_queries = [
        #OnePlus 10R5G vs Samsung Galaxy M13 5G
        "Compare the features of the Samsung Galaxy M13 and OnePlus 10R. Which is better for photography",
    ]
    session_id = uuid.uuid4().hex[:12]
    for query in test_queries:
        print(f"\nUser Query: {query}")
        try:
            response = await product_comparison_agent.ainvoke({
                "user_query": query,                
                "session_Id": session_id
            })
            print(f"Agent Response: {response.message}...") 
            print(f"Comparison Details: {response.sources}")
            #print metadata
            if response.metadata:
                print(f"Metadata:\n  Input Tokens={response.metadata.input_token},\n  Output Tokens={response.metadata.output_token},\n  Total Tokens={response.metadata.total_token}")

        except Exception as e:
            logger.error(f"Error invoking product comparison agent: {e}")
            traceback.print_exc()

async def test_query_expansion_agent():
    
    print("Testing Query Expansion Agent")
    query_expansion_agent = QueryExpansionAgent()
    test_queries = [
        #"laptop with 16GB RAM and 512GB SSD",
        #"I need a case for my Samsung z flip. Do you have any? what is the warranty of those products?",
        #"I need a case for my Samsung z flip. Do you have any?",
        #"looking for a smartphone with good camera and battery life under $600",
        "do you have any good looking smartphone with good camera and battery life under $600?",
    ]
    for query in test_queries:
        print(f"\nUser Query: {query}")
        try:
            response = await query_expansion_agent.ainvoke(
                {
                    "user_query": query,
                    "context": { "num_variations":2}
                }
               )
            print("Agent Response:")
            print(f"Original Query: {response["original_query"]}")
            print(f"Expanded Queries: {response["expanded_queries"]}") 
            print(f"Categories: {response["categories"]}") 
            if response.get("metadata"):
                metadata = response["metadata"]
                print(f"Metadata:\n  Input Tokens={metadata.input_token},\n  Output Tokens={metadata.output_token},\n  Total Tokens={metadata.total_token}")

        except Exception as e:
            logger.error(f"Error invoking query expansion agent: {e}")
            traceback.print_exc()

async def test_product_search_expanded_agent():
    print("Testing Product Search Expanded Agent")
    product_search_expanded_agent = ProductSearchExpandedAgent()
    test_queries = [
        {
            "query": "Please, show me some smartphones with good cameras under $700.",
            #expanded queries and categories expected as generated by the query expansion agent
            "expanded_queries": ['smartphone with high-quality camera and long-lasting battery under $600', 
                                 'mobile phone with excellent camera and battery performance below $600'],
            "categories": ["Smartphones"]
        }
        
    ]
    session_id = uuid.uuid4().hex[:12]
    for item in test_queries:
        query = item["query"]
        expanded_queries = item["expanded_queries"]
        categories = item["categories"]
        print(f"\nUser Query: {query}")
        try:
            response = await product_search_expanded_agent.ainvoke({
                "user_query": query,                
                "session_Id": session_id,
                "expanded_queries": expanded_queries,
                "categories": categories
            })
            print(f"Agent Response: {response.message}[end]") 
            print(f"Products Found: {response.sources}")
            #print metadata
            if response.metadata:
                print(f"Metadata:\n  Input Tokens={response.metadata.input_token},\n  Output Tokens={response.metadata.output_token},\n  Total Tokens={response.metadata.total_token}")

        except Exception as e:
            logger.error(f"Error invoking product search expanded agent: {e}")
            traceback.print_exc()

async def main(arg:str):
    if arg == "supervisor":
        await test_supervisor_agent()
    elif arg == "query_expansion":
        await test_query_expansion_agent()
    elif arg == "product_search_expanded":
        await test_product_search_expanded_agent()
    elif arg == "policy":
        await test_policy_agent()
    elif arg == "policy_history":
        session_id = "71d191aee33e" # "245c93fe0679"
        await test_history_agent(session_id, PolicyAgent())
    elif arg == "product":
        await test_product_search_agent()
    elif arg == "product_history":
        session_id = "ad8370c90393" #"3404bdb0b7de"
        await test_history_agent(session_id, ProductSearchAgent())
    elif arg == "escalation":
        await test_escalation_agent()
    elif arg == "product_detail":
        await test_product_detail_agent()
    elif arg == "product_detail_history":
        session_id = "9c02a9c07ada"
        await test_history_agent(session_id, ProductDetailAgent())
    elif arg == "product_comparison":
        await test_product_comparison_agent()
    elif arg == "product_comparison_history":
        session_id = ""
        await test_history_agent(session_id, ProductComparisonAgent())
    else:
        print("Unknown agent type. Use 'policy' or 'supervisor' or 'product' or 'product_comparison'.")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Test Agent ")
    parser.add_argument("agent", type=str, help="Agent to test: 'policy' or 'supervisor', or 'product'")
    args = parser.parse_args()
    
    asyncio.run(main(args.agent))