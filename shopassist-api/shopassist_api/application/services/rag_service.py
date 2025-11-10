import json
import traceback
from typing import Dict, List, Optional
from shopassist_api.application.prompts.templates import PromptTemplates, TestPromptTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.services.formaters import FormatterUtils
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
    
    TOP_K_PRODUCTS = 2
    TOP_K_KB_ARTICLES = 2
    TOP_K_CATEGORIES = 2

    def __init__(self,
                 llm_service: LLMServiceInterface,
                 nanolm_service: LLMServiceInterface,
                 retrieval_service: RetrievalService):
        self.retrieval = retrieval_service
        self.llm = llm_service
        self.nanolm = nanolm_service # Use nanolm for lightweight tasks
        self.sufficiency_builder = LLMSufficiencyBuilder(llm_service=llm_service)
        self.query_processor = QueryProcessor()
        self.context_builder = ContextBuilder()
        
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
                top_k=RAGService.TOP_K_PRODUCTS, # reduce the number of products to retrieve
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
        try:
            logger.info(f"Processing. Session: {session_id}, Query: {query}")
            
            # Step 1: Format conversation history
            history_text = FormatterUtils.format_history(conversation_history)

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

            # Step 6: Format sources
            return {
                "response": llm_response['response'],
                "sources": results,
                "query_type": llm_query_type,
                "has_results": True,
                "filters_applied": filters,
                "metadata": {
                    "query_type_confidence": sufficiency.get('confidence', 0.0),
                    "num_sources": len(results),
                    "tokens": llm_response['tokens'],
                    "cost": llm_response['cost'],
                    "products": product_sources,
                    "turn_index": len(conversation_history) + 1 if conversation_history else 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            traceback.print_exc()
            raise
    
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
            logger.info(f"  Query: [{refined_query}]")
        
            # retrieve top categories to enhance filters
            categories = await self.retrieval.retrieve_top_categories(refined_query, RAGService.TOP_K_CATEGORIES) 
            if categories and len(categories) > 0:
                category_names = []
                for cat in categories:
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
            context = "No relevant products needed to answer."
            logger.info("Context sufficient, skipping retrieval.")
            messages = PromptTemplates.product_query_prompt(
                    query, context, history)
        return messages, results

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
            context = "No documents retieved to answer"
            messages = PromptTemplates.product_query_prompt(
                    query, context, history)
            
        return messages, results

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
            context = "No relevant products needed to answer."
            messages = PromptTemplates.product_details_prompt(
                    query, context, data['history_text'])
            
        return messages, results

    async def handle_product_comparison(self, data:dict ) -> tuple[List[Dict[str,str]], List[Dict]]:
        """
        handle product comparison queries
        """
        logger.info("Checking context sufficiency for product comparison")
        
        query = data['query']

        sufficiency_data = data['sufficiency_data']
        sufficient_reasoning = sufficiency_data['is_sufficient'].lower()

        if sufficient_reasoning == 'no':
            
            refined_query = sufficiency_data.get('query_retrieval_hint', '')
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
                messages = PromptTemplates.product_details_prompt(
                    query, context, data['history_text'])
        else:
            results = []
            context = "No relevant products needed to answer."
            messages = PromptTemplates.product_details_prompt(
                    query, context, data['history_text'])
            
        return messages, results


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