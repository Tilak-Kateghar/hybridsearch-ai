# from pinecone import Pinecone, ServerlessSpec
# import os
# import uuid

# pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# INDEX_NAME = "hybridsearch"

# # create index if not exists
# if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
#     pc.create_index(
#         name=INDEX_NAME,
#         dimension=384,  # MiniLM
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )

# index = pc.Index(INDEX_NAME)


# class VectorStore:
#     def __init__(self, embedding_model):
#         self.embedding_model = embedding_model

#     def upsert(self, texts, user_id):
#         embeddings = self.embedding_model.encode(texts)

#         vectors = []
#         for i, (text, emb) in enumerate(zip(texts, embeddings)):
#             vectors.append({
#                 "id": str(uuid.uuid4()),
#                 "values": emb.tolist(),
#                 "metadata": {
#                     "text": text,
#                     "user_id": user_id
#                 }
#             })

#         index.upsert(vectors=vectors)

#     def search(self, query, user_id, top_k=5):
#         query_vec = self.embedding_model.encode([query])[0]

#         results = index.query(
#             vector=query_vec.tolist(),
#             top_k=top_k,
#             include_metadata=True,
#             filter={"user_id": user_id}
#         )

#         return [
#             match["metadata"]["text"]
#             for match in results["matches"]
#         ]

import os
import uuid
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = "hybridsearch"

existing_indexes = [i["name"] for i in pc.list_indexes()]

if INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

index = pc.Index(INDEX_NAME)


class VectorStore:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def upsert(self, texts, user_id):
        embeddings = self.embedding_model.encode(texts)

        vectors = []
        for text, emb in zip(texts, embeddings):
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": emb.tolist(),
                "metadata": {
                    "text": text,
                    "user_id": user_id
                }
            })

        index.upsert(vectors=vectors)

    def search(self, query, user_id, top_k=5):
        query_vec = self.embedding_model.encode([query])[0]

        results = index.query(
            vector=query_vec.tolist(),
            top_k=top_k,
            include_metadata=True,
            filter={
                "user_id": {"$eq": user_id}
            }
        )

        return [
            match["metadata"]["text"]
            for match in results["matches"]
        ]