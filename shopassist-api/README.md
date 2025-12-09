# ShopAssist API

AI-Powered Product Knowledge & Support Agent API with Multi-Agent Architecture

## Overview

ShopAssist API is a FastAPI-based backend service that provides intelligent product support and recommendations using Azure AI services, LangChain, LangGraph, and Retrieval-Augmented Generation (RAG). The API employs a multi-agent architecture with specialized agents for product discovery and policy queries, orchestrated through LangGraph for intelligent conversation routing.

## Features

### Core Capabilities
- 🤖 **Multi-Agent Architecture**: Orchestrator, Product Discovery, and Policy agents
- 🔍 **Semantic Product Search**: Vector-based search with Azure OpenAI and Sentence Transformers
- 📊 **Product Comparison**: Side-by-side comparison with detailed specifications
- 📚 **Knowledge Base**: Integrated FAQ and policy document retrieval
- 🎯 **Intent Classification**: Smart routing based on query type
- 💾 **Session Management**: Persistent conversation history with Azure Cosmos DB
- 🔄 **Redis Caching**: Performance optimization for repeated queries
- 📈 **Observability**: LangSmith integration for tracing and monitoring
- 💰 **Token Monitoring**: Track and optimize LLM costs
- 🐳 **Docker Ready**: Full containerization support

### Technical Features
- **LangGraph Agents**: State-based multi-agent workflows
- **RAG Pipeline**: Retrieval-Augmented Generation for grounded responses
- **Dependency Injection**: Clean architecture with DI container
- **Service Warmup**: Pre-load ML models on startup
- **Robust Error Handling**: Graceful degradation and detailed logging
- **Health Checks**: Multiple endpoints for liveness and readiness
- **Pydantic v2**: Modern data validation and settings management

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11
- **AI/ML**: 
  - Azure OpenAI (GPT-4 Mini for generation)
  - Azure OpenAI (text-embedding-3-small)
  - LangChain 0.3+
  - LangGraph (Multi-agent orchestration)
  - Sentence Transformers (all-MiniLM-L6-v2)
- **Databases**:
  - Azure Cosmos DB (sessions, messages & products)
  - Milvus 2.3+ (vector database)
  - Redis 7+ (caching)
- **Monitoring**: LangSmith
- **Cloud**: Azure (OpenAI, Cosmos DB)

## Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────┐
│         Orchestrator Agent              │
│     (LangGraph State Machine)           │
│                                         │
│  - Intent Classification                │
│  - Agent Routing                        │
│  - Response Aggregation                 │
└────────────┬────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
     ▼                ▼
