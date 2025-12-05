# Week 4 Revised Plan: Query Expansion First

## Rationale for Reordering

**Excellent decision!** Multi-query retrieval directly addresses the V1 retrieval issues documented in `v1_retrieval_issues.md`:

1. **Category Mismatch Problem**: Query expansion generates variations that may match better
2. **Core Capability**: Product discovery is the foundation - everything else builds on good retrieval
3. **Immediate Impact**: Better initial results = less need for complex refinement tools
4. **Natural Progression**: Fix retrieval → Add refinement → Add compression

---

## Revised Week 4 Schedule

### Day 22 (Monday): Multi-Query Retrieval Foundation
**Priority: CRITICAL** 🔥

#### Morning Session (3-4 hours)
1. **Implement Basic Query Expansion** (2 hours)
   ```python
   async def expand_query_with_llm(
       original_query: str,
       num_variations: int = 3
   ) -> List[str]:
       """Generate query variations focusing on:
       - Synonyms (laptop → notebook, portable computer)
       - Feature emphasis (for video editing → with GPU, high RAM)
       - Brand/category alternatives
       """
       prompt = f"""Generate {num_variations} alternative search queries for:
       "{original_query}"
       
       Focus on:
       1. Using different terminology
       2. Emphasizing different product features
       3. Being more/less specific
       
       Return only queries, one per line."""
   ```

2. **Create Parallel Retrieval Logic** (1.5 hours)
   ```python
   import asyncio
   
   async def parallel_milvus_search(
       queries: List[str],
       top_k: int = 5
   ) -> Dict[str, List[Product]]:
       """Execute all query variations in parallel"""
       tasks = [
           milvus_search(query, top_k=top_k) 
           for query in queries
       ]
       results = await asyncio.gather(*tasks)
       return dict(zip(queries, results))
   ```

#### Afternoon Session (3-4 hours)
3. **Implement Reciprocal Rank Fusion** (2 hours)
   ```python
   def reciprocal_rank_fusion(
       search_results: Dict[str, List[Product]],
       k: int = 60  # RRF constant
   ) -> List[Tuple[Product, float]]:
       """
       Merge results from multiple queries using RRF formula:
       score(product) = sum(1 / (k + rank_in_query_i))
       
       Higher score = appears highly ranked in multiple queries
       """
       product_scores = defaultdict(float)
       
       for query, products in search_results.items():
           for rank, product in enumerate(products, start=1):
               product_scores[product.id] += 1 / (k + rank)
       
       # Sort by score descending
       ranked = sorted(
           product_scores.items(), 
           key=lambda x: x[1], 
           reverse=True
       )
       return ranked[:10]  # Top 10 after fusion
   ```

4. **Add LangSmith Tracing** (1 hour)
   ```python
   from langsmith import traceable
   
   @traceable(name="multi_query_retrieval", tags=["retrieval", "query_expansion"])
   async def multi_query_retrieval(original_query: str):
       # Generate variations
       expanded_queries = await expand_query_with_llm(original_query)
       
       # Log expansions
       langsmith_context.update_current_trace(
           metadata={"expanded_queries": expanded_queries}
       )
       
       # Parallel search
       all_results = await parallel_milvus_search(expanded_queries)
       
       # Fusion
       final_results = reciprocal_rank_fusion(all_results)
       
       langsmith_context.update_current_trace(
           metadata={
               "num_unique_products": len(final_results),
               "fusion_method": "RRF_k60"
           }
       )
       
       return final_results
   ```

**Deliverables Day 22**:
- Query expansion with LLM working
- Parallel retrieval implementation
- RRF-based result merging
- LangSmith tracing integrated

---

### Day 23 (Tuesday): Testing & Optimization
**Priority: HIGH** 🎯

#### Tasks:
1. **Create Test Dataset** (1.5 hours)
   ```python
   # Test queries from v1_retrieval_issues.md
   test_cases = [
       {
           "query": "laptop for video editing",
           "expected_categories": ["Laptops", "Computers"],
           "expected_features": ["GPU", "high RAM", "SSD"]
       },
       {
           "query": "Compare MacBook Air M2 and Dell XPS 15",
           "expected_products": ["MacBook Air M2", "Dell XPS 15"],
           "issue_in_v1": "Category mismatch"
       },
       # Add 15-20 more cases
   ]
   ```

