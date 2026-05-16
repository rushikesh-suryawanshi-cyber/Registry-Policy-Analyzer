from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

class PolicyRetriever:
    """Handles semantic search and filtering against the ChromaDB policy index."""
    
    def __init__(self, persist_directory: str = "./chroma_db", model_name: str = "nomic-embed-text", k: int = 5):
        self.persist_directory = persist_directory
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.vector_store = Chroma(
            collection_name="policies",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        # Create the underlying LangChain retriever
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        
    def search(self, query: str, filter_metadata: Optional[Dict[str, Any]] = None, k: int = 5) -> List[Document]:
        """Performs a semantic search with optional metadata filtering."""
        search_kwargs = {"k": k}
        if filter_metadata:
            search_kwargs["filter"] = filter_metadata
            
        # Temporarily update kwargs
        self.retriever.search_kwargs = search_kwargs
        return self.retriever.invoke(query)
        
    def get_retriever(self, filter_metadata: Optional[Dict[str, Any]] = None, k: int = 5):
        """Returns the LangChain retriever object directly for use in chains."""
        search_kwargs = {"k": k}
        if filter_metadata:
            search_kwargs["filter"] = filter_metadata
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
