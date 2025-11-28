

from typing import Any


class ProductComparisonAgentState:
    query: str
    product_ids: list[str]

class ProductComparisonAgent:
    
    def __init__(self):
        pass

    async def ainvoke(self, input: dict) -> (dict[str, Any]| Any):
        """Compare products based on user query and product IDs."""
        pass