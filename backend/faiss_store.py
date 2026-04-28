import faiss
import numpy as np

class FAISSStore:
    def __init__(self, embedding_model):
        self.index = None
        self.documents = []
        self.embedding_model = embedding_model

    def build(self, documents):
        self.documents = documents
        embeddings = self.embedding_model.encode(
            documents,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings).astype("float32"))

    def search(self, query, top_k=5):
        query_vec = self.embedding_model.encode([query])
        distances, indices = self.index.search(
            np.array(query_vec).astype("float32"),
            top_k
        )

        return [
            {"doc": self.documents[idx], "score": float(distances[0][i])}
            for i, idx in enumerate(indices[0])
        ]