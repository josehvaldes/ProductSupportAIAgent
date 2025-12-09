# Query processing & intent classification

** api/chat.py
  - chat_message

** application/services/rag_services.py
  - RagService:generate_answer
  - RagService:handle_product_search
  - RagService:handle_product_comparison
  - RagService:handle_general_support
  - RagService:handle_chitchat
  - RagService:handle_general_out_of_scope
  - RagService:handle_product_details
  - RagService:handle_policy_question

** application/services/process_query
  - QueryProcessor: process_query

** application/services/llm_sufficiency_builder.py
  - LLMSufficiencyBuilder:analyze_sufficiency
  

# Retrieval operations (Milvus searches)

** application/services/retrieval_services.py
  - RetrievalService:retrieve_top_categories
  - RetrievalService:retrieve_products
  - RetrievalService:retrieve_knowledge_base
  - RetrievalService:hybrid_search


** infrastructure/services/milvus_service.py
  - MilvusService:insert_products
  - MilvusService:insert_knowledge_base
  - MilvusService:insert_categories
  - MilvusService:search_products
  - MilvusService:search_knowledge_base
  - MilvusService:search_categories

# Context building
** application/prompts/templates.py
  - ContextAnalysisPrompts:context_analysis_prompt

** application/services/context_builder.py
  - ContextBuilder:build_product_context
  - ContextBuilder:build_knowledge_base_context


# LLM generation calls

** infrastructure/services/openai_llm_service.py
  - OpenAILLMService:generate_response
  - OpenAILLMService:streaming_response

** infrastructure/services/openai_embedding_service.py
  - OpenAIEmbeddingService:generate_embedding
  - OpenAIEmbeddingService:generate_embedding_batch

** infrastructure/services/transformers_embedding_service
  - TransformersEmbeddingService:generate_embedding
  - TransformersEmbeddingService:generate_embedding_batch


# Session management operations

** application/services/session_manager.py
  - SessionManager:create_session
  - SessionManager:get_conversation_history
  

# Cache management
** infrastructure/services/redis_cache_service.py
  - RedisCacheService:get






** api/products.py
   - search_products_general

** api/session.py
   - get_history

** api/search.py
   - vector_search