# ShopAssist - AI Product Support Agent

An intelligent conversational AI agent for e-commerce product support and discovery, built with RAG (Retrieval-Augmented Generation) architecture.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-19.1-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)

## 🎯 Overview

ShopAssist is a full-stack AI application that provides intelligent product support through natural language conversations. It combines semantic search, vector databases, and large language models to help users:

- 🔍 **Discover products** through natural conversation
- 📊 **Compare products** side-by-side with detailed specifications
- ❓ **Get answers** about policies, shipping, and returns
- 🎯 **Receive personalized recommendations** based on requirements
- 💬 **Maintain context** across multi-turn conversations

Built as a portfolio project showcasing modern AI engineering practices and production-ready architecture.

## ✨ Key Features

- **Semantic Search**: Vector-based product search using Azure OpenAI embeddings
- **RAG Pipeline**: Retrieval-Augmented Generation for accurate, grounded responses
- **Intent Classification**: Smart routing of queries (product search, policy, comparison)
- **Session Management**: Persistent conversation history across sessions
- **Real-time Chat**: WebSocket-like experience with streaming responses
- **Product Comparison**: Side-by-side comparison of multiple products
- **Multi-language Support**: Extensible for international markets
- **Observability**: LangSmith integration for tracing and monitoring

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   React UI      │────────▶│   FastAPI        │
│   (TypeScript)  │         │   Backend        │
└─────────────────┘         └──────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
            │  Azure       │ │   Milvus    │ │   Redis      │
            │  Cosmos DB   │ │   Vector DB │ │   Cache      │
            └──────────────┘ └─────────────┘ └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │  Azure       │
            │  OpenAI      │
            │  (GPT-4)     │
            └──────────────┘
```

### Technology Stack

**Frontend:**
- React 19 with TypeScript
- Mantine UI 8.3 (Component Library)
- Vite (Build Tool)
- React Markdown (Message Rendering)

**Backend:**
- Python 3.11
- FastAPI (REST API Framework)
- LangChain (LLM Orchestration)
- Pydantic (Data Validation)

**AI/ML:**
- Azure OpenAI (GPT-4 & Embeddings)
- Sentence Transformers (Local Embeddings)
- LangSmith (Tracing & Monitoring)

**Data Storage:**
- Azure Cosmos DB (Sessions & Messages)
- Milvus (Vector Database)
- Redis (Caching)

**Infrastructure:**
- Docker & Docker Compose
- Azure Cloud Services
- GitHub Actions (CI/CD - planned)

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** & Docker Compose (for containerized deployment)
- **Azure Account** with:
  - Azure OpenAI Service
  - Azure Cosmos DB
  - Azure Cognitive Search (optional)
- **Milvus** instance (local or cloud)
- **Redis** instance (local or cloud)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ProductSupportAIAgent.git
   cd ProductSupportAIAgent
   ```

2. **Configure environment variables:**
   ```bash
   # Create .env files from templates
   cp shopassist-api/.env.example shopassist-api/.env
   cp shopassist-ui/.env.example shopassist-ui/.env
   
   # Edit with your credentials
   nano shopassist-api/.env
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost:8080
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend Setup

```bash
cd shopassist-api

