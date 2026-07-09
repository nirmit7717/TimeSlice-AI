import chromadb
from typing import List, Dict, Any
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

class SimpleMockEmbeddingFunction(EmbeddingFunction):
    """
    Local mock embedding function to execute vector operations without downloading external libraries
    or model parameters. Generates deterministic 384-dimensional vectors.
    """
    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            words = text.split()
            # Construct dummy values based on word lengths
            vector = [float(len(w)) for w in words][:384]
            # Pad with zeros to fit standard 384 dimensions
            if len(vector) < 384:
                vector += [0.0] * (384 - len(vector))
            embeddings.append(vector)
        return embeddings

class VectorStoreClient:
    """
    ChromaDB wrapper providing persistent and in-memory vector storage for Context Vault RAG.
    """
    def __init__(self, persist_dir: str = None):
        if persist_dir:
            self.client = chromadb.PersistentClient(path=persist_dir)
        else:
            self.client = chromadb.EphemeralClient()

        self.collection = self.client.get_or_create_collection(
            name="timeslice_vault",
            embedding_function=SimpleMockEmbeddingFunction()
        )

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> None:
        """
        Inserts or updates a document into the Chroma collection.
        """
        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}]
        )

    def query_similar(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves the most similar context entries.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Flatten structure into convenient dict format
        documents = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if "distances" in results else [0.0] * len(ids)

        output = []
        for i in range(len(ids)):
            output.append({
                "id": ids[i],
                "document": documents[i],
                "metadata": metadatas[i],
                "distance": distances[i]
            })
        return output

    def delete_document(self, doc_id: str) -> None:
        """
        Deletes a context record.
        """
        self.collection.delete(ids=[doc_id])

    def clear_all(self) -> None:
        """
        Deletes all documents in the collection.
        """
        # Retrieve all ids first
        all_ids = self.collection.get()["ids"]
        if all_ids:
            self.collection.delete(ids=all_ids)
