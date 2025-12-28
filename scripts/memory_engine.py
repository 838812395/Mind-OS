import os
import logging
import sys
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
import chromadb
import yaml

# Load Config
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'mind_os_config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

CONFIG = load_config()
PERSIST_DIR = "./.mind_os/vector_store"
LOGS_DIR = "." # Root of the project to scan everything

# Global Settings for Offline Operation
# BAAI/bge-small-en-v1.5 is the default for FastEmbed, 
# for Chinese we can use BAAI/bge-small-zh-v1.5 if needed,
# but FastEmbed default is usually okay for mixed content.
Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = None # Disable LLM for now, we just need retrieval

def setup_engine():
    # Setup ChromaDB
    db = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = db.get_or_create_collection("mind_os_memory")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    return storage_context

def sync_memory():
    """Build or update the index from local markdown files."""
    print("🧠 Starting Mind-OS Memory Sync (Offline Mode)...")
    
    # Define directories to scan based on config
    target_dirs = list(CONFIG.get('directories', {}).values())
    
    # Load documents
    documents = []
    for d in target_dirs:
        full_path = os.path.join(LOGS_DIR, d)
        if os.path.exists(full_path):
            print(f"📄 Reading: {d}...")
            reader = SimpleDirectoryReader(full_path, recursive=True, required_exts=[".md"])
            documents.extend(reader.load_data())
    
    if not documents:
        print("⚠️ No documents found to index.")
        return

    storage_context = setup_engine()
    
    # Build index
    print(f"⚡ Indexing {len(documents)} document fragments using FastEmbed...")
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
    
    print("✅ Sync complete. Memory is updated.")

def query_memory(query_str):
    """Retrieve relevant context for a given query."""
    print(f"🔎 Querying memory for: '{query_str}'")
    
    db = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = db.get_or_create_collection("mind_os_memory")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    index = VectorStoreIndex.from_vector_store(vector_store)
    
    # Simple retriever instead of full query engine (since LLM is None)
    retriever = index.as_retriever(similarity_top_k=5)
    nodes = retriever.retrieve(query_str)
    
    print("\n--- Memory Retrieval Result ---")
    if not nodes:
        print("No relevant memories found.")
    else:
        for i, node in enumerate(nodes):
            print(f"[{i+1}] Source: {node.metadata.get('file_path', 'Unknown')}")
            print(f"    Content: {node.text[:200]}...")
            print("-" * 30)
    print("-------------------------------\n")
    return nodes

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        sync_memory()
    elif len(sys.argv) > 1 and sys.argv[1] == "query":
        query_str = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        query_memory(query_str)
    else:
        print("Usage: python memory_engine.py [sync | query 'your question']")
