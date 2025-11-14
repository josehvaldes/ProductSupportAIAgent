# ShopAssist Development Log

**Project:** AI-Powered Product Knowledge & Support Agent  
**Duration:** 6 weeks (Oct 14, 2025 - Nov 25, 2025)  
**Tech Stack:** React + Mantine, FastAPI, Azure Cosmos DB, Milvus, Azure OpenAI, Gemma

---

## Week 1: Foundation & Data Preparation
**Goal:** Infrastructure deployed, dataset ready, project structure initialized  
**Dates:** Oct 14 - Oct 20, 2025

### Day 1 - Monday, Oct 14, 2025
**Today's Focus:** Azure setup and project initialization

**Completed:**
- [x] Created Azure resource group `rg-shopassistai-test-01`
- [x] Provisioned Azure Cosmos DB account
- [x] Created Cosmos DB containers (products, sessions, feedback)
- [x] Set up Azure OpenAI service
- [-] Deployed Milvus on Azure Container Instances (Scripts are ready, waiting for data to deploy the VM and avoid unnecessary costs)
- [x] Created GitHub repository with initial structure
- [x] Initialized FastAPI project with basic folder structure
- [x] Created React app with Mantine UI

**Technical Decisions:**
- Cosmos DB partition key: Using `/category` for products container (efficient category-based queries)
- Mantine version: 8.3.4 with default theme
- Python version: 3.11 for FastAPI
- Poetry as packing and delivery tool
- Conda as virtual environment and package management

**Challenges & Solutions:**
- *Document any issues you encounter here*
- Refactor generated code by Claude

**Learnings:**
- *Key insights from today's work*
- provide clear instructions to claude in github copilot

**Next Steps:**
- [ ] Generate product dataset (200 products)
- [ ] Write knowledge base documents

**Time Invested:** 4 hours

---

### Day 2 - Tuesday, Oct 15, 2025
**Today's Focus:** Product dataset creation

**Completed:**
Decomposed Tasks:
1. [X] Search and download product dataset from Kaggle (30 min)
   - Target: Electronics/e-commerce dataset with 500+ products
   - Must have: name, description, price, category, specs

2. [X] Clean and filter dataset to 200 products (1 hour)
   - Select: 80 electronics, 60 home & garden, 60 fashion
   - Validate: all required fields present
   - Standardize: price format, category names

3. [X] Create data transformation script (1.5 hours)
   - Convert to Cosmos DB document format
   - Generate product IDs
   - Add token counting function
   - Implement smart chunking (>512 tokens)
   - Track chunking statistics
   - Save as JSON file with chunk metadata

4. [X] Upload to Cosmos DB products container (1 hour)
   - Write upload script (Python + azure-cosmos SDK)
   - Test with 10 products first
   - Bulk upload all 200 products
   - Verify in Azure Portal

5. [X] Create sample product queries for testing (30 min)
   - Query by category
   - Query by price range
   - Get product by ID
   - Document queries for later use

**Technical Decisions:**
- Choose dataset domain: electronics
- Define Data models for CosmosDB, Milvus, and Azure Search AI 
- Choose strategies to chunk large vector text
- User RBAC to access cosmosDB

**Challenges & Solutions:**
- dataset had more information than required. Parsing and transformation script was needed

**Learnings:**
- control-plane roles have to be added by CLI, not in Portal

**Next Steps:**
- [ Write Knowledge base documents ] 

**Time Invested:** 4 hours

---

### Day 3 - Wednesday, Oct 16, 2025
**Today's Focus:** Knowledge base documents creation

**Completed:**
1. [X] Generate knowledge base documents with GPT-4 (1 hour)
   - Return policy, shipping, warranty, FAQ

2. [X] Review and customize generated content (1.5 hours)
   - Make policies consistent
   - Add specific details (email, phone)
   - Ensure realistic for electronics

3. [X] Format and save documents (30 min)
   - Create markdown files
   - Add document metadata headers
   - Save to knowledge_base/ folder

4. [X] Run through semantic splitter (30 min)
   - Chunk each document
   - Verify chunk quality
   - Save chunk statistics

5. [X] Create document mapping file (30 min)
   - Map doc_id to document type
   - Track chunk counts per document
   - Prepare for embedding in Week 2

6. [X] Move python scripts logic to Azure Data Factory 
   - Analyze need to use Adf pipelines
   - If needed:
     - Create ADF repository
     - Upload products data to blob containers
     - Review activities needed in the pipelines
     - Implement pipeline if needed

**Technical Decisions:**
- Generated base documents with GPT-4, then customized for electronics domain
- 5 documents created: Return Policy, Shipping, Warranty, Size Guide, FAQ
- Total words: ~2,500
- Semantic chunking: 12.5% overlap, avg 400 tokens/chunk
- Total chunks: ~15-20 for knowledge base

**Metrics:**
- Knowledge base documents: 5
- Total Q&A pairs in FAQ: 30
- Total knowledge base chunks: X
- Average chunk size: X tokens

**Challenges & Solutions:**
- Reduce costs for ADF execution.
- Split large Data flow activities into smaller steps to reduce the workload
- stop debug mode and shrink the cluster size.


**Learnings:**
- learn techniques to reduce ADF costs
- ADF benefits as orchestraitor

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** 8 hours

---

### Day 4 - Thursday, Oct 17, 2025
**Today's Focus:** FastAPI backend structure

**Completed:**
1. [X] Set up FastAPI project structure (1 hour)
   - Create folder structure: app/, services/, models/, api/routes/
   - Initialize main.py with FastAPI app
   - Check CORS middleware configuration
   - Set up environment variables (.env file)
   - update requirements.txt or pyproject.toml
   - Test Frontend access to API

