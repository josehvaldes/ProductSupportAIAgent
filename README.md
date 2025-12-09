# ShopAssist - AI Product Support Agent

An intelligent conversational AI agent for e-commerce product support and discovery, built with RAG (Retrieval-Augmented Generation) and LangGraph architecture.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-19.1-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## 🎯 Overview

ShopAssist is a full-stack AI application that provides intelligent product support through natural language conversations. It combines semantic search, vector databases, LangGraph agents, and large language models to help users:

- 🔍 **Discover products** through natural conversation
- 📊 **Compare products** side-by-side with detailed specifications
- ❓ **Get answers** about policies, shipping, and returns
- 🎯 **Receive personalized recommendations** based on requirements
- 💬 **Maintain context** across multi-turn conversations
- 🤖 **Multi-agent orchestration** with specialized agents for different tasks

Built as a portfolio project showcasing modern AI engineering practices and production-ready architecture.

## ✨ Key Features

### Core Capabilities
- **LangGraph Agents**: Multi-agent architecture with Product Discovery and Policy agents
- **Semantic Search**: Vector-based product search using Azure OpenAI and Sentence Transformers embeddings
- **RAG Pipeline**: Retrieval-Augmented Generation for accurate, grounded responses
- **Intent Classification**: Smart routing of queries (product search, policy, comparison)
- **Session Management**: Persistent conversation history with Azure Cosmos DB
- **Real-time Chat**: Interactive chat interface with message streaming
- **Product Comparison**: Side-by-side comparison of multiple products with detailed specs

### Technical Features
- **Observability**: LangSmith integration for tracing, monitoring, and debugging
- **Token Monitoring**: Track token usage and costs across all LLM calls
- **Caching**: Redis-based caching for improved performance
- **Error Handling**: Robust error handling with graceful degradation
- **Dependency Injection**: Clean architecture with DI container
- **Docker Support**: Full containerization with Docker Compose
- **Health Checks**: Comprehensive health monitoring for all services

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────────────────────┐
│   React UI      │────────▶│   FastAPI Backend                │
│   (TypeScript)  │         │   ┌────────────────────────┐     │
│   - Mantine UI  │         │   │   Orchestrator Agent   │     │
│   - Chat UI     │         │   │   (LangGraph)          │     │
└─────────────────┘         │   └───────────┬────────────┘     │
                            │               │                   │
                            │   ┌───────────┴────────────┐     │
                            │   │                        │     │
                            │   ▼                        ▼     │
                            │ ┌──────────────┐  ┌─────────────┐│
                            │ │   Product    │  │   Policy    ││
                            │ │  Discovery   │  │    Agent    ││
                            │ │    Agent     │  │             ││
                            │ └──────────────┘  └─────────────┘│
                            └──────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
            │  Azure       │ │   Milvus    │ │   Redis      │
            │  Cosmos DB   │ │   Vector DB │ │   Cache      │
            │  - Sessions  │ │  - Products │ │  - Responses │
            │  - Messages  │ │  - Policies │ └──────────────┘
            │  - Products  │ └─────────────┘
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │  Azure       │
            │  OpenAI      │
            │  GPT-4 Mini  │
            └──────────────┘
```

### Agent Architecture

**Orchestrator Agent**: Routes queries to specialized agents based on intent
- Product queries → Product Discovery Agent
- Policy/FAQ queries → Policy Agent
- Comparison queries → Product Discovery Agent with comparison mode

**Product Discovery Agent**: 
- Semantic product search with filters
- Category-based recommendations
- Price range filtering
- Multi-product retrieval

**Policy Agent**:
- Knowledge base retrieval
- FAQ responses
- Policy explanations

### Technology Stack

**Frontend:**
- React 19 with TypeScript
- Mantine UI 8.3 (Component Library)
- Vite (Build Tool)
- React Markdown (Message Rendering)
- Tabler Icons

**Backend:**
- Python 3.11
- FastAPI (REST API Framework)
- LangChain & LangGraph (Agent Orchestration)
- Pydantic v2 (Data Validation)

**AI/ML:**
- Azure OpenAI (GPT-4 Mini for generation)
- Azure OpenAI (text-embedding-3-small for embeddings)
- Sentence Transformers (all-MiniLM-L6-v2 for local embeddings)
- LangSmith (Tracing & Monitoring)

**Data Storage:**
- Azure Cosmos DB (Sessions, Messages & Products)
- Milvus 2.3+ (Vector Database)
- Redis 7+ (Caching Layer)

**Infrastructure:**
- Docker & Docker Compose
- Azure Cloud Services
- Nginx (Frontend serving)

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Conda** (recommended for environment management)
- **Docker** & Docker Compose (for containerized deployment)
- **Azure Account** with:
  - Azure OpenAI Service (GPT-4 Mini deployment)
  - Azure Cosmos DB (NoSQL API)
- **Milvus** instance (local via Docker or cloud)
- **Redis** instance (local via Docker or cloud)
- **LangSmith** account (optional, for tracing)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ProductSupportAIAgent.git
   cd ProductSupportAIAgent
   ```