┌─────────────┐  ┌────────────────┐
│  Product    │  │  Policy        │
│  Discovery  │  │  Agent         │
│  Agent      │  │                │
│             │  │  - FAQ         │
│  - Search   │  │  - Policies    │
│  - Filter   │  │  - Returns     │
│  - Compare  │  │  - Shipping    │
└─────────────┘  └────────────────┘
```

### Service Layers

```
┌─────────────────────────────────────────┐
│          API Layer (FastAPI)            │
│  - REST Endpoints                       │
│  - Request Validation                   │
│  - Response Formatting                  │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│       Application Layer                 │
│  - Agents (Orchestrator, Discovery)     │
│  - Services (RAG, Query Processing)     │
│  - Prompts & Templates                  │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          Domain Layer                   │
│  - Domain Models                        │
│  - Business Logic                       │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│      Infrastructure Layer               │
│  - Cosmos DB Service                    │
│  - Milvus Vector Service                │
│  - Redis Cache Service                  │
│  - Embedding Service                    │
└─────────────────────────────────────────┘
```

## Prerequisites

- **Python** 3.11 or higher
- **Conda** (recommended) or pip
- **Docker** & Docker Compose (for containerized deployment)
- **Azure subscription** with:
  - Azure OpenAI Service
  - Azure Cosmos DB (NoSQL API)
- **Milvus** instance (local via Docker or cloud)
- **Redis** instance (local via Docker or cloud)
- **LangSmith** account (optional, for tracing)

## Project Structure

```
shopassist-api/
├── shopassist_api/
│   ├── main.py                          # FastAPI application entry point
│   ├── logging_config.py                # Logging configuration
│   │
│   ├── api/                             # API endpoints
│   │   ├── chat.py                      # Chat endpoints
│   │   ├── health.py                    # Health checks
│   │   ├── products.py                  # Product endpoints
│   │   ├── search.py                    # Search endpoints
│   │   └── session.py                   # Session management
│   │
│   ├── application/                     # Application layer
│   │   ├── agents/                      # LangGraph agents
│   │   │   ├── orchestrator.py          # Main orchestrator agent
│   │   │   ├── product_discovery_agent.py
│   │   │   ├── policy_agent.py
│   │   │   └── models.py                # Agent models & states
│   │   │
│   │   ├── services/                    # Business logic services
│   │   │   ├── rag_service.py           # RAG orchestration
│   │   │   ├── query_processor.py       # Query processing & filters
│   │   │   ├── context_builder.py       # Context building
│   │   │   └── llm_sufficiency_builder.py
│   │   │
│   │   ├── prompts/                     # Prompt templates
│   │   │   ├── system_prompts.py
│   │   │   └── templates/
│   │   │
│   │   ├── interfaces/                  # Service interfaces
│   │   │   └── di_container.py          # Dependency injection
│   │   │
│   │   └── settings/                    # Configuration
│   │       └── config.py                # Pydantic settings
│   │
│   ├── domain/                          # Domain models
│   │   └── models/                      # Data models
│   │       ├── chat.py
│   │       ├── product.py
│   │       └── session.py
│   │
│   └── infrastructure/                  # Infrastructure layer
│       └── services/                    # External service implementations
│           ├── cosmos_product_service.py
│           ├── cosmos_session_service.py
│           ├── milvus_vector_service.py
│           ├── redis_cache_service.py
│           ├── transformers_embedding_service.py
│           └── azure_openai_service.py
│
├── tests/                               # Test suite
│   ├── test_services/                   # Service tests
│   │   ├── test_query_processor.py
│   │   └── test_rag_service.py
│   ├── test_agents/                     # Agent tests
│   └── test_dependency_injection.py
│
├── scripts/                             # Utility scripts
│   ├── data/                            # Data generation
│   ├── testing/                         # Test scripts
│   └── deployment/                      # Deployment utilities
│
├── logs/                                # Application logs
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Docker configuration
├── .dockerignore                        # Docker ignore patterns
├── pytest.ini                           # Pytest configuration
├── pyproject.toml                       # Project metadata
├── dev_server.py                        # Development server script
└── README.md                            # This file
```

## Getting Started

### 1. Navigate to API Directory

```bash
cd shopassist-api
```

### 2. Environment Setup

Create a `.env` file with your configuration:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_MODEL=gpt-4
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4-mini-deployment-name

# Embedding Configuration
EMBEDDING_PROVIDER=azure_openai  # or 'transformers'
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=embedding-deployment-name

# Azure Cosmos DB
COSMOSDB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOSDB_KEY=your-cosmos-key
COSMOSDB_DATABASE=shopassist
COSMOSDB_PRODUCT_CONTAINER=products
COSMOSDB_MESSAGES_CONTAINER=messages
COSMOSDB_SESSION_CONTAINER=sessions

# Milvus Vector Database
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=
MILVUS_PASSWORD=
MILVUS_PRODUCT_COLLECTION=product_collection
MILVUS_KNOWLEDGE_BASE_COLLECTION=knowledge_base_collection

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_SSL=false

# LangSmith (optional - for tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ShopAssistAPI
LANGSMITH_API_KEY=lsv2_pt_your-key-here

# Application Settings
LOG_LEVEL=INFO
LOG_FILE=logs/shopassist.log
LOG_TO_CONSOLE=true
DEBUG=false

# Service Configuration
USE_DUMB_SERVICE=false  # Set true for testing without external services
```

### 3. Install Dependencies

**Option A: Using Conda (Recommended)**

```bash
# Create conda environment from root directory
cd ..
conda env create -f environment.yml
conda activate saaivenv

# Return to API directory
cd shopassist-api

# Install in development mode
pip install -e .
```

**Option B: Using pip with venv**

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Initialize Databases (First Time Setup)

```bash
# Generate sample product data
python scripts/data/generate_products.py

# Load data to Cosmos DB
python scripts/data/load_cosmos_db.py

# Generate embeddings and load to Milvus
python scripts/data/load_milvus.py
```

### 5. Run the Development Server

```bash
# Using the development server script
python dev_server.py

# Or using uvicorn directly
uvicorn shopassist_api.main:app --reload --host 0.0.0.0 --port 8000

# Or with custom port
uvicorn shopassist_api.main:app --reload --port 8080
```

The API will be available at `http://localhost:8000`

### 6. Verify Installation

```bash
# Check basic health
curl http://localhost:8000/api/v1/health

# Check detailed health (all services)
curl http://localhost:8000/api/v1/health/full

# View interactive API documentation
# Open browser: http://localhost:8000/docs
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - Minimum service health status
- `GET /api/v1/health/ready` - Basic service health status
- `GET /api/v1/health/full` - Detailed health check (Cosmos DB, Milvus, Redis, LLM)

**Response Example:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-09T10:30:00Z",
  "services": {
    "api": "up",
    "database": "connected",
    "vector_db": "connected",
    "cache": "connected",
    "llm": "operational"
  }
}
```

