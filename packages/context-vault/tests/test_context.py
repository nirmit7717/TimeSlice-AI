import pytest
from context_vault.services.context_service import ContextService
from database.vector.vector_store import VectorStoreClient

def test_context_vault_rag_pipeline():
    # Ephemeral vector store client for unit testing
    vector_client = VectorStoreClient(persist_dir=None)
    service = ContextService(vector_client=vector_client)

    # 1. Store context documents
    service.store(
        doc_id="doc1",
        text="Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers.",
        metadata={"source": "meeting_notes", "tags": ["docker", "devops"]}
    )
    service.store(
        doc_id="doc2",
        text="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.",
        metadata={"source": "documentation", "tags": ["python", "fastapi"]}
    )

    # 2. Retrieve context using query
    package = service.retrieve(query_text="fastapi framework", n_results=1)
    
    assert len(package.relevant_documents) == 1
    closest_doc = package.relevant_documents[0]
    assert closest_doc.id in ["doc1", "doc2"]
    assert package.confidence_score > 0.0

