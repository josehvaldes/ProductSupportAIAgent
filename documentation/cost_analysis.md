# Cost analysis for LLM usages in Azure Open AI (as Nov 2025)

#GPT-4.1 Mini Global:
Pricing (as of Nov 2025):

Input: $0.40 per 1M tokens
Output: $1.4 per 1M tokens

Your Usage (100 requests/day):

Assumptions per request:
- Input: ~1,500 tokens (query + context + history)
- Output: ~300 tokens (response)

Daily cost:
- Input: 100 × 1,500 tokens = 150,000 tokens
  → $0.40 × 0.15 = $0.06/day
- Output: 100 × 300 tokens = 30,000 tokens
  → $1.4 × 0.03 = $0.42/day

Total month cost GPT-4-mini:
 ~$0.48/day = $14.20/month


#GPT-4.1 Nano Global:
Pricing (as of Nov 2025):

Input: $0.10 per 1M tokens
Output: $0.40 per 1M tokens

Your Usage (100 requests/day):

Assumptions per request:
- Input: ~1,500 tokens (query + context + history)
- Output: ~300 tokens (response)

Daily cost:
- Input: 100 × 1,500 tokens = 150,000 tokens
  → $0.1 × 0.15 = $0.015/day
- Output: 100 × 300 tokens = 30,000 tokens
  → $0.4 × 0.03 = $0.12/day

Total Monthly cost for GPt-4.1 nano: 
~$0.135/day = $4.20/month

##Total estimated monthly cost for Azure Open AI LLM's:
$18.2 per 100 product calls

## Gemma 7B deployment alternatives:

Azure VM (24/7): $379 20× more
Databricks (on-demand): $60-90 3 - 5× more
Azure ML Serverless: $18-25   1-2x more