2. [X] Create data models with Pydantic (1.5 hours)
   - ProductModel (for Cosmos DB)
   - ChunkModel (for Milvus/Azure AI)
   - ChatRequestModel (user message input)
   - ChatResponseModel (AI response output)
   - SessionModel (conversation tracking)
   
3. [X] Implement Cosmos DB service (1.5 hours)
   - Create product_service.py
   - Initialize Cosmos DB client
   - Implement get_product_by_id()
   - Implement search_products_by_category()
   - Implement search_products_by_price_range()
   - Test queries with sample data

4. [X] Set up Azure OpenAI client (1 hour)
   - Create openai_service.py
   - Initialize Azure OpenAI client
   - Test connection with simple completion
   - Test embedding generation
   - Document token usage
   
5. [X] Create basic API endpoints (1 hour)
   - POST /api/chat/message (placeholder)
   - GET /api/products/search (working with Cosmos)
   - GET /api/products/{product_id} (working with Cosmos)
   - GET /api/health (health check)
   - Test with Postman/Thunder Client

**Technical Decisions:**
- Project structure: Clean architecture with services layer
- Pydantic v2 for data validation
- Async/await for all database operations
- Environment-based configuration (dev/prod)

**Challenges & Solutions:**
- Adjust code to clean architecture in phyton apps
- Evaluate Dependency injection and its implementation and compare it with traditional .Net implementations

**Learnings:**
- Review how to implemement dependency injection in Python and FastAPI

**Next Steps:**
- [ ] Create React frontend structure (Day 5)
- [ ] Connect frontend to backend API
- [ ] Test end-to-end product retrieval flow

**Time Invested:** 6 hours

---

### Day 5 - Friday, Oct 18, 2025
**Today's Focus:** React frontend setup

**Completed:**
1. [X] Set up React project structure with Mantine (1 hour)
   - Verify Mantine 8.3.4 installation
   - Configure MantineProvider in App.tsx
   - Set up theme configuration (colors, fonts)
   - Create folder structure: components/, pages/, services/, types/
   - Install additional dependencies (axios, react-router-dom)

2. [X] Create API service layer (1 hour)
   - Create api/client.ts with axios configuration
   - Set up base URL pointing to FastAPI backend
   - Implement error handling interceptors
   - Create api/products.ts with product endpoints:
     * getProducts()
     * getProductById(id)
     * searchProducts(query, filters)
   - Test API connection with health endpoint

3. [X] Build basic layout components (1.5 hours)
   - Create Layout.tsx (AppShell with header, main content)
   - Create Header.tsx with app logo and title
   - Create ChatContainer.tsx (will hold chat messages)
   - Create ProductGrid.tsx (will display product cards)
   - Implement responsive design (mobile-first)

4. [X] Create ProductCard component (1 hour)
   - Design card with Mantine Card component
   - Display: image, name, price, category, rating
   - Add hover effects
   - Make it clickable (navigate to product details)
   - Handle missing images gracefully
   - Add "Add to Cart" button (placeholder)

5. [X] Create basic Chat UI components (1.5 hours)
   - Create ChatMessage.tsx (user message + AI response)
   - Create ChatInput.tsx (text input + send button)
   - Create ChatBubble.tsx (styled message bubbles)
   - Add typing indicator component
   - Style with Mantine components (Textarea, Button, Paper)

6. [X] Connect frontend to backend (1 hour)
   - Test fetching products from API
   - Display products in ProductGrid
   - Implement loading states (Loader component)
   - Implement error states (Alert component)
   - Add mock chat message to test UI
   - Verify CORS is working properly

7. [X] Add logging to the API
	- Implement logging in main.py
	- Update .env

**Technical Decisions:**
- Mantine AppShell for main layout structure
- Axios for HTTP requests with interceptors
- React Router for navigation (optional for MVP)
- Component-based architecture (atomic design principles)
- TypeScript interfaces for type safety
- Add logging for API

**Challenges & Solutions:**
- Use React with mantine

**Learnings:**
- ReactJS hooks and state management
- Mantine components

**Next Steps:**
- [ ] Integrate chat API endpoint (Week 2)
- [ ] Add product filtering UI
- [ ] Implement search bar

**Time Invested:** 8 hours

---

### Day 6 - Saturday, Oct 19, 2025
**Today's Focus:** Data ingestion and testing

1. [X] Test end-to-end product retrieval flow (1.5 hours)
   - Start both backend and frontend servers
   - Test fetching all products
   - Test searching by category
   - Test searching by price range
   - Test getting single product by ID
   - Verify data displays correctly in UI
   - Document any bugs found

2. [X] Refine ProductGrid and filtering (2 hours)
   - Add category filter dropdown (Mantine Select)
   - Add price range slider (Mantine RangeSlider)
   - Add search bar for product name/description
   - Implement filter logic (call backend API with params)
   - Test all filter combinations
   - Handle empty results gracefully

3. [X] Improve error handling and user feedback (1 hour)
   - Add error boundaries in React
   - Improve loading states (skeleton loaders)
   - Add toast notifications for errors (Mantine Notifications)
   - Test with backend offline scenario
   - Add retry logic for failed requests

4. [X] Add product detail view (1.5 hours)
   - Create ProductDetail page/modal
   - Show full description, all specs
   - Display larger image
   - Add "Back to products" navigation
   - Test routing/navigation

5. [X] Polish UI and responsiveness (1 hour)
   - Test on mobile viewport
   - Fix any layout issues
   - Improve spacing and typography
   - Add hover effects and transitions
   - Test in different browsers

6. [X] Document API endpoints and frontend structure (1 hour)
   - Update README with setup instructions
   - Document environment variables needed
   - Add screenshots of current UI
   - List completed features
   - Note known issues/TODOs