### Chat
- `POST /api/v1/chat/orchestrate` - Send message and get AI response

**Request:**
```json
{
  "message": "Show me laptops under $1500",
  "session_id": "abc123def456"  // optional
}
```

**Response:**
```json
{
  "response": "I found 5 laptops under $1500...",
  "sources": [
    {
      "product_id": "p001",
      "name": "Dell XPS 13",
      "price": 1299.99,
      "category": "Laptops"
    }
  ],
  "session_id": "abc123def456",
  "suggestions": ["Compare with MacBook", "Show more details"]
}
```

- `GET /api/v1/chat/history/{session_id}` - Get conversation history

### Products
- `GET /api/v1/products/{product_id}` - Get product details by ID
- `GET /api/v1/products/search/category/{category}` - Search by category
- `GET /api/v1/products/search/price?min_price=100&max_price=500` - Filter by price range

### Sessions
- `POST /api/v1/session` - Create new chat session
- `GET /api/v1/session/{session_id}` - Get session details
- `DELETE /api/v1/session/{session_id}` - Delete session and conversation history

### Search
- `POST /api/v1/search` - Semantic search across products

**Request:**
```json
{
  "query": "gaming laptop with RTX 4070",
  "top_k": 5
}
```

## Docker Deployment

### Build Image

```bash
docker build -t shopassist-api:1.0 .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  --name shopassist-api \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  shopassist-api:1.0
```

### Using Docker Compose

```bash
# From project root directory
docker-compose up -d shopassist-api

# View logs
docker-compose logs -f shopassist-api

# Stop service
docker-compose stop shopassist-api
```

## Development

### Running Tests

```bash
# Activate conda environment
conda activate saaivenv

# Run all tests
pytest

# Run with coverage report
pytest --cov=shopassist_api --cov-report=html

# Run specific test file
pytest tests/test_services/test_query_processor.py -v

# Run tests with LangSmith tracing
LANGCHAIN_TRACING_V2=true pytest

# Run only unit tests (exclude integration)
pytest -m "not integration"
```

### Code Quality

```bash
# Linting
flake8 shopassist_api

# Type checking
mypy shopassist_api

# Format code
black shopassist_api

# Sort imports
isort shopassist_api
```

### Development Workflow

```bash
# 1. Activate environment
conda activate saaivenv

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Make changes and run tests
pytest

# 4. Check code quality
flake8 shopassist_api
mypy shopassist_api

# 5. View logs during development
tail -f logs/shopassist.log

# 6. Test API manually
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test query"}'
```

## Configuration

### Settings Management

All configuration is managed through `application/settings/config.py` using Pydantic v2 settings:

```python
from shopassist_api.application.settings.config import settings

# Access settings
print(settings.azure_openai_endpoint)
print(settings.log_level)
```

### Key Configuration Options

**LLM Settings:**
- `azure_openai_model` - Model name (e.g., "gpt-4-mini")
- `azure_openai_model_deployment` - Azure deployment name
- `azure_openai_temperature` - Response randomness (0.0-1.0)
- `azure_openai_max_tokens` - Maximum response length

**Embedding Settings:**
- `embedding_provider` - "azure_openai" or "transformers"
- `embedding_model` - Model name for embeddings
- `embedding_dimension` - Vector dimension (384 or 1536)

**Search Settings:**
- `top_k_products` - Number of products to retrieve (default: 10)
- `top_k_categories` - Number of categories for expansion (default: 3)
- `threshold_category_similarity` - Similarity threshold (default: 0.75)

**Performance Settings:**
- `redis_ttl` - Cache time-to-live in seconds (default: 3600)
- `query_expansion_max_variations` - Max query variations (default: 2)

## Monitoring & Observability

### LangSmith Integration

The API integrates with LangSmith for comprehensive tracing:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ShopAssistAPI
LANGSMITH_API_KEY=your-key
```

**Features:**
- LLM call tracing with input/output
- Agent execution visualization
- Token usage and cost tracking
- Error tracking and debugging
- Performance metrics

View traces at: https://smith.langchain.com/

### Application Logging

**Log Levels:**
- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages with stack traces

**Log Configuration:**
```env
LOG_LEVEL=INFO
LOG_FILE=logs/shopassist.log
LOG_TO_CONSOLE=true
```

**View Logs:**
```bash
# Tail logs in real-time
tail -f logs/shopassist.log

# Filter for errors
grep "ERROR" logs/shopassist.log

# Search for specific session
grep "session_id: abc123" logs/shopassist.log
```

### Health Monitoring

```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Detailed health check (tests all services)
curl http://localhost:8000/api/v1/health/full

