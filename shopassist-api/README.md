# ShopAssist API

AI-Powered Product Knowledge & Support Agent API

## Overview

ShopAssist API is a FastAPI-based backend service that provides intelligent product support and recommendations using Azure AI services, LangChain, and Retrieval-Augmented Generation (RAG). The API handles product queries, policy questions, and product comparisons through natural language conversations.

## Features

- 🤖 AI-powered conversational assistant
- 🔍 Product search with semantic understanding
- 📊 Product comparison capabilities
- 📚 Knowledge base integration for policies and FAQs
- 🎯 Intent classification and query routing
- 💾 Session management and conversation history
- 🔄 Redis caching for performance
- 📈 LangSmith integration for tracing and monitoring
- 🐳 Docker support for containerized deployment

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11
- **AI/ML**: 
  - Azure OpenAI (GPT-4)
  - LangChain
  - Sentence Transformers
- **Databases**:
  - Azure Cosmos DB (sessions & messages)
  - Milvus (vector database)
  - Redis (caching)
- **Monitoring**: LangSmith
- **Cloud**: Azure (OpenAI, Cosmos DB, Cognitive Search)

## Prerequisites

- Python 3.11 or higher
- Conda (recommended) or pip
- Docker & Docker Compose (for containerized deployment)
- Azure subscription with:
  - Azure OpenAI
  - Azure Cosmos DB
  - Azure Cognitive Search (optional)
- Milvus instance (local or cloud)
- Redis instance (local or cloud)

## Project Structure

```
shopassist-api/
├── shopassist_api/
│   ├── main.py                      # FastAPI application entry point
│   ├── api/                         # API endpoints
│   │   ├── chat.py                  # Chat endpoints
│   │   ├── health.py                # Health checks
│   │   ├── products.py              # Product endpoints
│   │   ├── search.py                # Search endpoints
│   │   └── session.py               # Session management
│   ├── application/                 # Application layer
│   │   ├── services/                # Business logic services
│   │   │   ├── rag_service.py       # RAG orchestration
│   │   │   ├── query_processor.py   # Query processing
│   │   │   ├── context_builder.py   # Context building
│   │   │   └── llm_sufficiency_builder.py
│   │   ├── prompts/                 # Prompt templates
│   │   ├── interfaces/              # Service interfaces
│   │   └── settings/                # Configuration
│   ├── domain/                      # Domain models
│   │   └── models/                  # Data models
│   └── infrastructure/              # Infrastructure layer
│       └── services/                # External service implementations
│           ├── cosmos_product_service.py
│           ├── milvus_vector_service.py
│           ├── redis_cache_service.py
│           └── transformers_embedding_service.py
├── tests/                           # Test suite
│   ├── test_services/              # Service tests
│   └── test_dependency_injection.py
├── scripts/                         # Utility scripts
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker configuration
├── pytest.ini                       # Pytest configuration
└── pyproject.toml                  # Project metadata
```

## Getting Started

### 1. Clone and Navigate

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
AZURE_OPENAI_MODEL_DEPLOYMENT=your-deployment-name

# Azure Cosmos DB
COSMOSDB_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOSDB_DATABASE=shopassist
COSMOSDB_PRODUCT_CONTAINER=products
COSMOSDB_MESSAGES_CONTAINER=messages
COSMOSDB_SESSION_CONTAINER=sessions

# Milvus Vector Database
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_PRODUCT_COLLECTION=product_collection
MILVUS_KNOWLEDGE_BASE_COLLECTION=knowledge_base_collection

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# LangSmith (optional - for tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ShopAssistAPI
LANGSMITH_API_KEY=your-langsmith-key

# Application Settings
LOG_LEVEL=INFO
LOG_FILE=logs/shopassist.log
DEBUG=false
```

### 3. Install Dependencies

**Option A: Using Conda (Recommended)**

```bash
# Create conda environment from root directory
cd ..
conda env create -f environment.yml
conda activate saaivenv

# Install in development mode
cd shopassist-api
pip install -e .
```

**Option B: Using pip**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Run the Development Server

```bash
# Using the development server script
python dev_server.py

# Or using uvicorn directly
uvicorn shopassist_api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/api/v1/health

# View API documentation
# Open browser: http://localhost:8000/docs
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - Service health status
- `GET /api/v1/health/ready` - Readiness check (all services initialized) for kubernetes
- `GET /api/v1/health/full` - Service health check detailed(all services tested and running)