**Technical Decisions:**
- Add filtering UI before RAG pipeline (better UX foundation)
- Use Mantine Notifications for user feedback
- Implement skeleton loaders for better perceived performance
- Product detail as modal

**Challenges & Solutions:**
- building a good loking UI 

**Learnings:**
- How to use mantine components and hooks

**Next Steps:**
- [ ] Week 1 wrap-up (Day 7)
- [ ] Prepare data for Week 2 embedding
- [ ] Start Week 2: Embedding service

**Time Invested:** 6 hours

---

### Day 7 - Sunday, Oct 20, 2025
**Today's Focus:** Week 1 wrap-up and documentation

**Completed:**
1. [X] Clean up codebase (1.5 hours)
   - Remove unused imports and commented code
   - Standardize code formatting (Prettier/Black)
   - Add missing type hints (Python) and types (TypeScript)
   - Fix any linting warnings
   - Organize imports consistently
   - Add docstrings to key functions

2. [X] Write comprehensive README.md (2 hours)
   - Project overview and goals
   - Architecture diagram (text/ASCII art for now)
   - Tech stack list with versions
   - Setup instructions:
     * Prerequisites (Node.js, Python, Azure account)
     * Environment variables needed
     * Installation steps (backend + frontend)
     * Running the application
   - API endpoints documentation
   - Project structure explanation
   - Screenshots of current UI
   - Known limitations
   - Roadmap for remaining weeks

3. [-] Document Week 1 achievements (Postpone)
   - Fill in Week 1 Summary in DEVLOG.md:
     * List all shipped features
     * Document key technical decisions
     * Calculate metrics (products in DB, lines of code, etc.)
     * List blockers resolved
     * Key learnings
   - Take screenshots of:
     * Product grid with filters
     * Product detail view
     * Azure Portal (Cosmos DB, OpenAI services)
     * API response examples

4. [-] Create demo/presentation material (Postpone)
   - Record short screen recording (2-3 min) showing:
     * Product browsing
     * Filtering by category/price
     * Product detail view
   - Create architecture diagram (draw.io, Excalidraw, or Mermaid)
   - Prepare "elevator pitch" for the project
   - Update GitHub repo description

5. [X] Review and organize project files (45 min)
   - Verify .gitignore is complete (no secrets committed)
   - Organize data files into proper folders
   - Clean up any test/temporary files
   - Ensure all scripts are documented
   - Check that .env.example is up to date

6. [ ] Plan Week 2 in detail (1 hour)
   - Review Week 2 tasks from architecture doc
   - Break down Day 8 tasks (embedding service)
   - Verify Azure OpenAI quota/limits
   - Calculate embedding costs for 200 products
   - Prepare Milvus deployment checklist
   - List any dependencies to install
   - Identify potential blockers

7. [X] Calculate and document metrics (30 min)
   - Count lines of code (backend + frontend)
   - Check Azure costs so far
   - Count API endpoints created
   - Measure response times for current endpoints
   - Document product catalog stats:
     * Total products in Cosmos DB
     * Products by category
     * Average price by category
     * Chunk statistics



**Technical Decisions:**
- Week 1 focused on foundation - no AI/ML yet (as planned)
- Successfully integrated Cosmos DB, FastAPI, React + Mantine
- Deferred Milvus deployment to Week 2 (cost optimization)
- Added logging and error handling early (good practice) 

**Challenges & Solutions:**
- Create meaninfull documentation. Solve with Claude.ai
- Create architecture diagrams. Solved with excalidraw tool

**Learnings:**
- collect lines of code in Ubuntu


**Time Invested:** 2 hours

---

### 📊 Week 1 Summary

**Shipped:**
- ✅ Azure infrastructure (Cosmos DB, OpenAI service, Resource Group)
- ✅ Product dataset (200 electronics products from Kaggle)
- ✅ Knowledge base documents (5 documents, ~2,500 words)
- ✅ FastAPI backend with Cosmos DB integration
- ✅ React + Mantine frontend with product browsing
- ✅ End-to-end product retrieval and filtering

**Key Technical Decisions:**
1. Chose Cosmos DB over PostgreSQL (Azure-native, NoSQL flexibility)
2. Chose Mantine over Tailwind (component library, faster UI dev)
3. Semantic chunking with 12.5% overlap for long descriptions
4. Deferred Milvus deployment until Week 2 (cost + need embeddings first)
5. Clean architecture pattern for backend services

**Metrics:**
- Products in Cosmos DB: 200
- Knowledge base documents: 5
- Knowledge base chunks: ~15-20
- Lines of code (backend): ~1790
- Lines of code (frontend): 937
- Azure services deployed: 3 (Cosmos DB, OpenAI, Resource Group)
- API endpoints: 4 (health, products searchs, search)
- Average product token count: ~XXX
- Products requiring chunking: ~XX%

**Blockers Resolved:**
- RBAC for Cosmos DB (solved via Azure CLI)
- CORS configuration for FastAPI ↔ React
- Dataset filtering to 200 relevant products
- ADF cost management (optimized pipeline execution)

**Learnings:**
- Azure RBAC: control-plane vs data-plane roles
- Semantic chunking is better than hard token limits
- Mantine components accelerate UI development
- FastAPI dependency injection patterns
- React hooks and state management best practices


**Total Time This Week:** 44 hours

**Week 2 Preview:**
Core RAG pipeline implementation - embedding service, Milvus integration, Azure OpenAI connection

---

## Week 2: Core RAG Pipeline
**Goal:** Basic question-answering working via API  
**Dates:** Oct 21 - Oct 27, 2025