2. **Benchmark Against V1** (2 hours)
   - Run same 20 queries through V1 (single query) and V2 (multi-query)
   - Calculate precision@5 for both
   - Measure latency difference
   - Document improvements

3. **Optimize Query Expansion Prompt** (2 hours)
   - Test different prompt variations
   - Compare quality of generated queries
   - Find optimal number of variations (3 vs 5 vs 7)
   - Tune for your product catalog (electronics-focused)

4. **Handle Edge Cases** (1.5 hours)
   - Very specific queries ("MacBook Air M2 16GB") - maybe skip expansion?
   - Very broad queries ("laptop") - need expansion
   - Implement confidence-based decision logic

**Deliverables Day 23**:
- 20-query test dataset with ground truth
- V1 vs V2 comparison report
- Optimized query expansion prompt
- Edge case handling logic

---

### Day 24 (Wednesday): Integration with Product Search Agent

#### Tasks:
1. **Update Product Search Agent** (2 hours)
   ```python
   # In product_search_agent.py
   
   tools = [
       search_products_tool  # Now uses multi-query internally
   ]
   
   async def search_products_enhanced(
       query: str,
       use_multi_query: bool = True,
       filters: Optional[Dict] = None
   ) -> List[Product]:
       """Enhanced search with query expansion"""
       
       if use_multi_query and should_expand_query(query):
           # Multi-query path
           results = await multi_query_retrieval(query)
       else:
           # Single query path (for specific queries)
           results = await milvus_search(query)
       
       # Apply filters if provided
       if filters:
           results = apply_filters(results, filters)
       
       return results
   ```

2. **Add Adaptive Query Expansion** (2 hours)
   ```python
   def should_expand_query(query: str) -> bool:
       """Decide if query needs expansion"""
       
       # Skip expansion for:
       # - Exact product names: "MacBook Air M2"
       # - Product IDs: "PROD-12345"
       # - Very specific: "laptop with RTX 4090 32GB RAM"
       
       # Use expansion for:
       # - Generic: "laptop for work"
       # - Feature-focused: "laptop for video editing"
       # - Use case: "best laptop for students"
       
       # Use LLM to classify
       classification = llm.invoke(f"Classify query specificity: {query}")
       return classification in ["generic", "feature_focused", "use_case"]
   ```

3. **Test Multi-Turn Conversations** (2 hours)
   - Scenario 1: "Show me laptops" → "For video editing" → "Under $1500"
   - Scenario 2: "Gaming laptop" → "With RTX 4060" → "Show cheaper options"
   - Verify query expansion works with context

4. **Update Supervisor Agent Routing** (1 hour)
   - Ensure product discovery queries get routed correctly
   - Test with expanded query variations

**Deliverables Day 24**:
- Product Search Agent using multi-query retrieval
- Adaptive query expansion logic
- Multi-turn conversation tests passing

---

### Day 25 (Thursday): RAGAs Evaluation

#### Tasks:
1. **Run Full RAGAs Evaluation** (2 hours)
   ```python
   from ragas import evaluate
   from ragas.metrics import context_precision, context_recall
   
   # Test dataset
   test_data = create_test_dataset()  # From Day 23
   
   # Run through V2 system
   results = []
   for test in test_data:
       response = await process_query(test["query"])
       results.append({
           "question": test["query"],
           "contexts": response["retrieved_docs"],
           "answer": response["response"],
           "ground_truth": test["expected_answer"]
       })
   
   # Evaluate
   scores = evaluate(
       Dataset.from_list(results),
       metrics=[context_precision, context_recall]
   )
   ```

2. **Analyze Results** (2 hours)
   - Compare precision@5: V1 vs V2
   - Identify remaining failure cases
   - Document improvements per query type

3. **Generate Synthetic Test Cases** (2 hours)
   ```python
   from ragas.testset import TestsetGenerator
   
   # Generate 50 new test cases from your product catalog
   generator = TestsetGenerator.from_langchain(...)
   testset = generator.generate(test_size=50)
   ```

