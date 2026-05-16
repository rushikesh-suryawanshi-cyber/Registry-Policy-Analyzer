import logging
from typing import Dict, Any, Optional
from langchain_community.llms import Ollama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .retriever import PolicyRetriever
from .prompts import POLICY_PROMPT_TEMPLATE

logger = logging.getLogger("admx_parser")

class PolicyRAGPipeline:
    """End-to-end local RAG pipeline for Policy Intelligence."""
    
    def __init__(self, llm_model: str = "llama3.2:1b", persist_directory: str = "./chroma_db", embed_model: str = "nomic-embed-text"):
        self.retriever_helper = PolicyRetriever(
            persist_directory=persist_directory,
            model_name=embed_model
        )
        self.llm = Ollama(model=llm_model)
        
    def _format_docs(self, docs):
        """Formats the retrieved LangChain documents into a single context string."""
        return "\n\n".join(doc.page_content for doc in docs)
        
    def query(self, question: str, filter_metadata: Optional[Dict[str, Any]] = None, k: int = 5) -> str:
        """Executes the RAG pipeline to answer the given question."""
        logger.info(f"Executing RAG pipeline for query: '{question}'")
        
        # 1. Get the base retriever
        retriever = self.retriever_helper.get_retriever(filter_metadata=filter_metadata, k=k)
        
        # 2. Build the LangChain runnable chain
        rag_chain = (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | POLICY_PROMPT_TEMPLATE
            | self.llm
            | StrOutputParser()
        )
        
        # 3. Invoke
        result = rag_chain.invoke(question)
        return result