### Day 8 - Monday, Oct 21, 2025
**Today's Focus:** Embedding service implementation

**Completed:**
1. [X] Set up embedding service module (1.5 hours)
   - Create Infrastructure/services/OpenAIEmbeddingService and TransformersEmbeddingService for Open AI and Sentence Transformers
   - Create the service_interfaces.py module for Interfaces
   - Initialize Azure OpenAI embedding client
   - Create function: generate_embedding(text: str) -> List[float]
   - Create function: generate_embeddings_batch(texts: List[str]) -> List[List[float]]
   - Add error handling and retry logic
   - Test with sample product descriptions

2. [X] Prepare data for embedding (1 hour)
   - Load product chunks from Day 2 (products_for_embedding.json)
   - Load knowledge base chunks from Day 3
   - Validate chunk text quality (no empty strings, proper format)
   - Create combined dataset for embedding
   - Calculate total embedding cost estimate
   - Document chunk statistics

3. [X] Implement batch embedding generation (2 hours)
   - Create script: scripts/generate_embeddings.py
   - Process products in batches (100 at a time)
   - Process knowledge base chunks in batches
   - Add progress tracking (tqdm or logging)
   - Save embeddings to JSON files:
     * product_embeddings.jsonl
     * knowledge_base_embeddings.jsonl
   - Include metadata: chunk_id, product_id, embedding, timestamp
   - Use Sentence Transformers for testing 

4. [X] Test embedding quality (1 hour)
   - Test similarity between related products
   - Test similarity between question and FAQ chunks
   - Verify embedding dimensions (1536)
   - Check for NaN or invalid values
   - Document sample similarity scores
   - Test batch vs single embedding consistency

5. [X] Create data models for vector storage (1 hour)
   - Update shopassist-api/application/models/chunk.py with embedding field
   - Create VectorChunk model for Milvus
   - Add validation for embedding dimensions
   - Document schema for Milvus collection
   - Prepare sample data for Day 9

6. [X] Document embedding strategy and costs (30 min)
   - Calculate actual embedding costs later. After Sentence Transformers is replaced by OpenAI
   - Document token usage per chunk type
   - Record total chunks embedded
   - Note any API errors or retries
   - Document embedding generation time
   - Update DEVLOG with metrics

7. [X] Test embedding with Azure OpenAI text-embedding-3-small
   - update scripts/generate_embeddings.py to use the openai_embedding_service.py module
   - calculate costs and execution time

**Technical Decisions:**
- Use Open AI embedding model. Embedding dimension: 1536 (text-embedding-3-small)
- Use sentence-transformers/multi-qa-mpnet-base-dot-v1. Embedding dimension: 768 ()
- Batch size: 10 documents per request

**Challenges & Solutions:**
- Implement scripts and generate the correct data

**Learnings:**
- python ellipsis in Fields
- write and load jsonl files

**Next Steps:**
- [ ] Create Milvus collections
- [ ] Build vector indexing pipeline
- [ ] Chunk product descriptions

**Time Invested:** 6 hours

---

### Day 9 - Monday, Oct 27, 2025
**Today's Focus:** Milvus collection setup

**Completed:**
1. [X] Deploy Milvus on Azure Container Instances (1.5 hours)
   - Review Milvus deployment scripts from Day 1
   - Deploy Milvus standalone container to Azure
   - Configure networking and ports (19530, 9091)
   - Verify Milvus is accessible from local machine
   - Access Attu (Milvus web UI) at port 9091
   - Document connection details (host, port)

2. [X] Create Milvus collection schemas (1 hour)
   - Create script: scripts/create_milvus_collections.py
   - Define products_collection schema:
     * Fields: id, product_id, text, embedding[1536], chunk_index, 
       total_chunks, category, price, brand
     * Primary key: id
     * Vector index: HNSW (Hierarchical Navigable Small World)
   - Define knowledge_base_collection schema:
     * Fields: id, doc_id, text, embedding[1536], doc_type
     * Primary key: id
     * Vector index: HNSW
   - Create collections in Milvus
   - Verify collections exist

3. [X] Create Milvus service layer (1.5 hours)
   - Create app/services/milvus_service.py
   - Initialize Milvus connection
   - Implement insert_products(products: List[Dict])
   - Implement insert_knowledge_base(chunks: List[Dict])
   - Implement search_products(query_embedding, top_k, filters)
   - Implement search_knowledge_base(query_embedding, top_k)
   - Add error handling and logging

4. [X] Ingest product embeddings into Milvus (1 hour)
   - Create script: scripts/ingest_to_milvus.py
   - Load product_embeddings.json
   - Transform to Milvus format
   - Batch insert (1000 records at a time)
   - Verify insertion count
   - Create indexes on collection
   - Document ingestion statistics

5. [X] Ingest knowledge base embeddings (30 min)
   - Load knowledge_base_embeddings.json
   - Transform to Milvus format
   - Insert into knowledge_base_collection
   - Verify insertion count
   - Create indexes

6. [X] Test vector search functionality (1 hour)
   - Create test script: scripts/test_milvus_search.py
   - Test product search with sample queries:
     * "laptop for video editing"
     * "wireless headphones"
     * "kitchen appliances"
   - Test knowledge base search:
     * "what is the return policy"
     * "shipping information"
   - Verify top-k results are relevant
   - Measure search latency
   - Document search performance

7. [X] Verify data integrity and create health checks (30 min)
   - Count total vectors in each collection
   - Verify all product_ids have chunks
   - Check for duplicate entries
   - Test collection statistics
   - Create health check endpoint for Milvus
   - Document collection metrics

**Technical Decisions:**
- Use localhost instance of Milvus for testing.
- Enable attu service for milvus instance

