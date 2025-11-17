#v2-architecture.md LangGraph for RAG Orchestration

## Lessons from V1
- What worked well
- Pain points encountered
- Performance bottlenecks
- Code smells to fix

## V2 Goals
- Production-ready observability
- 10x better retrieval accuracy
- Multi-agent architecture


## Tech Stack Changes
- Add: LangGraph, LangSmith, 
- Replace: Custom RAG → LangGraph chains


## Migration Path
- Phase 1: Add observability (LangSmith)
- Phase 2: Migrate to LangGraph
- Phase 3: Multi-agent system (Custom agents for specialized tasks)

#Advanced Testing Framework

RAGAs for automated evaluation
Synthetic test data generation