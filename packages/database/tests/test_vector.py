import pytest
from database.vector.vector_store import VectorStoreClient

def test_vector_store_client():
    # Use Ephemeral in-memory client
    client = VectorStoreClient()
    
    # 1. Clean state
    client.clear_all()
    results = client.query_similar("database testing", n_results=1)
    assert len(results) == 0

    # 2. Add text documents
    client.add_document("doc-1", "Learn SQLite persistence techniques.", {"tags": ["sql"]})
    client.add_document("doc-2", "Implement neural networks for AI scheduling.", {"tags": ["ai"]})

    # 3. Query similar
    # Query matching doc-1 text features
    results = client.query_similar("SQLite database techniques", n_results=1)
    assert len(results) == 1
    assert results[0]["id"] == "doc-1"
    assert results[0]["metadata"]["tags"] == ["sql"]

    # 4. Delete document
    client.delete_document("doc-1")
    results = client.query_similar("SQLite techniques", n_results=2)
    # Only doc-2 should remain
    assert len(results) == 1
    assert results[0]["id"] == "doc-2"

    # 5. Clear all
    client.clear_all()
    results = client.query_similar("AI scheduling", n_results=2)
    assert len(results) == 0