**Challenges & Solutions:**
- Use a custom docker-compose.yml file instead of an external one when deploying the milvus_setup.bicep file
  Solution: add the yml text in bicep. Postpone this change when deploying in azure

**Learnings:**
- How to add texts in bicep scripts.

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** 4 hours

---

### Day 10 - Tuesday, Oct 28, 2025
**Today's Focus:** Document chunking and ingestion

**Completed:**
1. [X] Create retrieval service layer (1.5 hours)
   - Create app/services/retrieval_service.py
   - Implement retrieve_products(query: str, top_k: int, filters: dict)
   - Implement retrieve_knowledge_base(query: str, top_k: int)
   - Implement hybrid_search(query: str, use_vector: bool, use_keyword: bool)
   - Add result deduplication logic (multiple chunks from same product)
   - Add result ranking and scoring
   - Test retrieval with sample queries

2. [X] Implement query preprocessing (1 hour)
   - Create app/services/query_processor.py
   - Extract filters from natural language (price, category, brand)
   - Query expansion (synonyms, related terms)
   - Query classification (product vs policy)
   - Normalize query text
   - Test with various query formats

3. [X] Build result aggregation logic (1.5 hours)
   - Combine multiple chunks from same product
   - Calculate relevance scores
   - Merge vector and keyword search results
   - Implement re-ranking algorithms
   - Handle empty results gracefully
   - Format results for LLM consumption

4. [X] Create context builder for RAG (1 hour)
   - Create app/services/context_builder.py
   - Format retrieved documents into context string
   - Add metadata (source, product ID, price)
   - Implement context truncation (max tokens)
   - Prioritize most relevant chunks
   - Add citation tracking

5. [X] Implement retrieval API endpoints (1 hour)
   - Add POST /api/search/vector (vector search)
   - Add POST /api/search/hybrid (hybrid search)
   - Add GET /api/search/test (test various queries)
   - Document request/response formats
   - Add input validation
   - Test with Postman

6. [X] Test end-to-end retrieval flow (1 hour)
   - Test product queries with filters
   - Test policy/FAQ queries
   - Test edge cases (no results, ambiguous queries)
   - Measure retrieval latency
   - Verify result relevance
   - Document retrieval statistics

7. [X] Create retrieval evaluation script (1 hour)
   - Create scripts/evaluate_retrieval.py
   - Define test query set (20 queries)
   - Calculate precision@k, recall@k
   - Measure mean reciprocal rank (MRR)
   - Document retrieval quality metrics
   - Identify areas for improvement

**Technical Decisions:**
- Use dependencies injection for MilvusServices.
- Write query processors in application/services module.
- deprecate code in application/ai module.

**Challenges & Solutions:**
- Fix dependecy injection error for scripts outside FastAPI

**Learnings:**
- Milvus API and queries.
- Milvus metrics and distance meaning

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** 3 hours

---

### Day 11 - Wednesday, Oct 29, 2025
**Today's Focus:** LLM service and prompt engineering for RAG responses

**Completed:**
1. [X] Create LLM service layer (1.5 hours)
   - Create LLMServiceInterface in application/interfaces/service_interfaces
   - Create OpenAILLMService.py in infrastructure/services/
   - Initialize Azure OpenAI chat completion client
   - Implement generate_response(prompt: str, context: str, history: List)
   - Implement streaming_response() for better UX
   - Add token counting and cost tracking
   - Handle API errors and retries
   - Test with sample prompts

2. [X] Design and implement prompt templates (2 hours)
   - Create application/prompts/templates.py
   - Design system prompt for product assistant
   - Create prompt template for product queries
   - Create prompt template for policy queries
   - Create prompt template for product comparison
   - Add few-shot examples for better responses
   - Include formatting instructions (markdown, lists)
   - Test different prompt variations for testing

3. [X] Build RAG orchestration service (1.5 hours)
   - Create app/services/rag_service.py
   - Orchestrate: retrieve → build context → generate response
   - Implement query routing (product vs policy)
   - Add response post-processing
   - Include source citations
   - Handle edge cases (no results, unclear query)
   - Test end-to-end RAG flow

4. [X] Implement response generation API (1 hour)
   - Update POST /api/chat/message endpoint
   - Accept user message and session_id
   - Call RAG service
   - Return response with sources
   - Add streaming support (Server-Sent Events)
   - Document request/response format
   - Test with Postman

5. [X] Add conversation history management (1 hour)
   - Store conversations in Cosmos DB sessions container
   - Implement get_conversation_history(session_id)
   - Implement save_message(session_id, role, content)
   - Limit history to last N turns (5-10)
   - Format history for LLM context
   - Test multi-turn conversations

6. [X] Create prompt evaluation framework (1 hour)
   - Create scripts/evaluate_prompts.py
   - Define test scenarios (10-15 queries)
   - Test different prompt variations
   - Measure response quality (manual review)
   - Measure response relevance
   - Document best-performing prompts
   - Identify hallucinations or errors

7. [X] Test complete RAG pipeline (1 hour)
   - Test product discovery queries
   - Test specification questions
   - Test policy questions
   - Test multi-turn conversations
   - Test edge cases (no results, ambiguous)
   - Measure end-to-end latency
   - Document response quality

**Technical Decisions:**
- Use GPT-4-mini as LLM
- Implement dependecy injection for OpenAI implementation
- Refactor CosmosDB implementation and rename the interface to RepositoryServiceInterface
- Refactor FastAPI routes according to standards
- Follow DRY practices to handle Azure credentials
- Clean old generated files.

**Challenges & Solutions:**
- testing the prompts and analyze the results with a Basic prompt and later use the complex solution.
- 

