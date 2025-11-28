#DEVLOG v2

### Phase 1: Add Observability (Week 1)
**Goal**: Get visibility into current system

## Week 1 Add Observability



## Day 0 Setup LangSmith
- [X] Install LangSmith and instrument V1 code
- [X] Add basi POC tests and check correct functionality

## Day 1  Instrument V1 Code with Custom Tracing
- [X] List all critical functions to trace:
- [X] Add @traceable Decorators to Core Functions (2 hours)
- [X] Add Custom Metadata (1 hour)
- [X] Test Instrumentation (1 hour)
- [X] Create Custom Metrics Dashboard (1.5 hours)
- [X] Document Baseline Performance (1 hour)
- [X] Identify top 3 bottlenecks
- [X] Measure baseline metrics (latency, accuracy)


#v1_retrieval_issues.md 

# V1 Known Retrieval Issues

============================================================
BASELINE METRICS REPORT (1 day(s))
============================================================

rag.generate_answer:
  Total Runs: 11
  Success Rate: 100.0%
  Latency (ms):
    p50: 8077.4
    p95: 26244.9
    p99: 31744.1
    avg: 9183.4

## Problem: Irrelevant Products in Results

### Example Queries:
1. Query: "Compare the MacBook Air M2 and Dell XPS 15"
   - Retrieved: categories recovered didn't match. Then the products recovered didn't make same (incorrect)
   - Likely cause: Category classification mismatch

2. Query: "Does the MacBook Air M2 have 16GB RAM   "
   - Retrieved: categories recovered didn't match. Then the products recovered didn't make same (incorrect)
   - Likely cause: Category classification mismatch


### Root Causes:
- e5-large-v2 category classification (768 dims) less accurate
- Milvus search params need tuning (ef, nprobe)
- No query expansion (missing synonyms)

### Will Fix in Phase 2:
- MultiQueryRetriever (query expansion)
- Better category embeddings
- Hybrid search with Azure AI Search
EOF

# 3. Mark Week 1 complete


### Phase 2: Migrate to LangGraph (Weeks 2)

**Goal**: Replace custom orchestration with LangGraph

## Week 2 LangGraph flows

- [X] Start with simplest flow (policy questions)
- [X] Create single-agent LangGraph workflow
- [X] Test parity with V1 responses
- [X] Gradually migrate other intents
- [X] Keep V1 as fallback during migration
- [X] Implement supervisor agent
- [X] Create Policy specialized agent
- [X] Create Product Search specialized agent
- [X] Create Dumb Scalation specialized agent
- [X] Add conditional routing

**Technical Decisions:**
- Implement LangSmith as a AI logger.
- Don't fix or improve V1 code. They will be addressed in V2 testing
- Implement 2 basic specialized agents: Product Search and Policy Agent
- Use Custom Logic agent and "create_agent" based agent depending on its purposes
- Reuse V1 code for Retrieval without updating the V1 Rag implementation
- Use Async Redis cache with AsyncRedisSaver for long-term memory
- Use Monolithic tool approach for search_products and let multi tools for Enhancements
- Remove price filtering pattern and delegate that reasoning to the LLM following ReAct patterns
- Add a new single /chat/orchestrate endpoint for V2 

**Challenges & Solutions:**
- Langchain V1 release deprecated many samples and tutorials. Documentation and AI assistants are outdated yet
- Implement Async long term memory for all the agents.

**Learnings:**
- The langsmith, Langchain and LangGraph implementation
- Multi-agent implement with Lang graphs
- Long-term memory with Redis and LangGraph
- Agent Tooling with langgrapg vs Azure AI Projects
- 

**Next Steps:**
- Test complex multi-turn scenarios
- Add LangSmith tracing in V2 agents
- Compare V2 and V1 time response and token costs
- 

**Time Invested:** 26 hours

**Deliverable**: All V1 functionality working in LangGraph


## Week 3: Testing and documentation


## Week 4: Enhancements
Interactive Refinement


tools = [
    search_products_tool,
    apply_additional_filters_tool,  # NEW: Refine existing results
    get_alternatives_tool           # NEW: "Show me cheaper options"
]
```

**Example flow:**
```
User: "Show me laptops"
→ search_products() → 20 results

User: "Only under $1000"
→ apply_additional_filters(price_max=1000) → 8 results

User: "Show cheaper alternatives"
→ get_alternatives(price_range="lower") → 5 budget options