from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from database.vector.vector_store import VectorStoreClient
from app.dependencies import get_vector_store
from app.schemas import VectorQueryRequest, VectorDocumentAdd

router = APIRouter(prefix="/vault", tags=["vault"])

@router.post("/search")
def search_vault(
    payload: VectorQueryRequest,
    vector_client: VectorStoreClient = Depends(get_vector_store)
):
    """
    Performs cosine similarity searches on ChromaDB RAG context vaults.
    """
    return vector_client.query_similar(
        query_text=payload.query_text,
        n_results=payload.n_results or 3
    )

@router.post("/add")
def add_to_vault(
    payload: VectorDocumentAdd,
    vector_client: VectorStoreClient = Depends(get_vector_store)
):
    """
    Inserts raw context snippets directly into the vector database.
    """
    vector_client.add_document(
        doc_id=payload.doc_id,
        text=payload.text,
        metadata=payload.metadata
    )
    return {"status": "success", "message": f"Document '{payload.doc_id}' indexed in vault"}
