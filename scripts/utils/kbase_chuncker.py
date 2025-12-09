"""
This module handles chunking of knowledge base documents into smaller pieces suitable for embedding and storage.
It uses a semantic text splitter to ensure chunks are meaningful and within token limits.
"""

import json
import traceback
import math
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer
from tiktoken import get_encoding

KB_FOLDER_PATH = "../knowledge_base/"
KB_CHUNKED_PATH = "./knowledge_base_chunked/"
#Configurable Model parameters
#Move to settings?
MODEL_DIM = 1536           # text-embedding-3-small
BYTES_PER_FLOAT = 4        # float32
VECTOR_SIZE_BYTES = MODEL_DIM * BYTES_PER_FLOAT  # = 6,144 bytes ≈ 6 KB per vector
VECTOR_QUOTA_MB = 25       # Free tier
TOKEN_LIMIT = 8000         # Model max input tokens 8191

#Adjust the ratio according to needs and documents sizes
AVG_CHUNK_TOKENS = 500     # You can tune this based on your chunking
CHUNK_OVERLAP_TOKENS = int(AVG_CHUNK_TOKENS * 0.125)  #Overlap between chunks. hardcoded to 50 or use a %
CHUNK_SIZE = AVG_CHUNK_TOKENS - CHUNK_OVERLAP_TOKENS  #Effective chunk size after overlap

encoding = get_encoding("cl100k_base") # For models like text-embedding-3-small

tokenizer = Tokenizer.from_pretrained("bert-base-uncased")

semantic_splitter = TextSplitter.from_huggingface_tokenizer(
    tokenizer, #"thenlper/gte-small", 
    capacity=AVG_CHUNK_TOKENS, 
    overlap=CHUNK_OVERLAP_TOKENS
)


def chunk_in_folder(folder_path:str = KB_FOLDER_PATH, output_path:str = KB_CHUNKED_PATH):
    """
    Chunks all text files in the specified folder and prints chunking statistics.
    """
    import os
    total_files = 0
    all_files_tokens = 0
    allfiles_storage_mb = 0.0

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            print(f"Processing file: {filename}")
            total_files += 1
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                print(f"  Original text length (chars): {len(text)}")
                print(f"  Original text length (tokens): {len(encoding.encode(text))}")
                #extract medatata if any
                if text.startswith("---"):
                    skipt_pre_metadata, metadada_str, text = text.split('---', 2)
                metadata = {}
                for line in metadada_str.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                                
                total_tokens = len(encoding.encode(text))
                total_vectors = math.ceil(total_tokens / AVG_CHUNK_TOKENS) if total_tokens > 0 else 0
                total_storage_mb = (total_vectors * VECTOR_SIZE_BYTES) / (1024 * 1024)
                chunks = []
                if total_vectors == 1:
                    print("  No chunking needed, single chunk.")
                    chunks = [text]
                    all_files_tokens += total_tokens
                    allfiles_storage_mb += total_storage_mb
                else:
                    print(f"  Chunking needed, estimated chunks: {total_vectors}")
                    chunks = semantic_splitter.chunks(text)
                    
                    # Recalculate totals based on chunks
                    total_tokens = 0
                    chunk_vectors = 0
                    chunk_storage_mb = 0.0
                    for chunk_text in chunks:
                        chunk_tokens = len(encoding.encode(chunk_text))
                        total_tokens += chunk_tokens
                        chunk_vectors += 1 if chunk_tokens > 0 else 0
                        chunk_storage_mb += (chunk_vectors * VECTOR_SIZE_BYTES) / (1024 * 1024)
                    
                    # Update totals
                    total_storage_mb = chunk_storage_mb
                    total_vectors = chunk_vectors

                    all_files_tokens += total_tokens
                    allfiles_storage_mb += total_storage_mb


                json_content = {
                    "source_file": filename,
                    "metadata": metadata,
                    "chunks": chunks,
                    "total_tokens": total_tokens,
                    "total_vectors": total_vectors,
                    "total_storage_mb": total_storage_mb
                }
                
                output_file = os.path.join(output_path, filename.replace('.md', '_chunked.json'))
                with open(output_file, 'w', encoding='utf-8') as out_f:
                    json.dump(json_content, out_f, indent=4)
    #end for
    #print statistics
    print("Chunking complete.")
    print(f"Total files processed: {total_files}")
    print(f"Total tokens across all files: {all_files_tokens}")
    print(f"Total estimated storage (MB) across all files: {allfiles_storage_mb:.4f}")


if __name__ == "__main__":
    try:
        chunk_in_folder()
    except Exception as e:
        print("Error during chunking:")
        traceback.print_exc()
    print("Done.")
            
