import sys
import logging
from admx_parser.rag.indexer import PolicyIndexer
from admx_parser.rag.pipeline import PolicyRAGPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def index_policies():
    """Builds the ChromaDB vector index from the parsed JSON."""
    print("--- Indexing Policies (This may take a while depending on your hardware) ---")
    indexer = PolicyIndexer()
    indexer.index_from_json("examples/output.json", batch_size=50)
    print("Indexing complete!\n")

def query_rag():
    """Queries the local RAG pipeline."""
    print("--- Querying RAG Pipeline ---")
    pipeline = PolicyRAGPipeline(llm_model="llama3.2:1b")
    
    queries = [
        "How can I completely disable telemetry in Windows?",
        "What policies should I configure to harden the Edge browser against malicious downloads?",
        "How do I prevent users from using the webcam?"
    ]
    
    for q in queries:
        print(f"\n[Question]: {q}")
        try:
            # We can optionally pass metadata filters, e.g., filter_metadata={"class_type": "Machine"}
            answer = pipeline.query(q)
            print(f"[Answer]:\n{answer}")
        except Exception as e:
            print(f"[Error]: Make sure Ollama is running and models are pulled. {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--index":
        index_policies()
    else:
        print("Note: To index policies first, run: python rag_examples.py --index\n")
        query_rag()
