import json
import pytest
from shopassist_api.application.services.formaters import FormatterUtils
class TestFormaters:

    def setup_method(self):
        pass

    def test_format_history_empty(self):
        result = FormatterUtils.format_history(None)
        assert result == ""
    
    def test_format_history_with_data(self):
        conversation_history = [
            {
                "role": "user",
                "content": "Hello, I need help finding a laptop.",
                "metadata": {}
            },
            {
                "role": "assistant",
                "content": "Sure! What specifications are you looking for?",
                "metadata": {}
            },
            {
                "role": "user",
                "content": "I want a laptop under $1000.",
                "metadata": {
                    "products": [
                        {
                            "name": "Laptop A",
                            "id": "123",
                            "brand": "BrandX",
                            "availability": "In Stock",
                            "description": "A great laptop for everyday use."
                        }
                    ]
                }
            }
        ]
        result = FormatterUtils.format_history(conversation_history)
        assert "User: Hello, I need help finding a laptop." in result
        assert "Assistant: Sure! What specifications are you looking for?" in result
        assert "User: I want a laptop under $1000." in result
        assert "Sources:" in result
        assert "Product 1: Laptop A (123)" in result
        assert "Brand: BrandX, Availability: In Stock" in result
        assert "Description: A great laptop for everyday use." in result

