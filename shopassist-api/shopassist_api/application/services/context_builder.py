from typing import List, Dict
import tiktoken

class ContextBuilder:
    """
    Build context string for LLM from retrieved documents
    """
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4")
    
    def build_product_context(self, products: List[Dict]) -> str:
        """
        Build context string from product results
        
        Format:
        Product 1: [Name]
        Price: $X.XX
        Category: [Category]
        Description: [Text]
        ---
        """
        context_parts = []
        total_tokens = 0
        
        for i, product in enumerate(products, 1):
            product_text = self._format_product(product, i)
            tokens = len(self.encoding.encode(product_text))
            
            # Check if adding this product exceeds limit
            if total_tokens + tokens > self.max_tokens:
                break
            
            context_parts.append(product_text)
            total_tokens += tokens
        
        context = "\n\n".join(context_parts)
        return context
    
    def build_knowledge_base_context(self, chunks: List[Dict]) -> str:
        """
        Build context string from KB results
        """
        context_parts = []
        total_tokens = 0
        
        for i, chunk in enumerate(chunks, 1):
            chunk_text = f"Source {i} [{chunk['doc_type']}]:\n{chunk['text']}"
            tokens = len(self.encoding.encode(chunk_text))
            
            if total_tokens + tokens > self.max_tokens:
                break
            
            context_parts.append(chunk_text)
            total_tokens += tokens
        
        return "\n\n---\n\n".join(context_parts)
    
    def _format_product(self, product: Dict, index: int) -> str:
            """Format single product for context"""
            return f"""Product {index}: {product['title']}
                    Price: ${product['price']:.2f}
                    Category: {product['category']}
                    Brand: {product.get('brand', 'N/A')}
                    Description: {product.get('description', product.get('matched_text', 'N/A'))}
                    Relevance Score: {product.get('relevance_score', 0):.3f}"""