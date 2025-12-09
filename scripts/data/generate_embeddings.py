import json
import jsonlines
import uuid
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

# Generate embeddings for sample texts using Transformers model. use OpenAIEmbeddingService for OpenAI embeddings.
from shopassist_api.application.interfaces.service_interfaces import EmbeddingServiceInterface
from shopassist_api.infrastructure.services.transformers_embedding_service import TransformersEmbeddingService
#from shopassist_api.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService 


def process_products_file(source_file: str, output_file: str, embedding_service: EmbeddingServiceInterface):
    """Process the source file to generate embeddings and save to output file."""
    output = []
    print(f"Processing file: {source_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for record in data:  # Process each product record

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
                    "text": text,
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
                            "id": uuid.uuid4().hex[:12],
                            "product_id": record.get("id", "N/A"),
                            "text": embeddings[i]['text'],
                            "embedding": embeddings[i]['embedding'],                            
                            "chunk_index": i,
                            "total_chunks": total_vectors,
                            "category": record.get("category", "unknown"),
                            "price": record.get("price", 0.0),
                            "brand": record.get("brand", "unknown")
                        })        
            
    print(f"Saving embeddings to: {output_file}")   
    with jsonlines.open(output_file, mode='w') as writer:
        writer.write_all(output)

def process_knowledge_base_folder(source_folder: str, output_file: str, embedding_service: EmbeddingServiceInterface):
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
                
                metadata = data.get("metadata", {})
                chunks = data.get("chunks", [])
                if chunks and isinstance(chunks, list):
                    embeddings = embedding_service.generate_embedding_batch(chunks, batch_size=10)
                    print(f"Generated {len(embeddings)} embeddings for file {filename}.") 
                    data["embeddings"] = embeddings
                    for i in range(len(embeddings)):
                        all_kb_chunks.append({
                                "id": uuid.uuid4().hex[:12],
                                "doc_id": filename.replace('.json', ''),
                                "text": embeddings[i]['text'],
                                "chunk_index": i,
                                "embedding": embeddings[i]['embedding'],
                                "doc_type": metadata.get("category", "unknown")
                            })
            print(f"Saving embeddings to: {output_file}")

            with jsonlines.open(output_file, mode='w') as writer:
                writer.write_all(all_kb_chunks)

def process_category_file(source_file: str, output_file: str, embedding_service: EmbeddingServiceInterface):
    """Process the category file to generate embeddings and save to output file."""
    print(f"Processing category file: {source_file}")
    output = []
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for record in data:  # Process each category record
            category_name = record.get("name", "")
            full_category_name = record.get("full_name", "")
            #improve formatting for embedding generation
            formatted_category = full_category_name.replace(" > ", " , ") if full_category_name else category_name
            print(f".Formatted category for embedding: {category_name}")
            if not category_name:
                print(f"Skipping record ID: {record.get('id', 'N/A')} as it has no name.")
                continue
            
            embedding = embedding_service.generate_embedding(category_name)
            full_embedding = embedding_service.generate_embedding(formatted_category)
            output.append({
                "id": record.get("id", "N/A"),
                "name": category_name,
                "full_name": full_category_name,
                "embedding": embedding,
                "full_embedding": full_embedding
            })
    print(f"Saving category embeddings to: {output_file}")   
    with jsonlines.open(output_file, mode='w') as writer:
        writer.write_all(output)

def main(option: str):

    print("Generating embeddings for sample files")
    print(f"Using Transformers model for products: {settings.transformers_embedding_model}")
    print(f"Using Transformers model for categories: {settings.transformers_category_embedding_model}")

    #Use: embedding_service = OpenAIEmbeddingService() for OpenAI embeddings
    embedder_service = TransformersEmbeddingService(model_name=settings.transformers_embedding_model)
    category_embedder_service = TransformersEmbeddingService(model_name=settings.transformers_category_embedding_model)

    source_file = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_100.json"
    output_file = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_100_with_transformers_embeddings.jsonl"  
    
    if option in ["products", "both"]:
        print(f"Processing products from file: {source_file}")
        process_products_file(source_file, output_file, embedder_service)

    kb_source_folder = "c:/personal/_ProductSupportAIAgent/ProductSupportAIAgent/scripts/knowledge_base_chunked/"
    output_file = "c:/personal/_ProductSupportAIAgent/ProductSupportAIAgent/scripts/knowledge_base_chunked/kb_with_transformers_embeddings.jsonl"
    
    if option in ["knowledgebase", "both"]:
        print(f"Processing knowledge base from folder: {kb_source_folder}")
        process_knowledge_base_folder(kb_source_folder, output_file, embedder_service)

    category_source_file = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_50_categories.json"
    output_file = "c:/personal/_ProductSupportAIAgent/datasets/product_data/amazon_50_categories_with_transformer_embeddings.jsonl"
    if option in ["categories", "both"]:
        print("Category embeddings generation.")
        process_category_file(category_source_file, output_file, category_embedder_service)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embedding Generation Script")
    parser.add_argument("option", type=str, help="Products, KnowledgeBase, Categories, or Both")
    args = parser.parse_args()
    main(args.option.lower())