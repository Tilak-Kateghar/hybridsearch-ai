from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from chunker import chunk_text
from embeddings import model
# from hybrid_search import HybridSearch
from reranker import Reranker
from query_service import QueryService
from notes import save_note, get_notes
from video_service import get_transcript
from whisper_service import whisper_transcript
# from user_store import user_store
from vector_store import VectorStore
from redis_cache import redis_client
from utils import is_valid_chunk
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStore(model)

USE_API = True

if USE_API:
    from llm_api import ask_llm_api as ask_llm
else:
    from llm import ask_llm

reranker = Reranker()

def llm_wrapper(prompt):
    return ask_llm(prompt)

query_service = QueryService(None, reranker, llm_wrapper, model)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest_video")
def ingest_video(data: dict):
    user_id = data.get("user_id", "default")
    url = data["url"]

    # user = user_store.get_user(user_id)

    # if user.get("last_video") == url:
    #     return {"status": "already indexed"}

    # user["last_video"] = url

    print("Processing video:", url)

    # 🔹 Try YouTube transcript
    source = "youtube"
    print("SOURCE:", source)

    chunks = get_transcript(url)

    if not chunks:
        print("Falling back to Whisper...")
        chunks = whisper_transcript(url)
        source = "whisper"

    if not chunks:
        return {"error": "Could not process video"}

    chunks = [
        c for c in chunk_text(text)
        if is_valid_chunk(c["text"])
    ][:20]

    texts = [c["text"] for c in chunks]

    # user_store.save_documents(user_id, texts)
    # user = user_store.get_user(user_id)
    # user["bm25"].build(texts)
    # user["faiss"].build(texts)
    # user["hybrid"] = HybridSearch(user["bm25"], user["faiss"])

    vector_store.upsert(texts, user_id)

    for key in redis_client.scan_iter(f"*{user_id}*"):
        redis_client.delete(key)

    query_service.video_chunks = chunks

    return {
        "status": "video indexed",
        "chunks": len(texts),
        "source": source
    }


@app.post("/ingest")
def ingest(data: dict):
    user_id = data.get("user_id", "default")
    text = data["text"]

    # user = user_store.get_user(user_id)

    chunks = [
        c for c in chunk_text(text)
        if is_valid_chunk(c)
    ][:15]

    # if user.get("last_text") == text:
    #     return {"status": "already indexed"}

    # user["last_text"] = text

    # user_store.save_documents(user_id, chunks)
    # user = user_store.get_user(user_id)

    # user["bm25"].build(chunks)
    # user["faiss"].build(chunks)

    # user["hybrid"] = HybridSearch(user["bm25"], user["faiss"])

    vector_store.upsert(chunks, user_id)

    for key in redis_client.scan_iter(f"*{user_id}*"):
        redis_client.delete(key)

    # reset video mode
    query_service.video_chunks = None

    return {"status": "indexed", "chunks": len(chunks)}


@app.post("/query")
async def query(data: dict):
    user_id = data.get("user_id", "default")
    query_text = data["query"]

    print(f"USER: {user_id} | QUERY: {query_text}")

    # user = user_store.get_user(user_id)

    # if not user["hybrid"]:
    #     return {
    #         "answer": "No data indexed yet.",
    #         "actions": "",
    #         "timestamp": None
    #     }

    # query_service.hybrid = user["hybrid"]

    # result = query_service.answer(query_text)
    query_service.user_id = user_id

    docs = vector_store.search(query_text, user_id, top_k=5)

    result = query_service.answer_with_context(query_text, docs)

    return result


@app.post("/save_note")
def save_note_api(data: dict):
    save_note(data)
    return {"status": "saved"}


@app.get("/notes")
def fetch_notes():
    return {"notes": get_notes()}