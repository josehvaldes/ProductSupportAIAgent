import json
import jsonlines
import uuid
import sys
sys.path.append('../shopassist-api')

from pymilvus import connections, utility

import argparse


# Generate embeddings for sample texts using Transformers model. use OpenAIEmbeddingService for OpenAI embeddings.
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService

def process_products_file(source_file: str, output_file: str, embedding_service: TransformersEmbeddingService):
    """Process the source file to generate embeddings and save to output file."""
    output = []
    print(f"Processing file: {source_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for record in data:  # Process first 2 records for demo

            metadata = record.get("vector_metadata", {})
            total_vectors = 0 

            if record.get("chunks") is None:
                # chunks key missing, assume single vector
                total_vectors = 1
            else:
                total_vectors = len(record["chunks"])

            if total_vectors == 0:
                print(f"Skipping record ID: {record.get('id', 'N/A')} as it has zero vectors.")
                continue
            elif total_vectors == 1:
                text = record.get("vector_text", "")
                print(f"Generating single embedding for record ID: {record.get('id', 'N/A')}.")
                embedding = embedding_service.generate_embedding(text)
                output.append({
                    "id": uuid.uuid4().hex, # Unique ID for this embedding record
                    "product_id": record.get("id", "N/A"), # Link back to product ID
                    "embedding": embedding,
                    "chunk_text": text,
                    "chunk_index": 0,
                    "total_chunks": total_vectors,
                    "category": record.get("category", "unknown"),
                    "price": record.get("price", 0.0),
                    "brand": record.get("brand", "unknown")
                })
                continue
            else:
                chunks = record["chunks"] if "chunks" in record else []
                if chunks and isinstance(chunks, list):
                    embeddings = embedding_service.generate_embedding_batch(chunks, batch_size=10)
                    # Store { id, embeddeding, text } for each chunks this time
                    print(f"Generated {len(embeddings)} embeddings for record ID: {record.get('id', 'N/A')}.") 
                    for i in range(len(embeddings)):
                        output.append({
                            "id": uuid.uuid4().hex,
                            "product_id": record.get("id", "N/A"),
                            "embedding": embeddings[i]['embedding'],
                            "chunk_text": embeddings[i]['text'],
                            "chunk_index": i,
                            "total_chunks": total_vectors,
                            "category": record.get("category", "unknown"),
                            "price": record.get("price", 0.0),
                            "brand": record.get("brand", "unknown")
                        })        
            
    print(f"Saving embeddings to: {output_file}")   
    with jsonlines.open(output_file, mode='w') as writer:
        writer.write_all(output)

def process_knowledge_base_folder(source_folder: str, output_file: str, embedding_service: TransformersEmbeddingService):
    """Process all JSON files in the source folder to generate embeddings and save to output file."""
    import os
    print(f"Processing knowledge base folder: {source_folder}")
    all_kb_chunks = []
    for filename in os.listdir(source_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(source_folder, filename)
            print(f"Processing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data is None:
                    print(f"No data found in file: {filename}, skipping.")
                    continue

                chunks = data.get("chunks", [])
                if chunks and isinstance(chunks, list):
                    embeddings = embedding_service.generate_embedding_batch(chunks, batch_size=10)
                    print(f"Generated {len(embeddings)} embeddings for file {filename}.") 
                    data["embeddings"] = embeddings
                    for i in range(len(embeddings)):
                        all_kb_chunks.append({
                                "id": i,
                                "embedding": embeddings[i]['embedding'],
                                "knowledge_base_id": filename,
                                "chunk_text": embeddings[i]['text']
                            })
            print(f"Saving embeddings to: {output_file}")

            with jsonlines.open(output_file, mode='w') as writer:
                writer.write_all(all_kb_chunks)

def main(option: str):

    print("Generating embeddings for sample texts...")
    source_file = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_50.json"
    output_file = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_50_with_transformers_embeddings.json"  
    model_name = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
    
    print(f"Using model: {model_name}")
    embedding_service = TransformersEmbeddingService(model_name=model_name)
    
    if option in ["products", "both"]:
        print(f"Processing products from file: {source_file}")
        process_products_file(source_file, output_file, embedding_service)

    kb_source_folder = "c:/personal/_ProductSupportAIAgent/ProductSupportAIAgent/scripts/knowledge_base_chunked/"
    output_file = "c:/personal/_ProductSupportAIAgent/ProductSupportAIAgent/scripts/knowledge_base_chunked/kb_with_embeddings.jsonl"
    
    if option in ["knowledgebase", "both"]:
        print(f"Processing knowledge base from folder: {kb_source_folder}")
        process_knowledge_base_folder(kb_source_folder, output_file, embedding_service)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embedding Generation Script")
    parser.add_argument("option", type=str, help="Products, KnowledgeBase, or Both")
    args = parser.parse_args()
    main(args.option.lower())