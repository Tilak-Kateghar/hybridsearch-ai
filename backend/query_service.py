from backend.sentence_transformers import util
from backend.redis_cache import get_cache, set_cache
import hashlib
from backend.utils import is_valid_chunk

def normalize_query(query: str):
    q = query.lower().strip()

    stop_phrases = [
        "can you", "please", "tell me",
        "what is", "give me", "explain"
    ]

    for phrase in stop_phrases:
        q = q.replace(phrase, "")

    q = " ".join(q.split())

    if "summary" in q:
        q = "summary"

    return q


def semantic_filter(query, docs, embedding_model, threshold=0.35):
    if not docs:
        return []

    query_vec = embedding_model.encode(query)
    doc_vecs = embedding_model.encode(docs)

    scores = util.cos_sim(query_vec, doc_vecs)[0]

    filtered = [
        doc for doc, score in zip(docs, scores)
        if score > threshold
    ]

    return filtered if len(filtered) >= 2 else docs[:5]


def clean_context(docs):
    cleaned = []

    for d in docs:
        d = d.replace("\n", " ").strip()

        if not is_valid_chunk(d):
            continue

        cleaned.append(d)

    return cleaned


def detect_intent(query):
    q = query.lower()
    if "summary" in q:
        return "summary"
    elif "compare" in q:
        return "compare"
    return "qa"


class QueryService:
    def __init__(self, hybrid_search, reranker, llm, embedding_model):
        self.hybrid = hybrid_search
        self.reranker = reranker
        self.llm = llm
        self.embedding_model = embedding_model
        self.video_chunks = None

    def answer_with_context(self, query, docs):

        # if not docs:
        #     return {
        #         "answer": "Not enough relevant context found.",
        #         "actions": "",
        #         "timestamp": None
        #     }

        user_id = getattr(self, "user_id", "default")

        normalized_query = normalize_query(query)

        content_hash = hashlib.md5(
            " ".join(docs[:10]).encode()
        ).hexdigest()

        cache_key = f"answer::{user_id}::{normalized_query}::{content_hash}"
        retrieval_key = f"retrieval::{user_id}::{normalized_query}::{content_hash}"

        cached = get_cache(cache_key)
        if cached:
            print("⚡ REDIS CACHE HIT")
            return cached

        cached_docs = get_cache(retrieval_key)
        if cached_docs:
            print("⚡ RETRIEVAL CACHE HIT")
            docs = cached_docs
        else:
            set_cache(retrieval_key, docs, ttl=1800)

        filtered_docs = semantic_filter(
            normalized_query,
            docs,
            self.embedding_model
        )

        reranked_docs = self.reranker.rerank(
            normalized_query,
            filtered_docs[:8],
            top_k=5
        )

        context_docs = clean_context(reranked_docs)

        # if not context_docs:
        #     return {
        #         "answer": "Context too noisy.",
        #         "actions": "",
        #         "timestamp": None
        #     }

        context_docs = list(dict.fromkeys(context_docs))[:5]

        context = "\n\n".join(context_docs)

        print("\n=== FINAL CONTEXT ===")
        for d in context_docs:
            print(d[:120])

        # if len(context.split()) < 30:
        #     return {
        #         "answer": "Not enough relevant context found.",
        #         "actions": "",
        #         "timestamp": None
        #     }

        # 🔹 STEP 5: INTENT
        intent = detect_intent(query)

        if intent == "summary":
            prompt = f"""
You are a strict summarizer.

Rules:
- Use ONLY the provided content
- Do NOT assume anything
- Be concise and clear

Content:
{context}
"""
        elif intent == "compare":
            prompt = f"""
Compare key ideas ONLY from the content below.

Content:
{context}
"""
        else:
            prompt = f"""
You are a strict QA system.

Rules:
- Answer ONLY from context
- Do NOT guess

Context:
{context}

Question:
{query}
"""

        # 🔹 STEP 6: LLM
        response = self.llm(prompt)

        result = {
            "answer": response,
            "actions": ""
        }

        set_cache(cache_key, result, ttl=1800)

        return result