from rank_bm25 import BM25Okapi
import pickle
import os

class BM25Store:
    def __init__(self):
        self.bm25 = None
        self.documents = []

    def tokenize(self, text):
        return text.lower().split()

    def build(self, documents):
        self.documents = documents
        tokenized = [self.tokenize(doc) for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query, top_k=5):
        tokenized_query = self.tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        ranked = sorted(
            list(enumerate(scores)),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"doc": self.documents[idx], "score": score}
            for idx, score in ranked[:top_k]
        ]