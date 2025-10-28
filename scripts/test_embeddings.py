import json
import jsonlines
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def cosine_sim(emb1, emb2):
    return cosine_similarity([emb1], [emb2])[0][0]

def test_embedding_quality():
    print("🧪 Testing embedding quality...\n")
    # Load product embeddings
    products = []
    with jsonlines.open("c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_50_with_transformers_embeddings.json") as reader:
        products = [item for item in reader]
    
    print(f"Loaded {len(products)} products with embeddings.\n")    
    # Test 1: Same product chunks should be similar
    print("Test 1: Similarity between chunks of same product")
    same_product = [p for p in products if p['product_id'] == products[0]['product_id']]
    print(f"   Found {len(same_product)} chunks for product ID: {products[0]['product_id']}")

    if len(same_product) > 1:
        sim = cosine_sim(same_product[0]['embedding'], same_product[1]['embedding'])
        print(f"   Similarity: {sim:.4f} (expect > 0.7)")
        print(f"   ✅ PASS" if sim > 0.7 else "   ❌ FAIL")
    
    # Test 2: Same category should be moderately similar
    print("\nTest 2: Similarity within same category")
    category = products[0]['category']
    same_category = [p for p in products if p['category'] == category][:3]
    
    if len(same_category) >= 2:
        sim = cosine_sim(same_category[0]['embedding'], same_category[1]['embedding'])
        print(f"   Similarity: {sim:.4f} (expect 0.3-0.7)")
        print(f"   ✅ PASS" if 0.3 < sim < 0.7 else "   ❌ FAIL")
    
    # Test 3: Different categories should be less similar
    print("\nTest 3: Similarity across different categories")
    categories = list(set(p['category'] for p in products))
    
    if len(categories) >= 2:
        cat1_prod = next(p for p in products if p['category'] == categories[0])
        cat2_prod = next(p for p in products if p['category'] == categories[1])
        sim = cosine_sim(cat1_prod['embedding'], cat2_prod['embedding'])
        print(f"   Similarity: {sim:.4f} (expect < 0.5)")
        print(f"   ✅ PASS" if sim < 0.5 else "   ❌ FAIL")
    
    print("\n✅ Embedding quality tests complete!")

if __name__ == "__main__":
    test_embedding_quality()
