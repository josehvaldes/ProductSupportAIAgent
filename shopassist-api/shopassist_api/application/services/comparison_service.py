import traceback
from typing import Dict, List, Optional
from shopassist_api.application.prompts.templates import PromptTemplates
from shopassist_api.application.services.context_builder import ContextBuilder
from shopassist_api.application.services.session_manager import SessionManager
from shopassist_api.application.services.formaters import FormatterUtils
from shopassist_api.application.services.llm_sufficiency_builder import LLMSufficiencyBuilder
from shopassist_api.application.services.query_processor import QueryProcessor
from shopassist_api.application.services.retrieval_service import RetrievalService
from shopassist_api.application.interfaces.service_interfaces import LLMServiceInterface, RepositoryServiceInterface
from shopassist_api.logging_config import get_logger

logger = get_logger(__name__)


class ComparisonService:
    def __init__(
        self,
        repository_service: RepositoryServiceInterface,
        llm_service: LLMServiceInterface
    ):
        self.repository = repository_service
        self.llm = llm_service
        self.context_builder = ContextBuilder()


    async def get_products_for_comparison(
        self,
        product_ids: List[str],
        comparison_aspects: List[str],
    ) -> Dict:
        try:
            # Retrieve product details

            products = await self.repository.get_products_by_ids(product_ids)

            if not products or len(products) < 2:
                return {
                    "products": products,
                    "summary": "Not enough products found for comparison.",
                }

            #compare categories
            categories = {product.category for product in products}
            if len(categories) > 1:
                return {
                    "products": products,
                    "summary": "Products belong to different categories and cannot be compared.",
                }

            # Build context for LLM
            context = self.context_builder.build_product_context(products, comparison_aspects)

            comparison_query = f"Compare the following products based on: {', '.join(comparison_aspects)}."

            messages = PromptTemplates.product_comparison_prompt(
                    comparison_query, context, "")
            
            logger.info(f"Generating LLM response for comparison of products: {product_ids}")
            llm_response = await self.llm.generate_response(messages)

            return {
                "products": products,
                "summary": llm_response['response'],
            }

        except Exception as e:
            logger.error(f"Error in get_products_for_comparison: {str(e)}")
            logger.debug(traceback.format_exc())
            raise e