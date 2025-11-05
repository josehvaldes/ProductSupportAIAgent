import traceback
from typing import Dict, List, Optional
from shopassist_api.application.prompts.templates import PromptTemplates, TestPromptTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.services.intent_classifier import IntentClassifier
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
        self.intent_classifier = IntentClassifier(llm_service=llm_service)
        self.llm = llm_service
    
    async def generate_test_answer(self,
        query: str):
        """Generate answer for testing"""

        try:
            # Step 1: Process query
            cleaned_query, filters = self.query_processor.process_query(query)
            
            logger.info(f"Filters: {filters}. query: {cleaned_query}")

            messages = TestPromptTemplates.sample_prompt(
                    cleaned_query, "context", "history_text")
            # Step 6: Generate response
            llm_response = await self.llm.generate_response(messages)
            results = []  # Dummy results for testing

            return {
                "response": llm_response['response'],
                "sources": results,
                "query_type": "general_question",
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

    async def generate_dumb_answer(
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
        # Step 2: Retrieve relevant documents
        if query_type == 'product':

            categories = await self.retrieval.retrieve_top_categories(query, 1)
            if categories and len(categories) > 0:
                name = categories[0]['name']
                logger.info(f"  Extracted category filter: {name}")
                filters = {**filters, **{'category': name}}

            logger.info(f"  Final filters applied: {filters}")
            results = await self.retrieval.retrieve_products(
                cleaned_query,
                enriched=True,
                top_k=4, # reduce the number of products to retrieve
                filters=filters
            )
            context = self.context_builder.build_product_context(results)
        else:
            results = await self.retrieval.retrieve_knowledge_base(
                cleaned_query,
                top_k=3
            )
            context = self.context_builder.build_knowledge_base_context(results)
        
        logger.info(f"Retrieved {len(results)} results for query")
    
        response = f"NO LLM call: [{query}]: {context}"

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
        1. Process query (extract price filters)
        2. Classify intent
        3. Format conversation history 
        4. Handle different intents 
        4.1 Retrieve relevant documents
        4.2 Build prompt messages
        4.3 Build context
        5. Generate response with LLM
        6. Add citations
        
        Returns:
            Dict with response, sources, metadata
        """
        try:
            logger.info(f"Processing. Session: {session_id}, Query: {query}")
            
            # Step 1: Process query and get price filters
            cleaned_query, filters = self.query_processor.process_query(query)
            
            #step 2: Classify intent
            llm_query_type, confidence = await self.intent_classifier.classify(query)

            logger.info(f"Query type: {llm_query_type}, confidence {confidence} Filters: {filters}, query: {cleaned_query}")
            
            # Step 3: Format conversation history
            history_text = self._format_history(conversation_history)
            messages = []
            results = []
            # Step 4: Handle different query types
            match llm_query_type:
                case 'product_search':
                    logger.info("Handling product search intent")
                    messages, results = await self.handle_product_search(query, filters, history_text)
                case 'product_details':
                    logger.info("Handling product details intent")
                case 'product_comparison':
                    logger.info("Handling product comparison intent")
                case 'policy_question':
                    logger.info("Handling policy question intent")
                    messages, results = await self.handle_policy_question(query, history_text)
                case 'general_support':
                    logger.info("Handling general support intent")
                case 'chitchat':
                    logger.info("Handling chitchat intent")
                case 'out_of_scope':
                    logger.info("Handling out_of_scope intent")
                case _:
                    logger.info("Handling default/general intent")
                    messages, results = await self.handle_general_out_of_scope(query, history_text)

            
            # Step 5: Generate response
            logger.info(f"Generating LLM response for session: [{session_id}] with {len(messages)} messages")
            llm_response = await self.llm.generate_response(messages)

            logger.info(f"LLM response generated for session: [{session_id}] with {llm_response['tokens']} tokens, cost: {llm_response['cost']}")
            
            # Step 6: Format sources
            return {
                "response": llm_response['response'],
                "sources": results,
                "query_type": llm_query_type,
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
    
    async def handle_policy_question(self, query:str, history:str) -> tuple[List[Dict[str,str]], List[Dict]]:
        results = await self.retrieval.retrieve_knowledge_base(
            query,
            top_k=3
        )
        context = ""
        
        if not results:
            logger.warning("No results found for policy question")
            messages = PromptTemplates.no_results_prompt(query)
            results = []
        else:
            context = self.context_builder.build_knowledge_base_context(results)
            messages = PromptTemplates.policy_query_prompt(
                        query, context, history
                    )
        
        return messages, results
    
    async def handle_product_search(self, query:str, filters:Dict, history:str)-> tuple[List[Dict[str,str]], List[Dict]]:
        
        # Step 2: Retrieve relevant documents
        # retrieve top categories to enhance filters
        categories = await self.retrieval.retrieve_top_categories(query, 2)
        if categories and len(categories) > 0:
            category_names = []
            for cat in categories:
                logger.info(f"  Top category: {cat['name']}, score: {cat['distance']}")
                logger.info(f"  Extracted category filter: {cat['name']}")
                category_names.append(cat['name'])
                
            filters = {**filters, **{'categories': category_names}}
        
        logger.info(f"  Final filters applied: {filters}")

        results = await self.retrieval.retrieve_products(
            query,
            top_k=4, 
            filters=filters
        )
        context = self.context_builder.build_product_context(results)

        logger.info(f"Retrieved {len(results)} results for query")
        logger.info(f"Built context for query: {context}")
        messages = []
        # Step 3: Handle no results
        if not results:
            logger.warning("No results found for query")
            messages = PromptTemplates.no_results_prompt(query)
            results = []
        else:
            messages = PromptTemplates.product_query_prompt(
                query, context, history)
            
        return messages, results

    async def handle_product_details():
        pass

    async def handle_comparison():
        pass

    async def handle_general_support():
        pass

    async def handle_general_chitchat():
        pass
    
    async def handle_general_out_of_scope():
        pass

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
    
    async def health_check(self) -> dict:
        """Ping the service to check connectivity"""
        try:
            health = {}
            is_healthy = await self.llm.health_check()
            health['llm_service'] = "healthy" if is_healthy else "unhealthy"
            health['retrieval_service'] = await self.retrieval.health_check()
            return health
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False