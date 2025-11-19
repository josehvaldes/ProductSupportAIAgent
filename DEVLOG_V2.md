#DEVLOG v2

### Phase 1: Add Observability (Week 1)
**Goal**: Get visibility into current system

## Week 1 Add Observability

- [ ] Install LangSmith and instrument V1 code
- [ ] Add custom tracing to key functions
- [ ] Create LangSmith dashboard
- [ ] Identify top 3 bottlenecks
- [ ] Measure baseline metrics (latency, accuracy)

**No breaking changes** - Add observability layer


### Phase 2: Migrate to LangGraph (Weeks 2-3)

**Goal**: Replace custom orchestration with LangGraph

## Week 2 LangGraph flows

- [ ] Start with simplest flow (policy questions)
- [ ] Create single-agent LangGraph workflow
- [ ] Test parity with V1 responses
- [ ] Gradually migrate other intents
- [ ] Keep V1 as fallback during migration

**Deliverable**: All V1 functionality working in LangGraph