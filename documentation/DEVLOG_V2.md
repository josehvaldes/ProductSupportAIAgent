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


## Backlog of the week. Next To Do:

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