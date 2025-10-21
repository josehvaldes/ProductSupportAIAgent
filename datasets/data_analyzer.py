import json
import traceback

TOKEN_LIMIT = 500

def show_off_limits(file_path:str):
    print("This is a restricted function.")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        internal_count = 0
        for doc in data:  # Print first 2 documents for verification
            metadata = doc.get("vector_metadata")
            if metadata.get("total_tokens", 0) > TOKEN_LIMIT:  # Print only if tokens > 500 
                internal_count += 1
                print(f"ID: {doc.get('id')}, Category:{doc.get("category","")}, name: {doc.get('name')[0:50]}...")
                print(f"  Tokens: {metadata.get('total_tokens')}, Vectors: {metadata.get('total_vectors')}, Storage (MB): {metadata.get('total_storage_mb'):.4f}")
                print()
        print(f"Total documents with tokens > {TOKEN_LIMIT}: {internal_count}")
    


if __name__ == "__main__":
    file_path = "amazon_100.json"
    data = show_off_limits(file_path)

    print("Done.")
