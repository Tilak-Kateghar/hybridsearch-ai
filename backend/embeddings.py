# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer(
#     "all-MiniLM-L6-v2",
#     device="cpu"
# )

from sentence_transformers import SentenceTransformer
from redis_cache import get_cache, set_cache
import hashlib

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")


def embed(text):
    key = "embed::" + hashlib.md5(text.encode()).hexdigest()

    cached = get_cache(key)
    if cached:
        return cached

    vec = model.encode(text).tolist()
    set_cache(key, vec, ttl=86400)  # 1 day

    return vec