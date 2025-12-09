import traceback
import uuid
import requests
import time
import json
import sys
import argparse
import asyncio
import sys

from typing import List
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent.parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)

from shopassist_api.application.settings.config import settings
from shopassist_api.logging_config import setup_logging
from shopassist_api.logging_config import get_logger

setup_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        log_to_console=settings.log_to_console
    )

logger = get_logger(__name__)

BASE_URL = "http://localhost:8000"

class TestComparison:

    def __init__(self):
        self.results = []


    async def execute(self, product_ids:List[str], comparison_aspects: List[str]):
        """Test a single scenario"""
        print(f"\n{'='*60}")
        print(f"Testing: {product_ids}")
        print(f"Comparison Aspects: {comparison_aspects}")
        print('='*60)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/products/compare",
                json={
                    "product_ids": product_ids,
                    "comparison_aspects": comparison_aspects
                },
                timeout=45
            )
            
            elapsed = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "product_ids": product_ids,
                    "comparison_aspects": comparison_aspects,
                    "status": "SUCCESS",
                    "response_time_ms": round(elapsed, 2),
                    "response": data['summary'],
                    "products_compared": data['products']
                }
                
                print(f"✅ SUCCESS")
                print(f"   Response time: {elapsed:.2f}ms")
                print(f"   Products compared: {[p['id'] for p in data['products']]}")
                print(f"\n   Response preview:\n   {data['summary']}")
                
            else:
                result = {
                    "product_ids": product_ids,
                    "comparison_aspects": comparison_aspects,
                    "status": "FAILED",
                    "error": response.text
                }
                print(f"❌ FAILED: {response.status_code}")
                print(f"   Error: {response.text}")
            
            self.results.append(result)
            
        except Exception as e:
            result = {
                "product_ids": product_ids,
                "comparison_aspects": comparison_aspects,
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ ERROR: {e}")
            traceback.print_exc()
            self.results.append(result)

    def test_product_comparison(self):
        test_scenarios = [
            {
                "product_ids": ["38fa499937f8", "57dc878ee017"],
                "comparison_aspects": ["price", "features"]
            },
            # {
            #     "product_ids": ["prod_003", "prod_004", "prod_005"],
            #     "comparison_aspects": ["durability", "warranty", "customer reviews"]
            # },
            # {
            #     "product_ids": ["prod_006", "prod_007"],
            #     "comparison_aspects": ["design", "usability"]
            # }
        ]
        
        loop = asyncio.get_event_loop()
        for scenario in test_scenarios:
            loop.run_until_complete(
                tester.execute(
                    product_ids=scenario["product_ids"],
                    comparison_aspects=scenario["comparison_aspects"]
                )
            )

    def print_results(self):
        print("\n\nTest Results Summary:")
        for result in self.results:
            print(json.dumps(result, indent=2))

if __name__ == "__main__":
    tester = TestComparison()
    tester.test_product_comparison()
    tester.print_results()
