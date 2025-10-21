import uuid
import math
import json
import traceback
import pandas as pd

from tokenizers import Tokenizer
from tiktoken import get_encoding

from semantic_text_splitter import TextSplitter
import argparse

#Configurable Model parameters
#Move to settings?
MODEL_DIM = 1536           # text-embedding-3-small
BYTES_PER_FLOAT = 4        # float32
VECTOR_SIZE_BYTES = MODEL_DIM * BYTES_PER_FLOAT  # = 6,144 bytes ≈ 6 KB per vector
VECTOR_QUOTA_MB = 25       # Free tier
TOKEN_LIMIT = 8000         # Model max input tokens 8191

#Adjust the ratio according to needs and documents sizes
AVG_CHUNK_TOKENS = 500     # You can tune this based on your chunking
CHUNK_OVERLAP_TOKENS = int(AVG_CHUNK_TOKENS * 0.125)  #Overlap between chunks. harcoded to 50 or use a %

#dataset has ruppes prices so convert to USD as 10/15/2025
EXCHANGE_RATE_TO_USD = 0.011 

header_index_dict = {
        "id": 0,
        "name": 1,
        "category": 2,
        "price": 4,
        "rating": 6,
        "description": 8,
        "review_count": 7,
        "product_url": 15,
        "image_url": 14
    }

encoding = get_encoding("cl100k_base")

tokenizer = Tokenizer.from_pretrained("bert-base-uncased")

semantic_splitter = TextSplitter.from_huggingface_tokenizer(
    tokenizer, #"thenlper/gte-small", 
    capacity=AVG_CHUNK_TOKENS, 
    overlap=CHUNK_OVERLAP_TOKENS
)

def semantic_text_splitter(text: str) -> list[str]:
    return semantic_splitter.chunks(text)


def get_token_data(text: str, avg_chunk_tokens=AVG_CHUNK_TOKENS):
    #Estimate tokens, vectors, and storage
    total_tokens:int = len(encoding.encode(text))
    total_vectors = math.ceil(total_tokens/avg_chunk_tokens) if total_tokens > 0 else 0
    total_storage_mb = (total_vectors * VECTOR_SIZE_BYTES) / (1024 * 1024)
    return { "total_tokens": total_tokens, "total_vectors": total_vectors, "total_storage_mb": total_storage_mb }

def suggest_brand(name: str) -> str:
    # Simple heuristic: assume brand is the first word in the name
    if not name:
        return ""
    return name.split(" ")[0]

def parse_file(path:str, sample_size:int = -1) -> list :

    df = pd.read_csv(path)
    print(f"Initial rows in dataframe: {len(df)}")
    df.drop_duplicates(subset=['product_id'], inplace=True, keep='last')
    print(f"Rows after dropping duplicates: {len(df)}")

    sample = df.sample(n=sample_size) if sample_size > 0 and sample_size < len(df) else df
    
    print(f"Parsing file {path}...")

    docs = []
    for index, row in sample.iterrows():
        doc = {}
        for key, idx in header_index_dict.items():
            doc[key] = str(row.iloc[idx]) if idx < len(row) else ""
        
        category_str = str(row.iloc[header_index_dict["category"]]) if header_index_dict["category"] < len(row) else ""
        doc["category_full"] = category_str.split('|') if category_str else []        #last category as main category
        doc["category"] = doc["category_full"][-1] if doc["category_full"] else ""

        vector_text = f"{doc.get('name', '')}. {doc.get('description', '')}"
        doc["vector_text"] = vector_text
        
        vector_metadata = get_token_data(doc.get("vector_text"))
        doc["vector_metadata"] = vector_metadata

        doc["brand"] =  suggest_brand(doc.get("name", ""))

        price = doc.get("price", "").replace("₹", "").replace(",", "").strip()
        doc["price"] = round( float(price) * EXCHANGE_RATE_TO_USD if price.replace('.','',1).isdigit() else 0.00, 2)

        rating_count = doc.get("rating", "").replace(",", "").strip()
        doc["rating"] = float(rating_count) if rating_count.replace('.','',1).isdigit() else 0.0

        review_count = doc.get("review_count", "").replace(",", "").strip()
        doc["review_count"] = float(review_count) if review_count.replace('.','',1).isdigit() else 0.0

        new_id = uuid.uuid4().hex[:12]
        doc["id"] = new_id

        if vector_metadata.get("total_tokens", 0) > 500:
            chunks = []
            for chunk in semantic_text_splitter(doc["vector_text"]):
                chunks.append(chunk)
            doc["chunks"] = chunks
        docs.append(doc)
    print(f"Parsed {len(docs)} documents.")
    return docs

def save_to_json(data, output_path='output.json'):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print("Error saving to JSON:", e)
        traceback.print_exc()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Product Data Parser")
    parser.add_argument("sample_size", type=int, help="Number of sample records to parse")

    args = parser.parse_args()
    print(f"Sample size set to: {args.sample_size}")
    file_path = "./amazon.csv"
    output_path = f"amazon_{args.sample_size}.json"
    data = parse_file(file_path, sample_size=args.sample_size)
    save_to_json(data, output_path)

    for doc in data:  # Print first 2 documents for verification
        metadata = doc.get("vector_metadata")
        if metadata.get("total_tokens", 0) > 500:  # Print only if tokens > 500 for brevity
            print(f"ID: {doc.get('id')}, name: {doc.get('name')[0:50]}...")
            print(f"  Tokens: {metadata.get('total_tokens')}, Vectors: {metadata.get('total_vectors')}, Storage (MB): {metadata.get('total_storage_mb'):.4f}")
            print()

    print("Done.")

