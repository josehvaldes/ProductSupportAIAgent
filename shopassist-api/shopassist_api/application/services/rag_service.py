import traceback
from typing import Dict, List, Optional
from shopassist_api.application.prompts.templates import PromptTemplates, TestPromptTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.services.query_processor import QueryProcessor
from shopassist_api.application.services.retrieval_service import RetrievalService
from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface
from shopassist_api.logging_config import get_logger


logger = get_logger(__name__)


class RAGService:
    """
    Orchestrates the entire RAG pipeline
    """
    
    def __init__(self, llm_service: LLMServiceInterface,
                 retrieval_service: RetrievalService):
        self.retrieval = retrieval_service
        self.query_processor = QueryProcessor()
        self.context_builder = ContextBuilder()
        self.llm = llm_service
    
    async def generate_test_answer(self,
        query: str):
        """Generate answer for testing"""

        try:
            # Step 1: Process query
            cleaned_query, filters = self.query_processor.process_query(query)
            query_type = self.query_processor.classify_query_type(query)
            
            logger.info(f"Query type: {query_type}, Filters: {filters}. query: {cleaned_query}")

            messages = TestPromptTemplates.sample_prompt(
                    cleaned_query, "context", "history_text")
            print(f"Generated Messages: {messages}")
            # Step 6: Generate response
            llm_response = self.llm.generate_response(messages)
            print(f"LLM Response: {llm_response}")
            results = []  # Dummy results for testing

            return {
                "response": llm_response['response'],
                "sources": results,
                "query_type": query_type,
                "has_results": True,
                "filters_applied": filters,
                "metadata": {
                    "num_sources": len(results),
                    "tokens": llm_response['tokens'],
                    "cost": llm_response['cost']
                }
            }

        except Exception as e:
            logger.error(f"Error generating test answer: {e}")
            traceback.print_exc()
            raise

    async def generate_dump_answer(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        session_id: Optional[str] = None
    ) -> Dict:
        """Generate dump answer for testing"""

        # Step 1: Process query
        cleaned_query, filters = self.query_processor.process_query(query)
        query_type = self.query_processor.classify_query_type(query)
        
        logger.info(f"Query type: {query_type}, Filters: {filters}, query: {cleaned_query}")
        print(f"Processed query: {cleaned_query}, type: {query_type}, filters: {filters}")
        # Step 2: Retrieve relevant documents
        if query_type == 'product':
            results = await self.retrieval.retrieve_products(
                cleaned_query,
                enriched=True,
                #TODO uncomment below later
                top_k=2, # reduce the number of products to retrieve
                filters=filters # Currently not applying filters for products
            )
            context = self.context_builder.build_product_context(results)
        else:
            results = await self.retrieval.retrieve_knowledge_base(
                cleaned_query,
                top_k=3
            )
            context = self.context_builder.build_knowledge_base_context(results)
        
        print(f"Retrieved {len(results)} results for query")
        logger.info(f"Retrieved {len(results)} results for query")
        logger.info(f"Built context for query: {context}")
    
        response = f"NO LLM call: [{query}]: {context}"
        query_type = "product"

        return {
                "response": response,
                "sources": results,
                "query_type": query_type,
                "has_results": True,
                "filters_applied": filters,
                "metadata": {
                    "num_sources": len(results),
                    "tokens": 0,
                    "cost": 0
                }
            }

    async def generate_answer(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Generate an answer using RAG pipeline
        
        Pipeline:
        1. Process query (extract filters, classify type)
        2. Retrieve relevant documents
        3. Build context
        4. Generate response with LLM
        5. Add citations
        
        Returns:
            Dict with response, sources, metadata
        """
        try:
            logger.info(f"Processing. Session: {session_id}, Query: {query}")
            
            # Step 1: Process query
            cleaned_query, filters = self.query_processor.process_query(query)
            query_type = self.query_processor.classify_query_type(query)
            
            logger.info(f"Query type: {query_type}, Filters: {filters}, query: {cleaned_query}")
            print(f"Processed query: {cleaned_query}, type: {query_type}, filters: {filters}")
            # Step 2: Retrieve relevant documents
            if query_type == 'product':
                results = await self.retrieval.retrieve_products(
                    cleaned_query,
                    #TODO uncomment below later
                    top_k=2, # reduce the number of products to retrieve
                    filters=filters # Currently not applying filters for products
                )
                context = self.context_builder.build_product_context(results)
            else:
                results = await self.retrieval.retrieve_knowledge_base(
                    cleaned_query,
                    top_k=3
                )
                context = self.context_builder.build_knowledge_base_context(results)
            
            print(f"Retrieved {len(results)} results for query")
            logger.info(f"Retrieved {len(results)} results for query")
            logger.info(f"Built context for query: {context}")
            # Step 3: Handle no results
            if not results:
                logger.warning("No results found for query")
                print("No results found for query")
                messages = PromptTemplates.no_results_prompt(query)
                llm_response = self.llm.generate_response(messages)
                
                return {
                    "response": llm_response['response'],
                    "sources": [],
                    "query_type": query_type,
                    "has_results": False,
                    "metadata": {
                        "tokens": llm_response['tokens'],
                        "cost": llm_response['cost']
                    }
                }
            
            # Step 4: Format conversation history
            history_text = self._format_history(conversation_history)
            print(f"Formatted conversation history: {history_text}")
            logger.info(f"Formatted conversation history for session {session_id}")
            # Step 5: Build prompt
            if query_type == 'product':
                messages = PromptTemplates.product_query_prompt(
                    query, context, history_text
                )
            else:
                messages = PromptTemplates.policy_query_prompt(
                    query, context, history_text
                )
            
            print(f"Generated Messages for LLM: {messages}")
            logger.info(f"Generated messages for LLM for session {session_id}")
            # Step 6: Generate response
            llm_response = self.llm.generate_response(messages)
            print(f"LLM Response: {llm_response["response"]}")
            print(f"LLM Response: {llm_response["tokens"]} tokens, Cost: {llm_response["cost"]}")
            logger.info(f"LLM response generated for session {session_id} with {llm_response['tokens']} tokens, cost: {llm_response['cost']}")
            # Step 7: Format sources
            #sources = self._format_sources(results, query_type)
            return {
                "response": llm_response['response'],
                "sources": results,
                "query_type": query_type,
                "has_results": True,
                "filters_applied": filters,
                "metadata": {
                    "num_sources": len(results),
                    "tokens": llm_response['tokens'],
                    "cost": llm_response['cost']
                }
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            traceback.print_exc()
            raise
    
    def _format_history(
        self,
        conversation_history: Optional[List[Dict]]
    ) -> str:
        """Format conversation history for prompt"""
        if not conversation_history:
            return ""
        
        history_parts = []
        for msg in conversation_history[-5:]:  # Last 5 turns
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_parts.append(f"{role.title()}: {content}")
        
        return "\n".join(history_parts)
    