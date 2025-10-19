# API endpoint tests
import unittest
from shopassist_api.infrastructure.services.openai_service import openai_service

class TestServicesIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup code for integration tests
        pass

    def setUp(self):
        # Setup code before each test
        self.openai = openai_service()

    @unittest.skip("Skipping Azure OpenAI response generation test in integration tests")
    def test_generate_response(self):
        # Test generating a response using Azure OpenAI
        prompt = "Hello, how can I assist you today?"
        response = self.openai.generate_embedding(prompt)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def tireDown(self):
        # Teardown code after each test
        pass
