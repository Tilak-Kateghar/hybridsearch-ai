class HybridSearch:
    def __init__(self, bm25_store, faiss_store):
        self.bm25 = bm25_store
        self.faiss = faiss_store

    def reciprocal_rank_fusion(self, bm25_results, faiss_results, k=60):
        scores = {}

        for rank, item in enumerate(bm25_results):
            doc = item["doc"]
            scores[doc] = scores.get(doc, 0) + 1 / (k + rank)

        for rank, item in enumerate(faiss_results):
            doc = item["doc"]
            scores[doc] = scores.get(doc, 0) + 1 / (k + rank)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in ranked]

    def search(self, query, top_k=5):
        bm25_results = self.bm25.search(query, top_k=top_k)
        faiss_results = self.faiss.search(query, top_k=top_k)

        fused = self.reciprocal_rank_fusion(bm25_results, faiss_results)

        return fused[:top_k]