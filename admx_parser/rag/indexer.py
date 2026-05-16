import json
import logging
from typing import List, Dict, Any
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

logger = logging.getLogger("admx_parser")

class PolicyIndexer:
    """Indexes parsed policies into a ChromaDB vector store."""
    
    def __init__(self, persist_directory: str = "./chroma_db", model_name: str = "nomic-embed-text"):
        self.persist_directory = persist_directory
        # Use nomic-embed-text model via Ollama locally
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.vector_store = Chroma(
            collection_name="policies",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        
    def create_document_from_policy(self, policy: Dict[str, Any]) -> Document:
        """Converts a policy dictionary into a rich LangChain Document."""
        name = policy.get("name", "")
        display_name = policy.get("displayName", "")
        explain_text = policy.get("explainText", "")
        gpo_path = policy.get("gpoPath", "")
        class_type = policy.get("class", "")
        registry_key = policy.get("key", "")
        value_name = policy.get("valueName", "")
        
        # Craft a rich text representation for semantic embedding
        page_content = f"""Policy Name: {display_name} ({name})
Category Path: {gpo_path}
Class: {class_type}
Registry Key: {registry_key}
Registry Value: {value_name}

Description:
{explain_text}
"""
        
        # Add filtering metadata
        metadata = {
            "policy_name": name,
            "display_name": display_name,
            "class_type": class_type,
            "registry_key": registry_key,
            "gpo_path": gpo_path
        }
        
        # ChromaDB cannot store None values in metadata
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        return Document(page_content=page_content, metadata=metadata)

    def index_from_json(self, json_path: str, batch_size: int = 100):
        """Loads a parsed JSON file and indexes all policies."""
        logger.info(f"Loading policies from {json_path}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        policies = data.get("policies", [])
        if not policies:
            logger.warning("No policies found in JSON.")
            return
            
        logger.info(f"Converting {len(policies)} policies into Documents...")
        documents = [self.create_document_from_policy(p) for p in policies]
        
        logger.info("Adding documents to ChromaDB in batches...")
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            self.vector_store.add_documents(batch)
            logger.info(f"Indexed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
            
        logger.info(f"Successfully indexed {len(documents)} policies to {self.persist_directory}.")