4. **Create Evaluation Dashboard** (1 hour)
   - Summary metrics (precision, recall, latency)
   - Query type breakdown (generic vs specific)
   - Failure case analysis

**Deliverables Day 25**:
- RAGAs evaluation report
- 50 synthetic test cases
- Evaluation dashboard/notebook

---

### Day 26 (Friday): Contextual Compression

**Now that retrieval is solid, optimize token usage**

#### Tasks:
1. **Implement Compression** (2 hours)
   - Extract only relevant parts from retrieved docs
   - Test with long product descriptions

2. **Measure Impact** (2 hours)
   - Token reduction (target: 40-60%)
   - Quality impact (RAGAs scores)
   - Cost savings estimate

3. **Integrate into Pipeline** (2 hours)
   - Add after multi-query retrieval
   - Before passing to LLM

**Deliverables Day 26**:
- Contextual compression implementation
- Token usage comparison report

---

### Day 27 (Saturday): Multi-Tool Refinement

**Build on solid retrieval foundation**

#### Tasks:
1. **Implement Refinement Tools** (3 hours)
   - `apply_additional_filters_tool`
   - `get_alternatives_tool`

2. **Test Interactive Refinement** (2 hours)
   - "Show laptops" → "Under $1000" → "With 16GB RAM"

3. **Integration Testing** (2 hours)

**Deliverables Day 27**:
- Refinement tools working
- Interactive refinement flows tested

---

### Day 28 (Sunday): Documentation & Wrap-up

#### Tasks:
1. **Update DEVLOG_V2.md** (2 hours)
2. **Create Week 4 Summary Report** (2 hours)
   ```markdown
   # Week 4 Results: Query Expansion Impact
   
   ## Key Achievement: Multi-Query Retrieval
   - Precision@5: 0.72 → 0.87 (+21% improvement)
   - Category mismatch rate: 35% → 8% (-77%)
   - Latency: 800ms → 1200ms (+50%, but acceptable)
   
   ## Query Expansion Examples:
   Original: "laptop for video editing"
   Expanded:
   - "high performance laptop for 4K video editing"
   - "laptop with dedicated GPU for content creation"
   - "professional workstation laptop for multimedia"
   
   Products found: 12 → 28 (more comprehensive results)
   ```

3. **Plan Week 5** (1 hour)

**Deliverables Day 28**:
- Complete Week 4 documentation
- Metrics and improvements report

---

## Updated Success Criteria

✅ **Must Complete** (Revised Priority):
1. [ ] **Multi-query retrieval working** (Days 22-23) - CRITICAL
2. [ ] **Precision@5 improvement: +15% minimum** (Day 23) - CRITICAL
3. [ ] **RAGAs evaluation showing improvement** (Day 25) - HIGH
4. [ ] **Contextual compression reducing tokens 40%+** (Day 26) - MEDIUM
5. [ ] **Refinement tools implemented** (Day 27) - MEDIUM

🎯 **Stretch Goals**:
- [ ] Adaptive query expansion (auto-detect when to use)
- [ ] Real-time A/B testing in production
- [ ] Query expansion prompt tuning per category

---

## Expected Impact

Based on your V1 issues:

**Before (V1)**:
- "Compare MacBook Air M2 and Dell XPS 15" → Wrong categories → Irrelevant products
- Single query → Limited coverage → Misses relevant products

**After (V2 with Multi-Query)**:
- Same query → 3 variations:
  1. "compare Apple MacBook Air M2 vs Dell XPS 15"
  2. "MacBook Air M2 Dell XPS 15 specifications comparison"
  3. "premium ultrabook comparison Apple vs Dell"
- Results merged with RRF → Both products found → Correct comparison

**Estimated Improvements**:
- Category matching: 65% → 90%
- Product coverage: +40% more relevant products found
- User satisfaction: Fewer "product not found" scenarios

---

## Next Steps

Ready to start **Day 22: Multi-Query Retrieval Foundation**? 

I can help you with:
1. Writing the query expansion prompt
2. Implementing the parallel retrieval logic
3. Building the RRF scoring function
4. Setting up LangSmith tracing

Let me know which part you'd like to tackle first! 🚀
