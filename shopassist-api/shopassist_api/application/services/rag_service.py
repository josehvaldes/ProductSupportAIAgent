import traceback
from typing import Dict, List, Optional
from shopassist_api.application.prompts.templates import PromptTemplates, TestPromptTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.services.llm_sufficiency_builder import LLMSufficiencyBuilder
from shopassist_api.application.services.query_processor import QueryProcessor
from shopassist_api.application.services.retrieval_service import RetrievalService
from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)


class RAGService:
    """
    Orchestrates the entire RAG pipeline
    """
    
    def __init__(self,
                 llm_service: LLMServiceInterface,
                 nanolm_service: LLMServiceInterface,
                 retrieval_service: RetrievalService):
        self.retrieval = retrieval_service
        self.llm = llm_service
        self.nanolm = nanolm_service # Use nanolm for lightweight tasks
        self.sufficiency_builder = LLMSufficiencyBuilder(llm_service=nanolm_service)
        self.query_processor = QueryProcessor()
        self.context_builder = ContextBuilder()
        
    
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
                    "query_type_confidence": 0.5,
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
        query_type = "product_search"  if session_id == '1' else 'policy_question' # Dummy query type for testing
        
        logger.info(f"Query type: {query_type}, Filters: {filters}, query: {cleaned_query}")
        # Step 2: Retrieve relevant documents
        if query_type == 'product_search':

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
    
        response = f"NO LLM call: [{query}]:"

        return {
                "response": response,
                "sources": results,
                "query_type": query_type,
                "has_results": True,
                "filters_applied": filters,
                "metadata": {
                    "query_type_confidence": 0.5,
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
            
            history_text = self._format_history(conversation_history)
            # Step 1: Process query and get price filters
            cleaned_query, filters = self.query_processor.process_query(query)
            
            #step 2: Classify intent
            suffic_data = await self.sufficiency_builder.analyze_sufficiency(
                cleaned_query, history=history_text)
            
            llm_query_type = suffic_data.get('intent_query', 'general_support')
            confidence = float(suffic_data.get('confidence', 0.0))
            logger.info(f"Query type: {llm_query_type}, confidence {confidence} Filters: {filters}, query: {cleaned_query}")
            
            # Step 3: Format conversation history
            data = {
                "query": cleaned_query,
                "filters": filters,
                "history_text": history_text,
                "sufficiency_data": suffic_data
            }
            messages = []
            results = []
            # Step 4: Handle different query types
            match llm_query_type:
                case 'product_search':
                    logger.info("Handling product search intent")
                    messages, results = await self.handle_product_search(data)
                case 'product_details':
                    logger.info("Handling product details intent")
                    messages, results = await self.handle_product_details(data)
                case 'product_comparison':
                    logger.info("Handling product comparison intent")
                    messages, results = await self.handle_product_comparison(data)
                case 'policy_question':
                    logger.info("Handling policy question intent")
                    messages, results = await self.handle_policy_question(data)
                case 'general_support':
                    logger.info("Handling general support intent")
                    messages, results = await self.handle_general_support(data)
                case 'chitchat':
                    logger.info("Handling chitchat intent")
                    messages, results = await self.handle_chitchat(data)
                case 'out_of_scope':
                    logger.info("Handling out_of_scope intent")
                    messages, results = await self.handle_general_out_of_scope(data)
                case _:
                    logger.info("Handling default/general intent")
                    messages, results = await self.handle_general_out_of_scope(data)


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
                    "query_type_confidence": confidence,
                    "num_sources": len(results),
                    "tokens": llm_response['tokens'],
                    "cost": llm_response['cost']
                }
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            traceback.print_exc()
            raise
    

    async def handle_product_details(self, data:dict ) -> tuple[List[Dict[str,str]], List[Dict]]:
        """
        handle product details queries
        """
        logger.info("Checking context sufficiency for product details")
        
        history = data['history_text']
        filters = data['filters']
        query = data['query']

        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient']

        refined_query = sufficiency_data.get('query_retrieval_hint', '')
        refined_query = refined_query if refined_query else query
        
        logger.info(f"  Query: [{refined_query}] History: [{history}]")

        sufficient_reasoning = sufficiency_data['is_sufficient']
        if sufficient_reasoning.lower() == 'no':
            
            scope_retrieval_hint = sufficiency_data.get('scope_retrieval_hint', 'products')
            logger.info(f"  Retrieval scope hint: {scope_retrieval_hint}")
            
            # Step 2: Retrieve relevant documents
            results = await self.retrieval.retrieve_products(
                refined_query,
                top_k=1, # use the most relevant product 
                filters=filters
            )
            context = self.context_builder.build_product_context(results)
                
            logger.info(f"Retrieved {len(results)} results for query")
            logger.info(f"Built context for query: {context}")
            messages = []
            # Step 3: Handle no results
            if not results:
                logger.warning("No results found for product details query")
                messages = PromptTemplates.no_results_prompt(query)
                results = []
            else:
                messages = PromptTemplates.product_details_prompt(
                    query, context, history)
        else:
            results = []
            context = "No relevant products needed to answer."
            messages = PromptTemplates.product_details_prompt(
                    query, context, history)
            
        return messages, results

    async def handle_product_comparison(self, query:str, data:dict ) -> tuple[List[Dict[str,str]], List[Dict]]:
        """
        handle product comparison queries
        """

        logger.info("Checking context sufficiency for product details")
        
        history = data['history_text']
        filters = data['filters']
        query = data['query']

        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient']

        refined_query = sufficiency_data.get('query_retrieval_hint', '')
        refined_query = refined_query if refined_query else query
        
        logger.info(f"  Query: [{refined_query}] History: [{history}]")

        logger.warning("No results found for product comparison query")
        messages = PromptTemplates.no_results_prompt(refined_query)
        results = []
            
        return messages, results


    async def handle_general_support(self, data:dict) -> tuple[List[Dict[str,str]], List[Dict]]:
        """
        handle general support queries
        """

        history = data['history_text']
        query = data['query']

        sufficiency_data = data['sufficiency_data']
        refined_query = sufficiency_data.get('query_retrieval_hint', '')
        refined_query = refined_query if refined_query else query
        
        logger.info(f"  Query: [{refined_query}] History: [{history}]")
        
        results = await self.retrieval.retrieve_knowledge_base(
            refined_query,
            top_k=1
        )
        
        if not results:
            logger.warning("No results found for general support query")
            messages = PromptTemplates.no_results_prompt(query)
            results = []
        else:
            context = self.context_builder.build_knowledge_base_context(results)
            messages = PromptTemplates.general_prompt(
                        query, context, history
                    )
        
        return messages, results

    async def handle_chitchat(self, data:dict) -> tuple[List[Dict[str,str]], List[Dict]]:
        """
        handle chitchat queries. No retrieval
        """
        history = data['history_text']
        query = data['query']
        
        logger.warning("No results found for chitchat query")
        messages = PromptTemplates.general_prompt(query, history)
        results = []
    
        return messages, results

    async def handle_general_out_of_scope(self, query:str, history:str) -> tuple[List[Dict[str,str]], List[Dict]]:
        # handle out_of_scope queries. No retrieval        
        results = []
        
        logger.warning("No results found for out_of_scope query")
        messages = PromptTemplates.general_prompt(query, history)
        results = []
    
        return messages, results

    async def handle_policy_question(self, data:dict) -> tuple[List[Dict[str,str]], List[Dict]]:
        """ 
        Handle policy question queries
        """
        history = data['history_text']
        query = data['query']

        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient']
        
        refined_query = sufficiency_data.get('query_retrieval_hint', '')
        refined_query = refined_query if refined_query else query
        
        logger.info(f"  Query: [{refined_query}] History: [{history}]")

        if sufficient_reasoning.lower() == 'no':
            logger.info("Context insufficient for policy question")

            # Step 2: Retrieve relevant documents
            results = await self.retrieval.retrieve_knowledge_base(
                refined_query,
                top_k=2
            )
            
            if not results:
                logger.warning("No results found for policy question")
                messages = PromptTemplates.no_results_prompt(query)
                results = []
            else:
                context = self.context_builder.build_knowledge_base_context(results)
                messages = PromptTemplates.policy_query_prompt(
                            query, context, history
                        )
        else:
            results = []
            context = "No relevant products needed to answer."
            messages = PromptTemplates.product_query_prompt(
                    refined_query, context, history)
            
        return messages, results
    
    async def handle_product_search(self, query:str, data:dict)-> tuple[List[Dict[str,str]], List[Dict]]:
        """ 
        Handle product search queries
        """
        logger.info("Checking context sufficiency for product details")
        
        history = data['history_text']
        filters = data['filters']
        query = data['query']

        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient']

        refined_query = sufficiency_data.get('query_retrieval_hint', '')
        refined_query = refined_query if refined_query else query
        
        logger.info(f"  Query: [{refined_query}] History: [{history}]")

        if sufficient_reasoning.lower() == 'no':

            messages = []
            results = []
        
            # Step 2: Retrieve relevant documents
            # retrieve top categories to enhance filters
            categories = await self.retrieval.retrieve_top_categories(refined_query, 2)
            if categories and len(categories) > 0:
                category_names = []
                for cat in categories:
                    logger.info(f"  Top category: {cat['name']}, score: {cat['distance']}")
                    logger.info(f"  Extracted category filter: {cat['name']}")
                    category_names.append(cat['name'])
                    
                filters = {**filters, **{'categories': category_names}}
        
            logger.info(f"  Final filters applied: {filters}")
            results = await self.retrieval.retrieve_products(
                refined_query,
                top_k=4, 
                filters=filters
            )
            context = self.context_builder.build_product_context(results)
            logger.info(f"Retrieved {len(results)} results for query")
            logger.info(f"Built context for query: {context}")
            
            # Step 3: Handle no results
            if not results:
                logger.warning("No results found for query")
                messages = PromptTemplates.no_results_prompt(refined_query)
                results = []
            else:
                messages = PromptTemplates.product_query_prompt(
                    refined_query, context, history)
        else:
            results = []
            context = "No relevant products needed to answer."
            messages = PromptTemplates.product_query_prompt(
                    refined_query, context, history)
        return messages, results

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