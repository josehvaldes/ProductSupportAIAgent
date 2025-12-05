from typing import List, Dict
from langsmith import traceable
import tiktoken
from shopassist_api.logging_config import get_logger
import traceback

logger = get_logger(__name__)

class ContextBuilder:
    """
    Build context string for LLM from retrieved documents
    """
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    @traceable(name="context.build_product_context", tags=["context"], metadata={"version": "1.0"})
    def build_product_context(self, products: List[Dict]) -> str:
        """
        Build context string from product results
        
        Format:
        Product 1: [Name]
        Price: $X.XX
        Category: [Category]
        Brand: [Brand]
        Available: [in_stock/out_of_stock]
        Description: [Text]
        ---
        """
        context_parts = []
        total_tokens = 0
        logger.info(f"Building product context: {len(products)} products")

        try:
            for i, product in enumerate(products, 1):
                product_text = self._format_product(product, i)
                tokens = len(self.encoding.encode(product_text))
                
                # Check if adding this product exceeds limit
                if total_tokens + tokens > self.max_tokens:
                    break
                
                context_parts.append(product_text)
                total_tokens += tokens
        except Exception as e:
            logger.error(f"  Error logging product count: {e}")
            traceback.print_exc()

        context = "\n\n".join(context_parts)
        return context
    
    @traceable(name="context.build_knowledge_base_context", tags=["context"], metadata={"version": "1.0"})
    def build_knowledge_base_context(self, chunks: List[Dict]) -> str:
        """
        Build context string from KB results
        """
        context_parts = []
        total_tokens = 0
        
        for i, chunk in enumerate(chunks, 1):
            chunk_text = f"Source {i} [{chunk['doc_id']}]:\n{chunk['text']}"
            tokens = len(self.encoding.encode(chunk_text))
            
            if total_tokens + tokens > self.max_tokens:
                break
            
            context_parts.append(chunk_text)
            total_tokens += tokens
        
        return "\n\n---\n\n".join(context_parts)
    
    def _format_product(self, product: Dict, index: int) -> str:
            """Format single product for context"""
            return f"""Product {index}: {product['name']}
                    Price: ${product['price']:.2f}
                    Category: {product['category']}
                    Brand: {product.get('brand', 'N/A')}
                    Available: { product.get('availability', 'out_of_stock')}
                    Description: {product.get('description', product.get('matched_text', 'N/A'))}
                    Relevance Score: {product.get('distance', 0):.3f}"""