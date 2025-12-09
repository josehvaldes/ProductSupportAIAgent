
from typing import TypedDict, Annotated
import operator
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent.parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.application.settings.config import settings

from langgraph.graph import StateGraph, END
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

# 1. Define state 
class State(TypedDict):
    messages: Annotated[list, operator.add]
    user_query: str
    response: str


# 2. Define Simple node
def policy_node(state: State) -> State:
    
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )

    llm = AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        deployment_name=settings.azure_openai_model_deployment,
        azure_ad_token_provider=token_provider,
        temperature=0.3
    )
    response = llm.invoke(f"Answer this question: {state['user_query']}")
    state["response"] = response.content
    return state

# 3. Build the graph
workflow = StateGraph(State)
workflow.add_node("policy", policy_node)
workflow.set_entry_point("policy")
workflow.add_edge("policy", END)

app = workflow.compile()

# 4. Test it
if __name__ == "__main__":
    result = app.invoke({
        "messages": [],
        "user_query": "Who are you?",
        "response": ""
    })
    print("Response:", result["response"])