**Learnings:**
- RLock vs Lock for multithreading
- better ways to handle azure credentials.

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** 6 hours

---

### Day 12 - Thursday, Oct 30, 2025
**Today's Focus:** Frontend-backend chat integration and testing.

**Completed:**
1. [X] Create chat API service in frontend (1 hour)
   - Create src/services/api/chat.ts
   - Implement sendMessage(message: string, sessionId?: string)
   - Implement getChatHistory(sessionId: string)
   - Add types for chat messages and responses
   - Handle streaming responses (optional)
   - Add error handling
   - Test API calls with mock data

2. [X] Update ChatContainer component (1.5 hours)
   - Connect to chat API service
   - Display message history
   - Show user messages and AI responses
   - Add loading state (typing indicator)
   - Handle errors gracefully
   - Auto-scroll to latest message
   - Store session_id in state/localStorage

3. [X] Enhance ChatInput component (1 hour)
   - Send message on Enter key
   - Disable input while processing
   - Clear input after sending
   - Add character limit indicator
   - Handle empty messages
   - Show send button loading state
   - Add keyboard shortcuts

4. [X] Create product source display component (1 hour)
   - Create ProductSource.tsx component
   - Display product cards from AI response sources
   - Show relevance scores
   - Make products clickable (open detail view)
   - Format pricing and key features
   - Add "View Product" buttons
   - Test with different response types

5. [X] Add session management (1 hour)
   - Generate and persist session_id
   - Store session in localStorage
   - Clear session button (new conversation)
   - Display session info (optional)
   - Handle session expiration
   - Test session persistence across page reloads

6. [X] Implement response formatting (1 hour)
   - Parse markdown in AI responses
   - Format bullet points and lists
   - Handle code blocks (if any)
   - Add syntax highlighting for product names/prices
   - Linkify URLs
   - Test with various response formats

7. [X] End-to-end testing and polish (1.5 hours)
   - Test complete user flow:
     * User sends query
     * AI responds with products
     * User clicks product
     * Multi-turn conversation
   - Test error scenarios
   - Polish UI transitions and animations
   - Add loading skeletons
   - Optimize performance
   - Document any bugs found

**Technical Decisions:**
- Add a new ChatContainerExt component
- Reuse ProductGrid
- Remove Product format and let and API return raw products
- Add a new /dumpmeessage endpoint for testing. Let the endpoint use a new Dump method that uses local milvus for searchs

**Challenges & Solutions:**
- Build a usefull UI. Use mantine components, and generated UI code

**Learnings:**
- Build UI components with Mantine

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** 4 hours

---

### Day 13 - Friday, Oct 31, 2025
**Today's Focus:** wrap-up, testing, optimization, and documentation

**Completed:**
1. [X] Comprehensive end-to-end testing (1.5 hours)
   - Test all 7 key scenarios from architecture doc:
     * Product discovery ("laptop for video editing under $1500")
     * Specification query ("Does MacBook have 16GB RAM?")
     * Product comparison ("Compare MacBook vs Dell XPS")
     * Policy question ("What's your return policy?")
     * Out of stock handling (test with unavailable product)
     * Multi-turn conversation (3-5 turn dialogue)
     * Escalation scenario (order cancellation request)
   - Document test results for each scenario
   - Record response times
   - Note any issues or edge cases

2. [X] Performance optimization (1.5 hours)
   - Measure current response latency (end-to-end)
   - Identify bottlenecks (embedding, retrieval, LLM)
   - Optimize Milvus search parameters (ef, nprobe)
   - Implement result caching for common queries
   - Optimize frontend rendering
   - Test improvements and document gains: 
   - Update performance metrics

3. [X] Error handling and edge cases (1 hour)
   - Improve Health Checks
   - Test with malformed queries
   - Test with very long messages (>500 chars)
   - Test with empty/whitespace-only messages
   - Test with special characters
   - Test API error scenarios (service down)
   - Test session expiration
   - Verify all errors show user-friendly messages
   

4. [X] Response quality evaluation (1 hour)
   - Run evaluation script from Day 11
   - Review 8 responses for:
     * Factual accuracy
     * Relevance to query
     * Formatting quality
     * Citation correctness
   - Identify hallucinations or errors
   - Document quality metrics
   - Note areas for prompt improvement

5. [X] Code cleanup and documentation (1.5 hours)
   - Remove unused code and imports
   - Add missing docstrings
   - Update API documentation (Swagger)
   - Document prompt templates
   - Add inline comments for complex logic
   - Update README with Week 2 features
   - Create troubleshooting section

**Technical Decisions:**
- Use Singleton pattern for Azure open AI clients
- Use Singleton pattern for sentence transformer model
- 

**Challenges & Solutions:**
- Estimate costs and prepare reports. The solution is running basic tests and print the results for manual analysis

**Learnings:**
- How to implement class based vs Module based singleton pattern in python

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### 📊 Week 2 Summary

**Shipped:**
- 
- 
- 

**Key Technical Decisions:**
1. 
2. 
3. 

**Metrics:**
- Total embeddings generated: ___
- Average retrieval latency: ___ ms
- Milvus collection size: ___ MB
- Test queries answered: ___

**Blockers Resolved:**
- 

**Learnings:**
- 

**Total Time This Week:** ___ hours

**Week 3 Preview:**
Intent classification, context management, frontend integration

---

## Week 3: Intent & Context Management
**Goal:** Multi-turn conversations working with web interface  
**Dates:** Oct 28 - Nov 3, 2025

### Day 15 - Monday, Oct 28, 2025
**Today's Focus:** Formal intent classification system 

