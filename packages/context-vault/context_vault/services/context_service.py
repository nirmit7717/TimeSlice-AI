from datetime import datetime
from typing import List, Dict, Any, Optional
from database.vector.vector_store import VectorStoreClient
from context_vault.models import ContextPackage, ContextDocument

class ContextService:
    def __init__(self, vector_client: Optional[VectorStoreClient] = None):
        # Fallback to shared global if not injected
        if vector_client is None:
            from app.dependencies import get_vector_store
            self.vector_client = get_vector_store()
        else:
            self.vector_client = vector_client

    def retrieve(self, query_text: str, n_results: int = 3) -> ContextPackage:
        """
        Retrieves relevant documents and builds a structured ContextPackage.
        """
        results = self.vector_client.query_similar(query_text, n_results=n_results)
        
        relevant_docs = []
        relevant_reflections = []
        
        for r in results:
            doc_type = r["metadata"].get("source", "document")
            ctx_doc = ContextDocument(
                id=r["id"],
                document=r["document"],
                metadata=r["metadata"],
                distance=r["distance"]
            )
            if doc_type == "reflection":
                relevant_reflections.append(r)
            else:
                relevant_docs.append(ctx_doc)
                
        # Simple heuristic confidence score based on closest document match distance
        confidence = 1.0
        if results:
            # lower distance means higher confidence (Chroma default is L2 squared)
            min_dist = min(r["distance"] for r in results)
            confidence = max(0.1, min(0.99, 1.0 - min_dist))

        return ContextPackage(
            relevant_processes=[],
            relevant_documents=relevant_docs,
            relevant_reflections=relevant_reflections,
            confidence_score=round(confidence, 2),
            retrieved_at=datetime.utcnow()
        )

    def store(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> None:
        """
        Stores a context entry inside the vault vector database.
        """
        self.vector_client.add_document(doc_id, text, metadata)

    def delete(self, doc_id: str) -> None:
        """
        Removes a context entry from the vault.
        """
        self.vector_client.delete_document(doc_id)
