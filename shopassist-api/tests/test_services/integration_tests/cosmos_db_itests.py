# API endpoint tests
import unittest
from shopassist_api.infrastructure.services.cosmos_product_service import CosmosProductService
from shopassist_api.domain.models.product import Product

class TestServicesIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup code for integration tests
        pass

    def setUp(self):
        # Setup code before each test
        self.cosmos = CosmosProductService()

    @unittest.skip("Skipping product retrieval test in integration tests")
    def test_get_product_by_id(self):
        # Test retrieving a product by ID
        product_id = "ee54928186ad_test"
        product:Product = self.cosmos.get_product_by_id(product_id)
        self.assertIsNotNone(product)
        self.assertEqual(product['id'], product_id)
    
    @unittest.skip("Skipping category search test in integration tests")
    def test_search_products_by_category(self):
        # Test searching products by category
        category = "Smartphones_test"
        products = self.cosmos.search_products_by_category(category)
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)
        for product in products:
            self.assertIn(category, product.get('category', ''))
    
    @unittest.skip("Skipping price range search test in integration tests")
    def test_search_products_by_price_range(self):
        # Test searching products by price range
        min_price = 200
        max_price = 250
        products = self.cosmos.search_products_by_price_range(min_price, max_price)
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)
        for product in products:
            price = product.get('price', 0)
            self.assertGreaterEqual(price, min_price)
            self.assertLessEqual(price, max_price)

    def tireDown(self):
        # Teardown code after each test
        pass
        
if __name__ == "__main__":
    unittest.main()