### Chat
- `POST /api/v1/chat` - Send message and get AI response
- `GET /api/v1/chat/history/{session_id}` - Get conversation history

### Products
- `GET /api/v1/products/{product_id}` - Get product by ID
- `GET /api/v1/products/search/category/{category}` - Search by category
- `GET /api/v1/products/search/price?min_price={min}&max_price={max}` - Search by price range

### Sessions
- `POST /api/v1/session` - Create new session
- `GET /api/v1/session/{session_id}` - Get session details
- `DELETE /api/v1/session/{session_id}` - Delete session

### Search
- `POST /api/v1/search` - Semantic search across products

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
  shopassist-api:1.0
```

### Using Docker Compose

```bash
# From project root
docker-compose up -d shopassist-api
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=shopassist_api

# Run specific test file
pytest tests/test_services/test_query_processor.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Linting
flake8 shopassist_api

# Type checking
mypy shopassist_api

# Format code
black shopassist_api
```

### Project Commands

```bash
# Activate environment
conda activate saaivenv

# Update dependencies
pip install -r requirements.txt

# Run development server
python dev_server.py

# Run tests
pytest

# View logs
tail -f logs/shopassist.log
```

## Architecture

### Service Layers

1. **API Layer** (`api/`) - FastAPI routes and request handling
2. **Application Layer** (`application/`) - Business logic and orchestration
3. **Domain Layer** (`domain/`) - Core domain models
4. **Infrastructure Layer** (`infrastructure/`) - External service implementations

### Key Services

- **RAGService**: Orchestrates RAG pipeline and intent routing
- **QueryProcessor**: Extracts filters and processes queries
- **ContextBuilder**: Builds context from retrieved documents
- **LLMSufficiencyBuilder**: Analyzes query sufficiency and intent
- **EmbeddingService**: Generates embeddings for semantic search
- **VectorService**: Manages vector database operations
- **CacheService**: Redis caching layer

### Dependency Injection

Services are managed through a DI container (`di_container.py`) ensuring:
- Singleton pattern for expensive services
- Easy testing with mock services
- Centralized service configuration

## Configuration

All configuration is managed through `application/settings/config.py` using Pydantic settings.

Key settings:
- `azure_openai_*` - Azure OpenAI configuration
- `cosmosdb_*` - Cosmos DB settings
- `milvus_*` - Vector database settings
- `redis_*` - Cache settings
- `embedding_*` - Embedding model configuration
- `threshold_*` - Similarity thresholds

## Monitoring

### LangSmith Integration

The API integrates with LangSmith for tracing:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ShopAssistAPI
LANGSMITH_API_KEY=your-key
```

View traces at: https://smith.langchain.com/

### Logging

Logs are written to:
- Console (development)
- File: `logs/shopassist.log` (production)

Configure via:
```env
LOG_LEVEL=INFO
LOG_FILE=logs/shopassist.log
LOG_TO_CONSOLE=true
```

## Troubleshooting

### Service won't start

```bash
# Check environment variables
python -c "from shopassist_api.application.settings.config import settings; print(settings)"

# Verify Azure credentials
az account show

# Check service connectivity
curl http://localhost:8000/api/v1/health
```

### Slow first request

The first request loads ML models. To preload:
- Services are warmed up in `lifespan` function
- Or call `/api/v1/health` after startup

### Docker image too large

Ensure `.dockerignore` excludes:
- `__pycache__`
- `*.pyc`
- `.venv`
- `models/` (download at runtime)
- `.git`

### Tests failing

```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv

# Check environment
pytest --collect-only
```

## Contributing

1. Create a feature branch
2. Make changes
3. Write/update tests
4. Run test suite: `pytest`
5. Check code quality: `flake8`, `mypy`
6. Submit pull request

## Performance

- **Average response time**: ~500ms (with cache)
- **First request**: ~2-3s (model loading)
- **Throughput**: ~100 req/s
- **Docker image**: ~800MB

## Security

- API keys stored in environment variables
- Azure Managed Identity support
- CORS configured for frontend origin
- Request validation with Pydantic
- No sensitive data in logs

## License

Part of the ShopAssist AI Product Support Agent system.

## Related Projects

- [ShopAssist UI](../shopassist-ui/README.md) - React frontend application

## Support

For issues or questions, please check:
- API documentation: `http://localhost:8000/docs`
- Logs: `logs/shopassist.log`
- LangSmith traces: https://smith.langchain.com/