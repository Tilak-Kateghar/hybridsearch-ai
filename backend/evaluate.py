from ragas import evaluate
from datasets import Dataset
from evaluation_data import dataset

from chunker import chunk_text
from embeddings import model
from bm25_store import BM25Store
from faiss_store import FAISSStore
from hybrid_search import HybridSearch
from reranker import Reranker
from query_service import QueryService
from llm import ask_llm
from ragas.llms import LangchainLLMWrapper
from langchain_ollama import OllamaLLM, OllamaEmbeddings

ollama_llm = OllamaLLM(model="llama3")

ragas_llm = LangchainLLMWrapper(ollama_llm)

ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text")

def build_system():
    documents = []

    for item in dataset:
        for ctx in item["contexts"]:
            documents.extend(chunk_text(ctx))

    bm25 = BM25Store()
    faiss = FAISSStore(model)

    bm25.build(documents)
    faiss.build(documents)

    hybrid = HybridSearch(bm25, faiss)
    reranker = Reranker()

    def llm_wrapper(prompt):
        return ask_llm(prompt)

    query_service = QueryService(
        hybrid,
        reranker,
        llm_wrapper,
        model  
    )

    return query_service


def generate_predictions(query_service):
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in dataset:
        q = item["question"]

        response = query_service.answer(q)

        retrieved = query_service.hybrid.search(q, top_k=3)

        questions.append(q)
        answers.append(response)
        contexts.append([doc for doc in retrieved])  # IMPORTANT
        ground_truths.append(item["answer"])

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "reference": ground_truths
    })


def run_evaluation():
    qs = build_system()
    data = generate_predictions(qs)

    result = evaluate(
        data,
        llm=ragas_llm,
        embeddings=ollama_embeddings,
        raise_exceptions=False,
        max_workers=1
    )

    print("\nEVALUATION RESULTS:")
    print(result)


if __name__ == "__main__":
    run_evaluation()