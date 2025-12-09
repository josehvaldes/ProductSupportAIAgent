import traceback
from typing import Dict, List, Optional
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
import time
from shopassist_api.application.prompts.templates import PromptTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.services.session_manager import SessionManager
from shopassist_api.application.services.formaters import FormatterUtils
from shopassist_api.application.services.llm_sufficiency_builder import LLMSufficiencyBuilder
from shopassist_api.application.services.query_processor import QueryProcessor
from shopassist_api.application.services.retrieval_service import RetrievalService
from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface
from shopassist_api.application.settings.config import settings
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)


class RAGService:
    """
    Orchestrates the entire RAG pipeline
    """
    
    TOP_K_PRODUCTS = 3
    TOP_K_KB_ARTICLES = 2
    TOP_K_CATEGORIES = 3

    def __init__(self,
                 llm_service: LLMServiceInterface,
                 nanolm_service: LLMServiceInterface,
                 retrieval_service: RetrievalService,
                 session_manager: SessionManager
                 ):
        self.retrieval = retrieval_service
        self.llm = llm_service
        self.nanolm = nanolm_service # Use nanolm for lightweight tasks
        self.session_manager = session_manager
        self.sufficiency_builder = LLMSufficiencyBuilder(llm_service=nanolm_service)
        self.query_processor = QueryProcessor()
        self.context_builder = ContextBuilder()
        
        
    async def generate_dumb_answer(
        self,
        query: str,
        session_id: Optional[str] = None,
        top_k: int = 3
    ) -> Dict:
        """Generate dump answer for testing"""

        # Step 1: Process query
        cleaned_query, filters = self.query_processor.process_query(query)
        query_type = "product_search"  if session_id == '58ca3bbb-1fbc-4cfa' else 'policy_question' # Dummy query type for testing
        
        logger.info(f"Query type: {query_type}, Filters: {filters}, query: {cleaned_query}")
        # Step 2: Retrieve relevant documents
        if query_type == 'product_search':

            categories = await self.retrieval.retrieve_top_categories(query, top_k)
            
            if categories and len(categories) > 0:
                category_names = []
                for cat in categories:
                    if cat['score'] > settings.threshold_category_similarity:
                        category_names.append(cat['name'])
                    
                filters = {**filters, **{'categories': category_names}}

            logger.info(f"  Final filters applied: {filters}")
            results = await self.retrieval.retrieve_products(
                cleaned_query,
                enriched=True,
                top_k=top_k, # reduce the number of products to retrieve
                filters=filters
            )
            context = self.context_builder.build_product_context(results)
        else:
            results = await self.retrieval.retrieve_knowledge_base(
                cleaned_query,
                top_k=top_k
            )
            context = self.context_builder.build_knowledge_base_context(results)
        
        logger.info(f"Retrieved {len(results)} results for query")
    
        response = f"NO LLM call: [{query}]:"

        return {
                "response": response,
                "sources": results,
                "query_type": "product_comparison",
                "has_results": True,
                "filters_applied": filters,
                "metadata": {
                    "query_type_confidence": 0.5,
                    "num_sources": len(results),
                    "tokens": 0,
                    "cost": 0
                }
            }

    @traceable(name="rag.generate_answer", tags=["rag", "entry-point"], metadata={"version": "1.0"})
    async def generate_answer(
        self,
        user_id:str,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Generate an answer using RAG pipeline
        
        Pipeline:
        1. Format conversation history 
        2. Process query (extract price filters)
        3. Classify intent and sufficiency        
        4. Handle different intents 
        4.1 Retrieve relevant documents
        4.2 Build prompt messages
        4.3 Build context
        5. Generate response with LLM
        6. Add sources and metadata
        
        Returns:
            Dict with response, sources, metadata
        """
        run = get_current_run_tree()
        start_time = time.time()
        try:
            logger.info(f"Processing. Session: {session_id}, Query: {query}")
            
            # Step 1: Format conversation history
            history = await self.session_manager.get_conversation_history(session_id=session_id)

            history_text = FormatterUtils.format_message_history(history)

            # Step 2: Process query and get price filters
            cleaned_query, filters = self.query_processor.process_query(query)
            
            #step 3: Classify intent
            sufficiency = await self.sufficiency_builder.analyze_sufficiency(
                cleaned_query, history=history_text)

            logger.info(f"Sufficiency data: {sufficiency}")
            
            data = {
                "query": cleaned_query,
                "filters": filters,
                "history_text": history_text,
                "sufficiency_data": sufficiency
            }
            
            llm_query_type = sufficiency.get('intent_query', 'general_support')
            
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
            
            product_sources = FormatterUtils.build_product_sources(llm_query_type,results)

            # Step 6: Save user and assistant messages
            await self.session_manager.add_message(
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=query,
            )

            metadata = {
                    "query_type_confidence": sufficiency.get('confidence', 0.0),
                    "num_sources": len(results),
                    "tokens": llm_response['tokens'],
                    "cost": llm_response['cost'],
                    "products": product_sources,
                    "turn_index": len(history) + 1 if history else 1
                }
            
            await self.session_manager.add_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=llm_response['response'],
                metadata=metadata
            )

            total_time = time.time() - start_time
            logger.info(f"RAG pipeline completed in {total_time*1000:.2f} ms for session: [{session_id}]")
            if run:
                run.add_metadata({
                    "total_latency_ms": total_time * 1000,
                    "intent": llm_query_type,
                    "docs_used": len(results)
                })
            else:
                logger.warning("No active LangSmith run found to add metadata.")

            # return
            return {
                "response": llm_response['response'],
                "sources": results,
                "query_type": llm_query_type,
                "has_results": True,
                "filters_applied": filters,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            traceback.print_exc()
            raise
    
    @traceable(name="rag.handle_product_search", tags=["rag", "intent"], metadata={"version": "1.0"})
    async def handle_product_search(self, data:dict)-> tuple[List[Dict[str,str]], List[Dict]]:
        """ 
        Handle product search queries
        """
        logger.info("Checking context sufficiency for product details")
        
        query = data['query']
        history = data['history_text']
        
        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient'].lower()
        
        logger.info(f"Sufficiency reasoning: {sufficiency_data}")
        
        if sufficient_reasoning == 'no':
            logger.info("Context insufficient for product search")
            messages = []
            results = []
            filters = data['filters']
            refined_query = sufficiency_data.get('query_retrieval_hint', '')
            refined_query = refined_query if refined_query else query
            logger.info(f" Search Query: [{refined_query}]")
        
            # retrieve top categories to enhance filters
            categories = await self.retrieval.retrieve_top_categories(refined_query, RAGService.TOP_K_CATEGORIES) 
            if categories and len(categories) > 0:
                category_names = []
                for cat in categories:
                    if cat['score'] > settings.threshold_category_similarity:
                        category_names.append(cat['name'])
                    
                filters = {**filters, **{'categories': category_names}}
        
            logger.info(f"  Filters applied: {filters}")
            results = await self.retrieval.retrieve_products(
                refined_query,
                top_k=RAGService.TOP_K_PRODUCTS, 
                filters=filters
            )
            
            logger.info(f"Retrieved {len(results)} results for query")
            # Handle no results
            if not results:
                logger.warning("No results found for query")
                messages = PromptTemplates.no_results_prompt(query)
                results = []
            else:
                context = self.context_builder.build_product_context(results)
                messages = PromptTemplates.product_query_prompt(
                    query, context, history)
        else:
            results = []
            context = ""
            logger.info("Context sufficient, skipping retrieval.")
            messages = PromptTemplates.product_query_prompt(
                    query, context, history)
        return messages, results


    @traceable(name="rag.handle_policy_question", tags=["rag", "intent"], metadata={"version": "1.0"})
    async def handle_policy_question(self, data:dict) -> tuple[List[Dict[str,str]], List[Dict]]:
        """ 
        Handle policy question queries
        """
        history = data['history_text']
        query = data['query']
        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient'].lower()
        
        if sufficient_reasoning == 'no':
            refined_query = sufficiency_data.get('query_retrieval_hint', '')
            refined_query = refined_query if refined_query else query
            logger.info(f"Context insufficient for policy question.  Query: [{refined_query}]")

            #Retrieve relevant documents
            results = await self.retrieval.retrieve_knowledge_base(
                refined_query,
                top_k=RAGService.TOP_K_KB_ARTICLES # retrieve top knowledge base articles
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
            context = ""
            messages = PromptTemplates.product_query_prompt(
                    query, context, history)
            
        return messages, results

    @traceable(name="rag.handle_product_details", tags=["rag", "intent"], metadata={"version": "1.0"})
    async def handle_product_details(self, data:dict ) -> tuple[List[Dict[str,str]], List[Dict]]:
        """
        handle product details queries
        """
        logger.info("Checking context sufficiency for product details")
        
        query = data['query']
        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient'].lower()

        if sufficient_reasoning == 'no':
            
            scope_retrieval_hint = sufficiency_data.get('scope_retrieval_hint', 'products')
            logger.info(f"  Retrieval scope hint: {scope_retrieval_hint}")
            
            refined_query = sufficiency_data.get('query_retrieval_hint', '')
            refined_query = refined_query if refined_query else query
            
            logger.info(f"  Query: [{refined_query}]")    

            # Retrieve relevant documents
            results = await self.retrieval.retrieve_products(
                refined_query,
                top_k=RAGService.TOP_K_PRODUCTS, # use the most relevant product 
                filters=data['filters']
            )
            
            messages = []
            logger.info(f"Retrieved {len(results)} results for query")            
            # Handle no results
            if not results:
                logger.warning("No results found for product details query")
                messages = PromptTemplates.no_results_prompt(query)
                results = []
            else:
                context = self.context_builder.build_product_context(results)
                #TODO Use a different prompt for product details
                messages = PromptTemplates.product_details_prompt(
                    query, context, data['history_text'])
        else:
            results = []
            context = ""
            messages = PromptTemplates.product_details_prompt(
                    query, context, data['history_text'])
            
        return messages, results

    @traceable(name="rag.handle_product_comparison", tags=["rag", "intent"], metadata={"version": "1.0"})
    async def handle_product_comparison(self, data:dict ) -> tuple[List[Dict[str,str]], List[Dict]]:
        """
        handle product comparison queries
        """
        logger.info("Checking context sufficiency for product comparison")
        
        query = data['query']

        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient'].lower()

        if sufficient_reasoning == 'no':
            
            refined_query = sufficiency_data['query_retrieval_hint']
            refined_query = refined_query if refined_query else query
            logger.info(f"  Query: [{refined_query}]")    
            filters = data['filters']

            # Retrieve relevant documents
            results = await self.retrieval.retrieve_products(
                refined_query,
                top_k=RAGService.TOP_K_PRODUCTS, # use the most relevant product 
                filters=filters
            )
            
            messages = []
            logger.info(f"Retrieved {len(results)} results for query")            
            # Handle no results
            if not results:
                logger.warning("No results found for product details query")
                messages = PromptTemplates.no_results_prompt(query)
                results = []
            else:
                context = self.context_builder.build_product_context(results)
                #TODO Use a different prompt for product comparison
                messages = PromptTemplates.product_comparison_prompt(
                    query, context, data['history_text'])
        else:
            results = []
            context = ""
            messages = PromptTemplates.product_comparison_prompt(
                    query, context, data['history_text'])
            
        return messages, results

    @traceable(name="rag.handle_general_support", tags=["rag", "intent"], metadata={"version": "1.0"})
    async def handle_general_support(self, data:dict) -> tuple[List[Dict[str,str]], List[Dict]]:
        """
        handle general support queries
        """
        sufficiency_data = data['sufficiency_data']
        refined_query = sufficiency_data.get('query_retrieval_hint', '')
        refined_query = refined_query if refined_query else data['query']
        
        logger.info(f" Handle General Query: [{refined_query}]")
        
        results = await self.retrieval.retrieve_knowledge_base(
            refined_query,
            top_k=1
        )
        
        if not results:
            logger.warning("No results found for general support query")
            messages = PromptTemplates.no_results_prompt(data['query'])
            results = []
        else:
            context = self.context_builder.build_knowledge_base_context(results)
            messages = PromptTemplates.general_prompt(
                        data['query'], context, data['history_text']
                    )
        
        return messages, results

    @traceable(name="rag.handle_chitchat", tags=["rag", "intent"], metadata={"version": "1.0"})
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

    @traceable(name="rag.handle_general_out_of_scope", tags=["rag", "intent"], metadata={"version": "1.0"})
    async def handle_general_out_of_scope(self, query:str, history:str) -> tuple[List[Dict[str,str]], List[Dict]]:
        # handle out_of_scope queries. No retrieval        
        results = []
        
        logger.warning("No results found for out_of_scope query")
        messages = PromptTemplates.general_prompt(query, history)
        results = []
    
        return messages, results

    async def health_check(self) -> dict:
        """Ping the service to check connectivity"""
        try:
            health = {}
            is_llm_healthy = await self.llm.health_check()
            
            retrieval_healthy = await self.retrieval.health_check()
            is_retrieval_healthy = "healthy" if retrieval_healthy["is_healthy"] == "healthy" else "unhealthy"
            health = {
                "is_healthy": "is_healthy" if is_llm_healthy and is_retrieval_healthy == "healthy" else "unhealthy",
                "llm_service": "healthy" if is_llm_healthy else "unhealthy",
                "retrieval_service": retrieval_healthy
            }
            return health 
        except Exception as e:
            logger.error(f"Rag Service Health check failed: {e}")
            traceback.print_exc()
            return False