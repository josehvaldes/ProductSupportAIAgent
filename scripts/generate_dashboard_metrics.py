from langsmith import Client

from datetime import datetime, timedelta
from collections import defaultdict
import statistics

import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append('../shopassist-api')
# Load .env file from the correct location
script_dir = Path(__file__).parent
env_path = script_dir.parent / 'shopassist-api' / '.env'
load_dotenv(dotenv_path=env_path)


client = Client()
def analyze_baseline_performance(project_name="ProductSupportAIAgent", days=1):
    """Pull metrics from LangSmith and generate report"""
    
    # Get runs from last N days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    print(f"Analyzing runs from {start_time} to {end_time}...")
    runs = client.list_runs(
        project_name=project_name,
        start_time=start_time,
        is_root=True  # Only top-level calls
    )
    
    # Organize metrics by tag/name
    metrics = defaultdict(lambda: {
        "latencies": [],
        "token_counts": [],
        "error_count": 0,
        "success_count": 0
    })
    
    for run in runs:
        tags = run.tags or []
        name = run.name
        print(f"Processing run: {name} with tags: {tags}")
        # Collect latency
        if run.end_time and run.start_time:
            latency_ms = (run.end_time - run.start_time).total_seconds() * 1000
            metrics[name]["latencies"].append(latency_ms)
        
        # Collect tokens
        if hasattr(run, 'outputs') and run.outputs:
            token_usage = run.outputs.get('token_usage', {})
            total_tokens = token_usage.get('total_tokens', 0)
            if total_tokens > 0:
                metrics[name]["token_counts"].append(total_tokens)
        
        # Track errors
        if run.error:
            metrics[name]["error_count"] += 1
        else:
            metrics[name]["success_count"] += 1

        if name == "manual_embedding_trace":
            print(f"  Latency: {latency_ms} ms, Tokens: {total_tokens}, Error: {run.error}")
            client.delete_run(run.id)

    # Generate report
    print("=" * 60)
    print(f"BASELINE METRICS REPORT ({days} day(s))")
    print("=" * 60)
    
    for component, data in sorted(metrics.items()):
        total = data["success_count"] + data["error_count"]
        if total == 0:
            continue
            
        print(f"\n{component}:")
        print(f"  Total Runs: {total}")
        print(f"  Success Rate: {data['success_count']/total*100:.1f}%")
        
        if data["latencies"]:
            print(f"  Latency (ms):")
            print(f"    p50: {statistics.median(data['latencies']):.1f}")
            print(f"    p95: {statistics.quantiles(data['latencies'], n=20)[18]:.1f}")
            print(f"    p99: {statistics.quantiles(data['latencies'], n=100)[98]:.1f}")
            print(f"    avg: {statistics.mean(data['latencies']):.1f}")
        
        if data["token_counts"]:
            print(f"  Tokens:")
            print(f"    avg: {statistics.mean(data['token_counts']):.0f}")
            print(f"    max: {max(data['token_counts'])}")
    
    print("\n" + "=" * 60)
    
    return metrics

if __name__ == "__main__":
    analyze_baseline_performance(days=1)