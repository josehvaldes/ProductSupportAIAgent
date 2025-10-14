# Shop Assistant API

AI-Powered Product Knowledge & Support Agent API

## Project Structure

```
shopassist_api/
├── main.py              # FastAPI app entry point
├── api/                 # API routes and endpoints
│   ├── chat.py         # Chat endpoints
│   └── health.py       # Health check
├── ai/                  # AI/ML modules
│   ├── agents/         # AI agents
│   ├── models/         # ML models and LLM clients
│   ├── embeddings/     # Vector embeddings
│   ├── retrieval/      # RAG components
│   └── prompts/        # Prompt templates
├── core/               # Core business logic
│   └── config.py       # Configuration settings
└── utils/              # Utilities
    └── helpers.py      # Helper functions
```

## Setup

1. **Environment Setup**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your API keys and configuration
   ```

2. **Install Dependencies**
   ```bash
   # Create conda environment (from project root)
   conda env create -f ../environment.yml
   conda activate saaivenv
   
   # Install project in development mode
   pip install -e .
   ```

3. **Run Development Server**
   ```bash
   # Make sure conda environment is activated
   conda activate saaivenv
   
   # Run development server
   python dev_server.py
   
   # Or using uvicorn directly
   uvicorn shopassist_api.main:app --reload
   ```

4. **Run Tests**
   ```bash
   # Make sure conda environment is activated
   conda activate saaivenv
   
   # Run tests
   pytest
   ```

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/chat` - Chat with the AI assistant
- `GET /api/v1/chat/history/{conversation_id}` - Get chat history

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options.

Key configurations:
- **OpenAI/Azure OpenAI**: For LLM capabilities
- **Azure AI Search**: For product search and retrieval
- **Azure Storage**: For document and data storage

## Development

The API is built with:
- **FastAPI**: Modern, fast web framework
- **OpenAI/Azure OpenAI**: Language model integration
- **Azure AI Services**: Search and cognitive services
- **Pydantic**: Data validation and settings management