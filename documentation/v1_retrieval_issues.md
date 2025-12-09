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