1. [X] Define clear intent categories (1 hour)
   - Define clear intent categories:
      product_search - Finding products by features/needs
      product_details - Asking about specific product specs
      product_comparison - Comparing multiple products
      policy_question - Return/shipping/warranty queries
      general_support - How-to, troubleshooting
      chitchat - Greetings, off-topic
      out_of_scope - Order management, account issues
   - Create intent examples (10 per category)
   - Document intent routing rules

2 [X] Implement intent classifier (2 hours)
   - Create app/services/intent_classifier.py
   - Option A: Prompt-based classification (use LLM)
      Design classification prompt
      Parse LLM response to intent enum
      Add confidence scoring
   - Add fallback to general_support for low confidence
   - Test with sample queries

3 [X] Add intent-based routing (1.5 hours)
   - Update rag_service.py to use intent classifier
   - Create specialized handlers per intent:
      handle_product_search()
      handle_product_details()
      handle_comparison()
      handle_policy_question()
   - Adjust retrieval strategy per intent
   - Customize prompts per intent
   - Test routing logic

4 [X] Create evaluation dataset (1 hour)
   - Create scripts/integration_intent_tests.json
   - queries across all intent types
   - Include edge cases (ambiguous, multi-intent)
   - Label ground truth intents
   - Add intent confusion matrix examples

5 [X] Test and evaluate intent accuracy (1.5 hours)
   - Create scripts/evaluate_intent_classifier.py
   - Run classifier on test dataset
   - Calculate accuracy, precision, recall per intent
   - Identify misclassification patterns
   - Document results in DEVLOG
   - Target: >85% accuracy

6 [X] Add intent to API response (30 min)
   - Update ChatResponse model with detected_intent field
   - Include confidence score
   - Log intents for analytics
   - Display intent in frontend (optional, for debugging)

7 [X] Frontend: Intent-based UI hints (30 min)

   - Show different placeholders based on previous intent
      After product search: "Want to compare products?"
      After policy question: "Any other questions?"

   - Add quick action buttons per intent
   - Test user experience improvements
 
**Technical Decisions:**
- Use intfloat/e5-large-v2 model for category classification
- use the top 2 categories for vector search
- use different prompts for different intented queries
- Use LLM to classify intent queries


**Challenges & Solutions:**
- find cost effective solutions to category classification mismatches. Solution: use an better model for taxonomy classification

**Learnings:**
- Different models can be used for different purposes
- Specific class for Asynchrouns calls to Azure Open AI

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** 8 hours

---

### Day 16 - Tuesday, Nov 11, 2025
**Today's Focus:** Context manager and session storage

**Completed:**
- [X] Design Session Data Model 
- [X] Create SessionManager Service 
- [X] Implement Preference Extraction Logic 
- [X] Add Redis Caching Layer 
- [X] Update RAG Service to Use Context 
- [X] Update API Endpoints for sessions management 
- [X] Test Multi-Turn Conversations 
- [X] Documentation updated



**Technical Decisions:**
- use Redis cache container
- Separate the session endpoints in a new API Route
- Use dependecy injection and Singleton caching for Redis
- Retake the use of pydantic objects for sessions
- branch session manager to a new branch

**Challenges & Solutions:**
- write integration tests for all new endpoints. Solutions, User copilot

**Learnings:**
- How to serialize and convert pydantic object

**Next Steps:**
- [ ] Advanced Query Processing & Retrieval Polish
- [ ] 

**Time Invested:** 4 hours

---

### Day 17 - Wednesday, Nov 12, 2025
**Today's Focus:** Advanced Query Processing & Retrieval Polish

**Completed:**
- [X] Query Preprocessing Enhancement 
	- Price filtering
- [X] Multi-Strategy Retrieval Router (1.5 hours)
- [X] Advanced Milvus Filtering (1 hour)
     Category filtering
- [X] Result Post-Processing & Ranking (1 hour)
- [X] Streaming Response Implementation (1.5 hours)
- [X] Add Query Suggestions (1 hour)
- [X] Testing & Documentation (1.5 hours)

**Technical Decisions:**
- Add a full_embedding field in the Categories collection 
- Implement a cosine similatiry score that combines category and full_category embeddings
- Add more complex queries to the test set

**Challenges & Solutions:**
- Review several alternatives of price and category filtering. Choose the RegExp for prices and cosine similarity for categories.
- Exclude other product fields from filtering for simplicity purposes

**Learnings:**
- How to make cosine similatiry with different vector and weight them into a single score

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 18 - Thursday, Nov 13, 2025
**Today's Focus:** Product comparison logic

**Completed:**
- [X] Design Comparison Data Model
- [X] Build Comparison Retrieval Logic
- [X] Implement Comparison Table Generation
- [X] Generate natural language comparison and recommendation
- [X] Implement Comparison API Endpoint
- [X] Integrate Comparison into RAG Flow
- [X] Test Comparison End-to-End


**Technical Decisions:**
- Simplify comparison logic to retrieve products, and send a query to the LLM

**Challenges & Solutions:**
- 

**Learnings:**
- reuse current code to simply process

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** 2 hours

---

### Day 19 - Friday, Nov 14, 2025
**Today's Focus:** Chat interface component (Mantine)

**Completed:**
- [X] Clean up ChatContainerExt component
- [X] Improve message display 
- [X] Add error handling UI 
- [X] Users can start fresh conversations
- [] Add session management UI 
- [] Final tests and polish UI


**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 20 - Saturday, Nov 2, 2025
**Today's Focus:** Product card display

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 21 - Sunday, Nov 3, 2025
**Today's Focus:** Frontend-backend integration

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### 📊 Week 3 Summary

**Shipped:**
- 
- 
- 

**Key Technical Decisions:**
1. 
2. 
3. 

**Metrics:**
- Multi-turn conversations handled: ___
- Intent classification accuracy: ___%
- Average context window size: ___ messages
- UI components built: ___