# Check from Docker
docker exec shopassist-api curl http://localhost:8000/api/v1/health
```

## Troubleshooting

### Service won't start

```bash
# Check environment variables are loaded
python -c "from shopassist_api.application.settings.config import settings; print(settings.dict())"

# Verify Python version
python --version  # Should be 3.11+

# Check if port is already in use
lsof -i :8000  # On Mac/Linux
netstat -ano | findstr :8000  # On Windows

# Verify Azure credentials
az account show
```

### Slow first request

The first request loads ML models (~3s). This is normal.

**Solutions:**
- Services are pre-warmed in the `lifespan` function
- Call `/api/v1/health/full` after startup to trigger loading
- Use Redis caching for repeated queries

### Database connection errors

```bash
# Test Cosmos DB connection
python scripts/testing/test_cosmos_connection.py

# Test Milvus connection
python scripts/testing/test_milvus_connection.py

# Test Redis connection
python scripts/testing/test_redis_connection.py
```

### Docker image too large (>2GB)

Ensure `.dockerignore` excludes unnecessary files:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/
env/
ENV/
*.log
.git/
.gitignore
tests/
*.md
.vscode/
.idea/
models/
checkpoints/
.cache/
```

### LangSmith not showing traces

```bash
# Verify environment variables
echo $LANGCHAIN_TRACING_V2  # Should be "true"
echo $LANGSMITH_API_KEY     # Should be set

# Check logs for LangSmith errors
grep "langsmith" logs/shopassist.log

# Test with simple script
python scripts/testing/test_langsmith.py
```

### Tests failing

```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv

# Check test collection
pytest --collect-only

# Run specific failing test
pytest tests/test_services/test_query_processor.py::test_extract_filters -vv
```

### Out of memory errors

```bash
# Reduce batch sizes in config
# Check memory usage
docker stats shopassist-api

# Increase Docker memory limit
# In Docker Desktop: Settings > Resources > Memory
```

## Performance

### Benchmarks

- **Average Response Time**: ~500ms (cached), ~1.5s (uncached)
- **First Request (Cold Start)**: ~3s (model loading)
- **Embedding Generation**: 
  - Azure OpenAI: ~100-150ms
  - Local Transformers: ~50-80ms
- **Vector Search (Milvus)**: ~50-100ms for 10k products
- **LLM Generation**: ~800ms-1.5s (depends on response length)
- **Cache Hit Rate**: ~60% for common queries
- **Throughput**: ~50-100 req/s (single instance)

### Optimization Tips

1. **Enable Redis Caching**: Set `REDIS_HOST` in `.env`
2. **Use Local Embeddings**: Set `EMBEDDING_PROVIDER=transformers` for faster embedding
3. **Adjust `top_k`**: Reduce `TOP_K_PRODUCTS` for faster retrieval
4. **Preload Models**: Service warmup in lifespan function
5. **Use GPT-4 Mini**: Lower cost and faster than GPT-4

### Resource Usage

- **Memory**: ~2GB (with loaded models)
- **CPU**: 1-2 cores recommended
- **Docker Image**: ~800MB
- **Storage**: Minimal (logs only)

## Security

- ✅ Environment variables for sensitive credentials
- ✅ No hardcoded secrets in code
- ✅ Azure Managed Identity support (planned)
- ✅ CORS configured for specific origins
- ✅ Request validation with Pydantic v2
- ✅ Input sanitization for user queries
- ✅ No PII/sensitive data in logs
- ✅ Secure session management with UUIDs
- 🔄 Rate limiting (planned)
- 🔄 API authentication & authorization (planned)

## Contributing

1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
2. Make your changes
3. Write/update tests
4. Run full test suite: `pytest`
5. Check code quality: `flake8`, `mypy`
6. Update documentation
7. Submit pull request

### Code Style Guidelines

- Follow PEP 8
- Use type hints for all functions
- Write docstrings for public APIs
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic

## License

Part of the ShopAssist AI Product Support Agent system.

## Related Projects

- [ShopAssist UI](../shopassist-ui/README.md) - React frontend application
- [Main Documentation](../README.md) - Project overview

## Support & Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **LangSmith Traces**: https://smith.langchain.com/
- **Application Logs**: `logs/shopassist.log`
- **LangChain Docs**: https://python.langchain.com/
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## Changelog

### v2.0.0 (Current)
- ✅ Multi-agent architecture with LangGraph
- ✅ Product Discovery and Policy agents
- ✅ Token usage monitoring
- ✅ Service warmup on startup
- ✅ Pydantic v2 migration
- ✅ Enhanced error handling
- ✅ Docker optimization (~800MB image)

### v1.0.0
- ✅ Initial RAG implementation
- ✅ Basic chat functionality
- ✅ Product search and retrieval
- ✅ Session management
- ✅ LangSmith integration

---

**Built with ❤️ using FastAPI, LangChain, and Azure AI**