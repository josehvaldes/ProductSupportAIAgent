# ShopAssist V2 - Advanced RAG Architecture
## Technical Architecture Document

**Project**: ShopAssist V2 - Production-Ready Multi-Agent RAG System  
**Version**: 2.0  
**Timeline**: 8 weeks  
**Build Upon**: V1 (6 weeks completed, Nov 2025)  
**Tech Stack**: React + Mantine, FastAPI, LangGraph, LangChain, Milvus, Azure OpenAI, LangSmith  

---

## 1. Executive Summary

### 1.1 V1 Achievements & Lessons Learned

**What Worked Well** (Retain for V2):
- ✅ Clean architecture with dependency injection
- ✅ Mantine UI framework (faster development than Tailwind)
- ✅ Cosmos DB for structured data (products, sessions)
- ✅ Redis caching layer
- ✅ Intent classification system
- ✅ Multi-strategy retrieval (vector + keyword)
- ✅ Session management with preference tracking

**Pain Points** (Fix in V2):
- ❌ **No observability**: Debugging RAG pipeline was difficult
- ❌ **Monolithic RAG flow**: Hard to optimize individual components
- ❌ **Manual orchestration**: Complex if-else logic for routing queries
- ❌ **Limited testing**: No automated RAG evaluation (RAGAs)
- ❌ **Poor error recovery**: Failed retrievals crashed entire flow
- ❌ **No feedback loop**: Can't improve from user interactions

**Performance Bottlenecks**:
- Category classification using e5-large-v2 (slow, 768 dims)
- Sequential retrieval → LLM calls (no parallelization)
- Context building inefficient for multi-turn conversations

### 1.2 V2 Goals

**Primary Objectives**:
1. **Production-grade observability** with LangSmith tracing
2. **10x better retrieval accuracy** through multi-agent architecture
3. **Automated evaluation** using RAGAs framework
4. **Robust error handling** with retry mechanisms and fallbacks
5. **Scalable orchestration** using LangGraph state machines

**Key Improvements**:
- Replace custom RAG pipeline → LangGraph workflow
- Add specialized agents for different query types
- Implement supervisor agent for routing
- Add RAGAs for automated quality monitoring
- Create synthetic test data generation
- Build feedback collection and retraining pipeline

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     User Interface (V1)                      │
│              React + Mantine (Minimal Changes)               │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTPS/WebSocket
┌────────────────────▼─────────────────────────────────────────┐
│                   API Gateway Layer (V1)                     │
│                  FastAPI with Clean Architecture             │
│  ┌──────────────┬──────────────┬─────────────────────────┐   │
│  │ Chat API     │ Product API  │ Analytics API (NEW)     │   │
│  └──────────────┴──────────────┴─────────────────────────┘   │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│              LangGraph Orchestration Layer (NEW)             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Supervisor Agent (Router)                              │ │
│  │  ├─> Product Discovery Agent                            │ │
│  │  ├─> Product Detail Agent                               │ │
│  │  ├─> Comparison Agent                                   │ │
│  │  ├─> Policy Agent                                       │ │
│  │  └─> Escalation Agent                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  LangChain Components                                   │ │
│  │  ├─> Retrievers (Product, Knowledge, Hybrid)            │ │
│  │  ├─> Prompt Templates                                   │ │
│  │  ├─> Output Parsers                                     │ │
│  │  └─> Memory (Conversation Buffer)                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│              Observability Layer (NEW)                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │ LangSmith      │  │ RAGAs          │  │ Azure App      │  │
│  │ (Tracing)      │  │ (Evaluation)   │  │ Insights       │  │
│  └────────────────┘  └────────────────┘  └────────────────┘  │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│              Retrieval Layer (Enhanced from V1)              │
│  ┌────────────────┐  ┌──────────────────────────────────┐    │
│  │ Milvus Vector  │  │ Azure AI Search                  │    │
│  │ Database       │  │ (Hybrid Search)                  │    │
│  │ + Categories   │  │                                  │    │
│  └────────────────┘  └──────────────────────────────────┘    │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│              LLM & Embedding Layer (V1)                      │
│  ┌────────────────┐  ┌──────────────────────────────────┐    │
│  │ Azure OpenAI   │  │ text-embedding-3-small           │    │
│  │ GPT-4.1-mini   │  │                                  │    │
│  └────────────────┘  └──────────────────────────────────┘    │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│              Data & Storage Layer (V1)                       │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐   │
│  │ Cosmos DB  │  │ Redis    │  │ Blob     │  │ Postgres  │   │
│  │ (Products, │  │ (Cache)  │  │ Storage  │  │ (Feedback)│   │
│  │  Sessions) │  │          │  │ (Images) │  │  (NEW)    │   │
│  └────────────┘  └──────────┘  └──────────┘  └───────────┘   │
└──────────────────────────────────────────────────────────────┘
```
