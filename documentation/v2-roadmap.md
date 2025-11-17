#v2-roadmap.md

# ShopAssist V2 - Advanced RAG Architecture

## Option A: Azure AI Projects + AI Search
- Use AIProjectClient for orchestration
- Azure AI Search for hybrid retrieval
- Function calling for tool use
- Multi-agent patterns

## Option B: LangGraph + LangChain
- LangGraph for workflow orchestration
- LangChain for RAG chains
- Custom agents for specialized tasks
- Better observability with LangSmith

## Option C: Milvus + Neoj4 graph database
- Review Neo4j capabilities and feasibility
- create a POC for RAG retrieval and Neo4j refinement and extension

## Comparison Matrix
| Feature | Azure AI | LangGraph |
|---------|----------|-----------|
| Cost | Higher | Lower |
| Lock-in | Azure | Flexible |
| Maturity | Preview | Production |
| Portfolio | Azure-focused | ML Engineering |

## Recommended: Start with LangGraph, migrate to Azure AI Projects when GA