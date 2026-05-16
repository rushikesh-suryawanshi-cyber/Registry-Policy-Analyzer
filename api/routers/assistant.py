from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/assistant", tags=["assistant"])


class ChatRequest(BaseModel):
    question: str
    class_filter: Optional[str] = None  # "Machine" | "User" | None
    k: int = 5  # number of context documents to retrieve


class ChatResponse(BaseModel):
    answer: str
    question: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Query the local RAG pipeline (ChromaDB + Ollama LLM) using natural language.
    Requires Ollama to be running with `llama3.2:1b` and `nomic-embed-text` pulled.
    """
    try:
        from admx_parser.rag.pipeline import PolicyRAGPipeline

        filter_metadata = None
        if request.class_filter:
            filter_metadata = {"class_type": request.class_filter}

        pipeline = PolicyRAGPipeline()
        answer = pipeline.query(
            question=request.question,
            filter_metadata=filter_metadata,
            k=request.k
        )
        return ChatResponse(answer=answer, question=request.question)

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=(
                f"RAG pipeline error: {str(e)}. "
                "Ensure Ollama is running and models are pulled: "
                "`ollama pull llama3.2:1b && ollama pull nomic-embed-text`"
            )
        )