**Blockers Resolved:**
- 

**Learnings:**
- 

**Total Time This Week:** ___ hours


### Week 4: Model Analysis & Cost Optimization

**Goal:** Cost analysis complete, realistic model comparison documented

**Completed:**
- [X] Analyzed Gemma 7B deployment options
- [X] Calculated breakeven point: 31,000 requests/day
- [X] Documented why GPT-41-mini is optimal for <1,000 req/day
- [X] Created cost comparison dashboard
- [X] Analyze Gemma-2b factibility.

**Key Finding:**
For low-volume applications (<1,000 requests/day), modern LLM APIs (GPT-4.1-mini, Claude Haiku) are 15-300× cheaper than self-hosting open-source models.
The history and sufficiency uanalysis required more complex model. The requirements exceed Gemm-2b-it capabilities for how.

**Deliverables:**
- Cost analysis document: cost_analysis.dm (included in documentation/)
- Architecture decision record: Why we use GPT-4.1-mini

**Technical decisions:
- Stick to Azure Open AI models
- Reduce scope of the project discarding gemma-7b implementation
- Evaluate if low cost and uncritical tasks like greetings or chitchat can be done with gemma-2b-it.


**Week 5 Preview:**
Evaluation framework, metrics dashboard, automated testing

---

## Week 5: Evaluation & Analytics
**Goal:** Metrics dashboard live, automated evaluation running  
**Dates:** Nov 11 - Nov 17, 2025

### Day 29 - Monday, Nov 11, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 30 - Tuesday, Nov 12, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 31 - Wednesday, Nov 13, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 32 - Thursday, Nov 14, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 33 - Friday, Nov 15, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 34 - Saturday, Nov 16, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 35 - Sunday, Nov 17, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### 📊 Week 5 Summary

**Shipped:**
- 
- 
- 

**Key Technical Decisions:**
1. 
2. 
3. 

**Metrics:**
- Test queries evaluated: ___
- Factual accuracy: ___%
- Retrieval precision: ___%
- Average response time: ___ ms
- Thumbs up rate: ___%

**Blockers Resolved:**
- 

**Learnings:**
- 

**Total Time This Week:** ___ hours

**Week 6 Preview:**
Polish, deployment, documentation, demo video

---

## Week 6: Polish & Deployment
**Goal:** Production deployment, comprehensive documentation, demo ready  
**Dates:** Nov 18 - Nov 25, 2025

### Day 36 - Monday, Nov 18, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 37 - Tuesday, Nov 19, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 38 - Wednesday, Nov 20, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 39 - Thursday, Nov 21, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 40 - Friday, Nov 22, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 41 - Saturday, Nov 23, 2025
**Today's Focus:** 

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### Day 42 - Sunday, Nov 24, 2025
**Today's Focus:** Final review and launch preparation

**Completed:**
- [ ] 
- [ ] 
- [ ] 

**Technical Decisions:**
- 

**Challenges & Solutions:**
- 

**Learnings:**
- 

**Next Steps:**
- [ ] 
- [ ] 

**Time Invested:** ___ hours

---

### 📊 Week 6 Summary

**Shipped:**
- 
- 
- 

**Key Technical Decisions:**
1. 
2. 
3. 

**Metrics:**
- GitHub stars: ___
- Demo video views: ___
- Blog post reads: ___
- Portfolio site visits: ___

**Blockers Resolved:**
- 

**Learnings:**
- 

**Total Time This Week:** ___ hours

---

## 🎉 Project Completion - Nov 25, 2025

### Final Metrics

**Technical:**
- Total products in catalog: ___
- Total embeddings: ___
- Average query latency: ___ ms
- Factual accuracy: ___%
- System uptime: ___%
- Total API calls: ___
- Azure monthly cost: $___

**Development:**
- Total time invested: ___ hours
- Lines of code: ___
- Commits: ___
- Issues opened/closed: ___/___
- Documentation pages: ___

**Portfolio:**
- Live demo URL: ___
- GitHub repo: ___
- Blog post URL: ___
- Video demo URL: ___

### Key Achievements

1. 
2. 
3. 
4. 
5. 

### Most Valuable Learnings

1. **Technical:**
   - 
   - 
   - 

2. **Process:**
   - 
   - 
   - 

3. **Career:**
   - 
   - 
   - 

### What I Would Do Differently

1. 
2. 
3. 

### Next Steps

- [ ] Apply to AI Engineer positions
- [ ] Share project on LinkedIn
- [ ] Post to Reddit/HackerNews
- [ ] Create presentation for portfolio
- [ ] Plan next portfolio project

---

## Quick Reference

### Useful Commands
```bash
# Start development servers
cd backend && uvicorn main:app --reload
cd frontend && npm run dev

# Deploy to Azure
az webapp up --name shopassist-api --resource-group shopassist-rg

# Run tests
pytest tests/ -v
npm test

# Check costs
az consumption usage list --start-date 2025-10-14 --end-date 2025-10-21
```

### Important Links
- Azure Portal: https://portal.azure.com
- GitHub Repo: [YOUR_REPO_URL]
- Live Demo: [YOUR_DEMO_URL]
- Milvus Dashboard: [YOUR_MILVUS_URL]:9091
- Cosmos DB: [YOUR_COSMOS_URL]

### Key Contacts
- Mentor/Advisor: [NAME]
- Azure Support: [TICKET_URL]
- Community Discord: [DISCORD_LINK]

---

**Legend:**
- ✅ Completed
- 🚧 In Progress
- 🚫 Blocked
- 📝 Need to Document
- 🐛 Bug Found
- 💡 Idea/Enhancement