2. **Configure environment variables:**
   ```bash
   # Copy environment templates
   cp shopassist-api/.env.example shopassist-api/.env
   cp shopassist-ui/.env.example shopassist-ui/.env
   
   # Edit API environment variables
   nano shopassist-api/.env
   ```

   Required environment variables:
   ```env
   # Azure OpenAI
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4-mini-deployment-name
   
   # Azure Cosmos DB
   COSMOSDB_ENDPOINT=https://your-account.documents.azure.com:443/
   COSMOSDB_KEY=your-cosmos-key
   
   # Milvus
   MILVUS_HOST=milvus-standalone
   MILVUS_PORT=19530
   
   # Redis
   REDIS_HOST=redis
   REDIS_PORT=6379
   
   # LangSmith (optional)
   LANGCHAIN_TRACING_V2=true
   LANGSMITH_API_KEY=your-langsmith-key
   LANGCHAIN_PROJECT=ShopAssistAPI
   ```

3. **Build and start all services:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend UI: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - LangSmith Traces: https://smith.langchain.com/

### Manual Setup

#### Backend Setup

```bash
cd shopassist-api

# Create conda environment from root directory
cd ..
conda env create -f environment.yml
conda activate saaivenv

# Return to API directory and install
cd shopassist-api
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run development server
python dev_server.py
```

Backend runs at: http://localhost:8000

#### Frontend Setup

```bash
cd shopassist-ui

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000/api/v1

# Run development server
npm run dev
```

Frontend runs at: http://localhost:5173

## 📁 Project Structure

```
ProductSupportAIAgent/
├── shopassist-api/              # FastAPI Backend
│   ├── shopassist_api/
│   │   ├── api/                 # API endpoints
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   ├── health.py        # Health checks
│   │   │   ├── products.py      # Product endpoints
│   │   │   └── session.py       # Session management
│   │   ├── application/         # Business logic
│   │   │   ├── agents/          # LangGraph agents
│   │   │   │   ├── orchestrator.py           # Main orchestrator
│   │   │   │   ├── product_discovery_agent.py
│   │   │   │   └── policy_agent.py
│   │   │   ├── services/        # Core services
│   │   │   │   ├── rag_service.py
│   │   │   │   ├── query_processor.py
│   │   │   │   └── context_builder.py
│   │   │   ├── prompts/         # Prompt templates
│   │   │   ├── interfaces/      # DI container
│   │   │   └── settings/        # Configuration
│   │   ├── domain/              # Domain models
│   │   ├── infrastructure/      # External services
│   │   │   ├── cosmos_product_service.py
│   │   │   ├── milvus_vector_service.py
│   │   │   ├── redis_cache_service.py
│   │   │   └── transformers_embedding_service.py
│   │   ├── logging_config.py    # Logging setup
│   │   └── main.py              # FastAPI app
│   ├── tests/                   # Test suite
│   ├── Dockerfile               # Docker configuration
│   ├── requirements.txt         # Python dependencies
│   └── README.md
│
├── shopassist-ui/               # React Frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── chat/            # Chat components
│   │   │   ├── navigation/      # Navigation
│   │   │   └── product/         # Product components
│   │   ├── hooks/               # Custom hooks (useChat)
│   │   ├── services/            # API client
│   │   ├── types/               # TypeScript types
│   │   ├── App.tsx              # Main app component
│   │   └── main.tsx             # Entry point
│   ├── Dockerfile               # Docker configuration
│   ├── package.json
│   └── README.md
│
├── dataset/                     # Sample product data
├── knowledge_base/              # Policy documents & FAQs
├── scripts/                     # Utility scripts
│   ├── data/                    # Data generation
│   ├── testing/                 # Test scripts
│   └── deployment/              # Deployment utilities
├── milvus/                      # Milvus setup & data
├── docs/                        # Documentation
├── docker-compose.yml           # Multi-container orchestration
├── environment.yml              # Conda environment
└── README.md                    # This file
```