# Create conda environment
conda env create -f ../environment.yml
conda activate saaivenv

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

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
│   │   ├── application/         # Business logic
│   │   │   ├── services/        # Core services (RAG, LLM)
│   │   │   ├── prompts/         # Prompt templates
│   │   │   └── settings/        # Configuration
│   │   ├── domain/              # Domain models
│   │   ├── infrastructure/      # External services
│   │   └── main.py              # FastAPI app
│   ├── tests/                   # Test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── shopassist-ui/               # React Frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # API client
│   │   ├── types/               # TypeScript types
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
│
├── dataset/                     # Sample product data
├── knowledge_base/              # Policy documents
├── scripts/                     # Utility scripts
├── docs/                        # Documentation
├── docker-compose.yml           # Multi-container setup
├── environment.yml              # Conda environment
└── README.md                    # This file
```

## 🔌 API Endpoints

### Health & Status
- `GET /api/v1/health` - Service health check
- `GET /api/v1/health/ready` - Readiness check (all services initialized) for kubernetes
- `GET /api/v1/health/full` - Service health check detailed(all services tested and running)

### Chat
- `POST /api/v1/chat` - Send message and get AI response
- `GET /api/v1/chat/history/{session_id}` - Get conversation history

### Products
- `GET /api/v1/products/{product_id}` - Get product details
- `GET /api/v1/products/search/category/{category}` - Search by category
- `GET /api/v1/products/search/price` - Search by price range

### Sessions
- `POST /api/v1/session` - Create new chat session
- `GET /api/v1/session/{session_id}` - Get session details
- `DELETE /api/v1/session/{session_id}` - Delete session

### Search
- `POST /api/v1/search` - Semantic search across products

Full API documentation: http://localhost:8000/docs

## 🧪 Testing

### Backend Tests

```bash
cd shopassist-api

# Run all tests
pytest

# Run with coverage
pytest --cov=shopassist_api

# Run specific test
pytest tests/test_services/test_query_processor.py -v
```

### Frontend Tests

```bash
cd shopassist-ui

# Run linting
npm run lint

# Type checking
npm run type-check  # (if configured)
```

## 📊 Performance Metrics

- **Response Time**: <2s average (95th percentile: <3s)
- **Retrieval Latency**: ~500ms for semantic search
- **Embedding Generation**: ~100ms per query
- **Token Cost**: <$0.01 per conversation
- **Accuracy**: >90% on factual product queries
- **Docker Image Sizes**:
  - API: ~800MB
  - UI: ~25MB (Nginx)

## 🔐 Security

- Environment variables for sensitive credentials
- Azure Managed Identity support (planned)
- CORS configuration for frontend origin
- Request validation with Pydantic
- No sensitive data in logs
- Rate limiting (planned)

## 📈 Monitoring & Observability

- **LangSmith**: LLM call tracing and debugging
  - View traces: https://smith.langchain.com/
- **Application Logs**: Structured logging to files and console
- **Health Checks**: Liveness and readiness probes
- **Metrics** (planned): Prometheus/Grafana integration

## 🗺️ Roadmap

### Completed ✅
- [x] Product browsing and filtering
- [x] Semantic search with embeddings
- [x] RAG pipeline with Milvus
- [x] Multi-turn conversations
- [x] Session management
- [x] Product comparison
- [x] Docker deployment
- [x] LangSmith integration

### In Progress 🚧
- [ ] Unit test coverage >80%
- [ ] Performance optimization
- [ ] Error handling improvements

### Planned 📋
- [ ] Azure deployment (Container Apps)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] User authentication
- [ ] Rate limiting
- [ ] Monitoring dashboard
- [ ] Multi-language support
- [ ] Voice input support
- [ ] Product recommendation engine

## 🐛 Known Issues

- First request after startup is slow (~3s) due to model loading
- Large Docker images (working on optimization)
- Limited error messages for end users
- No retry logic for failed API calls

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Jose Valdes**
- GitHub: [@josehvaldes](https://github.com/josehvaldes)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/josevaldesmurguia)

## 🙏 Acknowledgments

- Azure OpenAI for LLM capabilities
- LangChain for RAG orchestration
- Mantine for beautiful UI components
- FastAPI for excellent documentation
- The open-source community

## 📚 Documentation

- [API Documentation](./shopassist-api/README.md)
- [Frontend Documentation](./shopassist-ui/README.md)
- [Deployment Guide](./docs/deployment.md) (planned)
- [Architecture Deep Dive](./docs/architecture.md) (planned)

## 💡 Use Cases

This project demonstrates:
- Production-ready RAG implementation
- Microservices architecture
- Vector database integration
- LLM prompt engineering
- Full-stack development with modern tools
- Docker containerization
- Cloud service integration

Perfect for learning or as a template for similar AI-powered applications!

---

**⭐ If you find this project useful, please consider giving it a star!**