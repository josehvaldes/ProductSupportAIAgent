"""
Test all 7 key scenarios from architecture document
"""
import uuid
import requests
import time
import json
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent.parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)
from shopassist_api.application.settings.config import settings


BASE_URL = "http://localhost:8000"

class IntentTester:
    """Class to test integration scenarios for intent handling."""
    def __init__(self):
        self.results = []


    def test_scenario(self, name: str, query: str, session_id:str):
        """Test a single scenario"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"Query: {query}")
        print('='*60)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/chat/message",
                json={
                    "message": query,
                    "session_id": session_id
                },
                timeout=30
            )
            
            elapsed = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data['session_id']
                
                result = {
                    "scenario": name,
                    "query": query,
                    "status": "SUCCESS",
                    "response_time_ms": round(elapsed, 2),
                    "query_type": data['query_type'],
                    "num_sources": data['metadata']['num_sources'],
                    "tokens": data['metadata']['tokens']['total'],
                    "cost": data['metadata']['cost'],
                    "response_preview": data['response']
                }
                
                print(f"✅ SUCCESS")
                print(f"   Response time: {elapsed:.2f}ms")
                print(f"   Query type: {data['query_type']}")
                print(f"   Sources: {data['metadata']['num_sources']}")
                print(f"   Tokens: {data['metadata']['tokens']['total']}")
                print(f"   Cost: ${data['metadata']['cost']:.6f}")
                print(f"\n   Response preview:\n   {data['response']}")
                
            else:
                result = {
                    "scenario": name,
                    "query": query,
                    "status": "FAILED",
                    "error": response.text
                }
                print(f"❌ FAILED: {response.status_code}")
                print(f"   Error: {response.text}")
            
            self.results.append(result)
            
        except Exception as e:
            result = {
                "scenario": name,
                "query": query,
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ ERROR: {e}")
            self.results.append(result)

    def run_scenario(self, scenario: int):
        """Run all 7 scenarios"""
        print(f"\nRunning Scenario {scenario}")
        if scenario == 1:
            # Scenario 1: Product Discovery
            session_id = str(uuid.uuid4())
            self.test_scenario(
                "Product search",
                "I need a smartphone for video editing under $500",
                session_id
            )
        elif scenario == 2:
            session_id = str(uuid.uuid4())
            # Scenario 2: Specification Query
            self.test_scenario(
                "Product Details",
                "what characteristics have the MacBook Air M2?",
                session_id
            )
        elif scenario == 3:
            session_id = str(uuid.uuid4())
            # Scenario 3: Comparison
            self.test_scenario(
                "Product Comparison",
                "Compare the MacBook Air M2 and Dell XPS 15",
                session_id
            )
        elif scenario == 4:
            session_id = str(uuid.uuid4())
            # Scenario 4: Policy Question
            self.test_scenario(
                "Policy Question",
                "What's your return policy?",
                session_id
            )
        elif scenario == 5:
            session_id = str(uuid.uuid4())
            # Scenario 5: general_support Troubleshooting
            self.test_scenario(
                "Troubleshooting",
                "My headphones are not charging, what can I do?",
                session_id
            )
        elif scenario == 6:
            session_id = str(uuid.uuid4())
            # Scenario 6: Chitchat
            self.test_scenario(
                "Chitchat",
                "Tell me a joke about computers",
                session_id
            )
        elif scenario == 7:
            session_id = str(uuid.uuid4())
            # Scenario 7: out of scope
            self.test_scenario(
                "Out of Scope",
                "What's the weather like today in New York?",
                session_id
            )
    
    def generate_report(self):
        """Generate test report"""
        print(f"\n{'='*60}")
        print("TEST REPORT SUMMARY")
        print('='*60)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'SUCCESS')
        failed = total - successful
        
        print(f"\nTotal scenarios: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {successful/total*100:.1f}%")
        
        if successful > 0:
            success_results = [r for r in self.results if r['status'] == 'SUCCESS']
            avg_time = sum(r['response_time_ms'] for r in success_results) / len(success_results)
            avg_tokens = sum(r['tokens'] for r in success_results) / len(success_results)
            total_cost = sum(r['cost'] for r in success_results)
            
            print(f"\nPerformance Metrics:")
            print(f"  Average response time: {avg_time:.2f}ms")
            print(f"  Average tokens per response: {avg_tokens:.0f}")
            print(f"  Total cost: ${total_cost:.6f}")
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Detailed results saved to test_results.json")

if __name__ == "__main__":
    
    tester = IntentTester()
    parser = argparse.ArgumentParser(description="Integration Test Scenarios")
    parser.add_argument("scenario", type=str, help="scenario to run: all or comma-separated list of scenario numbers (1-7)")
    args = parser.parse_args()
    if args.scenario == "all":
        for i in range(1, 8):
            tester.run_scenario(i)
    else:
        scenarios = args.scenario.split(",")
        for arg in scenarios:
            tester.run_scenario(int(arg.strip()))

    tester.generate_report()