## 🔌 API Endpoints

### Health & Status
- `GET /api/v1/health` - Minimum health check
- `GET /api/v1/health/ready` - Basic health check
- `GET /api/v1/health/full` - Detailed service health (Cosmos DB, Milvus, Redis)

### Chat
- `POST /api/v1/chat/orchestrate` - Send message and get AI response
  - Request: `{ "message": "string", "session_id": "string" }`
  - Response: `{ "response": "string", "sources": [...], "session_id": "string" }`
- `GET /api/v1/chat/history/{session_id}` - Get conversation history

### Products
- `GET /api/v1/products/{product_id}` - Get product details by ID
- `GET /api/v1/products/search/category/{category}` - Search by category
- `GET /api/v1/products/search/price?min_price={min}&max_price={max}` - Filter by price

### Sessions
- `POST /api/v1/session` - Create new chat session
- `GET /api/v1/session/{session_id}` - Get session details
- `DELETE /api/v1/session/{session_id}` - Delete session and history

### Search
- `POST /api/v1/search` - Semantic search across products
  - Request: `{ "query": "string", "top_k": 10 }`

Full API documentation: http://localhost:8000/docs

## 🧪 Testing

### Backend Tests

```bash
cd shopassist-api

# Activate conda environment
conda activate saaivenv

# Run all tests
pytest

# Run with coverage
pytest --cov=shopassist_api --cov-report=html

# Run specific test file
pytest tests/test_services/test_query_processor.py -v

# Run tests with LangSmith tracing
LANGCHAIN_TRACING_V2=true pytest
```

### Frontend Tests

```bash
cd shopassist-ui

# Run linting
npm run lint

# Build to check for TypeScript errors
npm run build
```

### Integration Testing

```bash
# Test scripts in scripts/testing/
python scripts/testing/test_api_endpoints.py
python scripts/testing/test_langsmith.py
```

## 📊 Performance Metrics

- **Average Response Time**: <2s (with cache: <500ms)
- **First Request (Cold Start)**: ~3s (model loading)
- **Retrieval Latency**: ~300-500ms for semantic search
- **Embedding Generation**: 
  - Azure OpenAI: ~100ms per query
  - Local Transformers: ~50ms per query
- **Token Usage**: ~500-1000 tokens per conversation turn
- **Token Cost**: <$0.01 per conversation (using GPT-4 Mini)
- **Accuracy**: >90% on factual product queries
- **Cache Hit Rate**: ~60% for common queries

### Docker Image Sizes
- **API**: ~800MB (optimized from 12GB)
- **UI**: ~25MB (Nginx + static files)
- **Total Deployment**: ~850MB

## 🔐 Security

- ✅ Environment variables for sensitive credentials
- ✅ Azure Managed Identity support (ready)
- ✅ CORS configuration for frontend origin
- ✅ Request validation with Pydantic v2
- ✅ No sensitive data in logs
- ✅ Input sanitization for user queries
- ✅ Secure session management with UUIDs
- 🔄 Rate limiting (planned)
- 🔄 API authentication (planned)

## 📈 Monitoring & Observability

### LangSmith Integration
- **LLM Call Tracing**: Track all LLM interactions
- **Agent Execution**: Visualize multi-agent workflows
- **Token Usage**: Monitor costs per request
- **Error Tracking**: Debug failed requests
- **Performance Metrics**: Latency and throughput
- View traces at: https://smith.langchain.com/

### Application Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Rotating file logs: `logs/shopassist.log`
- Request/response logging
- Error stack traces

### Health Monitoring
- Service availability checks
- Database connection status
- Vector database health
- Cache status
- Model loading verification

## 🗺️ Roadmap

### Completed ✅
- [x] Product browsing and filtering
- [x] Semantic search with embeddings (Azure + Local)
- [x] RAG pipeline with Milvus vector database
- [x] Multi-turn conversations with context
- [x] Session management with Cosmos DB
- [x] Product comparison feature
- [x] Docker deployment with compose
- [x] LangSmith integration for tracing
- [x] LangGraph multi-agent architecture
- [x] Token usage monitoring
- [x] Redis caching layer
- [x] Robust error handling
- [x] Health check endpoints
- [x] Service warmup on startup
- [x] Dependency injection container

