

from typing import Dict, List, Optional


class FormatterUtils:

    @staticmethod
    def format_history(
        conversation_history: Optional[List[Dict]]
    ) -> str:
        """Format conversation history for prompt"""
        if not conversation_history:
            return ""
        
        history_parts = []
        for msg in conversation_history[-4:]:  # Last 4 turns
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            metadata = msg.get('metadata', {})
            history_parts.append(f"{role.title()}: {content}")
            products = metadata.get('products', [])

            if products:
                history_parts.append(f"\nSources:")
                for index, product in enumerate(products):
                    text = f"  Product {index+1}: {product.get('name', '')} ({product.get('id', '')})\n"
                    text += f"    Brand: {product.get('brand', '')}, Availability: {product.get('availability', '')} \n"
                    description = product.get('description', '')
                    if description:
                        text += f"    Description: {description}"
                    history_parts.append(text)

        return "\n\n".join(history_parts)

    @staticmethod
    def build_product_sources(query_type:str, sources:List[Dict]) -> List[Dict[str,str]]:
        """Build lightweight source info for response"""
        product_sources = []
        
        if query_type in ['chitchat', 'out_of_scope', 'general_support']:
            return product_sources  # No sources for these types
        elif query_type in ['product_search', 'product_details', 'product_comparison']:
            for src in sources:
                product_sources.append({
                    "id": src.get('id', ''),
                    "name": src.get('name', ''),
                    "availability": src.get('availability', ''),
                    "description": src.get('description', ''),
                    #add more fields if needed later
                })
        elif query_type in ['policy_question']:
            #not implemented yet
            return product_sources

        return product_sources