### In Progress 🚧
- [ ] Unit test coverage >80%
- [ ] Performance optimization (caching, indexing)
- [ ] Enhanced error messages for users
- [ ] Retry logic for failed API calls

### Planned 📋
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Rate limiting per user/session

## 🐛 Known Issues & Limitations

- **Cold Start**: First request after startup takes ~3s due to model loading
  - *Mitigation*: Service warmup in lifespan function
- **Docker Image Size**: API image is ~800MB
  - *Cause*: ML models and dependencies
  - *Improvement*: Multi-stage builds, model download at runtime
- **Error Messages**: Limited user-facing error details
  - *Security trade-off*: Avoid exposing internal errors
- **No Retry Logic**: Failed external API calls don't automatically retry
  - *Planned*: Exponential backoff retry mechanism
- **Session Cleanup**: Old sessions not automatically deleted
  - *Workaround*: Manual cleanup script available

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for new features
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Write unit tests (target: >80% coverage)
- Update documentation for new features
- Use conventional commits
- Add type hints to all Python functions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Jose Valdes**
- GitHub: [@josehvaldes](https://github.com/josehvaldes)
- LinkedIn: [Jose Valdes Murguia](https://linkedin.com/in/josevaldesmurguia)
- Portfolio: Coming soon!

## 🙏 Acknowledgments

- **Azure OpenAI** for powerful LLM capabilities
- **LangChain & LangGraph** for agent orchestration framework
- **Mantine** for beautiful, accessible UI components
- **FastAPI** for excellent developer experience and documentation
- **Milvus** for scalable vector search
- **LangSmith** for invaluable debugging and monitoring
- The open-source AI community

## 📚 Documentation

- [API Documentation](./shopassist-api/README.md) - Backend API details
- [Frontend Documentation](./shopassist-ui/README.md) - React UI guide
- [API Interactive Docs](http://localhost:8000/docs) - Swagger UI (when running)
- [LangSmith Traces](https://smith.langchain.com/) - Production monitoring

### Additional Resources
- [Deployment Guide](./docs/deployment.md) (planned)
- [Architecture Deep Dive](./docs/architecture.md) (planned)
- [Prompt Engineering Guide](./docs/prompts.md) (planned)

## 💡 Use Cases & Learning Outcomes

This project demonstrates:

### AI/ML Engineering
- ✅ Production-ready RAG implementation
- ✅ Multi-agent orchestration with LangGraph
- ✅ Vector database integration (Milvus)
- ✅ Embedding generation and similarity search
- ✅ LLM prompt engineering and optimization
- ✅ Cost-aware token management
- ✅ Observability with LangSmith

### Software Architecture
- ✅ Microservices architecture
- ✅ Clean architecture with dependency injection
- ✅ Domain-driven design principles
- ✅ SOLID principles
- ✅ Repository pattern for data access

### Full-Stack Development
- ✅ FastAPI REST API development
- ✅ React with TypeScript
- ✅ Modern UI with Mantine components
- ✅ Docker containerization
- ✅ Docker Compose orchestration

### Cloud & DevOps
- ✅ Azure cloud services integration
- ✅ Container deployment strategies
- ✅ Health check implementation
- ✅ Logging and monitoring setup
- ✅ Environment configuration management

Perfect for learning or as a template for similar AI-powered applications!

## 🎓 Skills Demonstrated

- **Python**: FastAPI, async/await, type hints, Pydantic
- **TypeScript/React**: Hooks, custom hooks, modern React patterns
- **AI/ML**: LangChain, LangGraph, RAG, embeddings, vector search
- **Databases**: Cosmos DB (NoSQL), Milvus (vector), Redis (cache)
- **Cloud**: Azure OpenAI, Azure Cosmos DB
- **DevOps**: Docker, Docker Compose, environment management
- **Architecture**: Clean architecture, DI, microservices
- **Testing**: pytest, integration testing, API testing
- **Monitoring**: LangSmith, structured logging, health checks

---

**⭐ If you find this project useful or educational, please consider giving it a star!**

**🐛 Found a bug or have a suggestion? [Open an issue](https://github.com/yourusername/ProductSupportAIAgent/issues)**