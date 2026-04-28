# HybridSearch AI: Context-Aware Retrieval-Augmented Intelligence System

> A production-grade hybrid retrieval system that combines semantic search, keyword matching, vector databases, and LLM reasoning to extract high-quality answers from unstructured text and video content.

---

## 1. Introduction

Modern AI systems often fail not because of weak models, but due to **poor retrieval quality**. Large Language Models (LLMs) rely heavily on the relevance of provided context. When retrieval is weak, answers become hallucinated, vague, or incorrect.

Most systems:
- Rely purely on semantic search (vector similarity)
- Ignore keyword-level precision
- Fail on noisy or unstructured data (web pages, transcripts)
- Do not handle real-time ingestion effectively

This project addresses these limitations by building a **hybrid, production-ready Retrieval-Augmented Generation (RAG) system** that:
- Combines **semantic + lexical retrieval**
- Supports **text and video ingestion**
- Uses **LLMs strictly constrained by context**
- Implements **multi-layer caching for latency optimization**

---

## 2. Motivation

> Instead of asking:
> “What can the model generate?”
>
> This system asks:
> “What is the most relevant context, and how can we enforce grounded answers?”

### Problems with existing systems:
- Hallucination due to weak context
- Slow responses (no caching)
- Poor handling of real-world noisy data
- No multi-user isolation

### Goal:
Build a **fast, accurate, scalable AI retrieval system** that behaves like a real product.

---

## 3. Key Features

### 🔍 Hybrid Retrieval
- Combines:
  - Vector similarity (semantic)
  - Keyword matching (BM25)
- Improves recall and precision

### 🧠 Context-Constrained LLM
- Strict prompting rules:
  - No assumptions
  - No hallucination
  - Answer only from context

### 🎥 Video Understanding
- YouTube transcript extraction
- Whisper fallback for audio transcription
- Timestamp-aware answers

### ⚡ Redis Caching
- Query-level caching
- Retrieval-level caching
- Normalized query matching

### 🧩 Multi-User Isolation
- Separate context per user
- Independent retrieval pipelines

### 🗄️ Vector Database (Production Upgrade)
- Pinecone integration
- Scalable semantic search

---

## 4. System Architecture

### High-Level Pipeline

1. Data ingestion (text / video)
2. Chunking and cleaning
3. Embedding generation
4. Vector DB storage (Pinecone)
5. Hybrid retrieval (semantic + lexical)
6. Reranking (cross-encoder)
7. Context filtering
8. LLM response generation
9. Redis caching

---

## 5. Methodology

### 5.1 Data Ingestion

#### Text:
- Chunked into semantically meaningful segments
- Filtered for noise

#### Video:
- Step 1: YouTube transcript API
- Step 2: Whisper fallback
- Step 3: Timestamp mapping

---

### 5.2 Embeddings

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Generates dense semantic vectors
- Used for vector DB search

---

### 5.3 Hybrid Retrieval

Instead of relying on a single method:

- **Semantic Search** → captures meaning  
- **Keyword Search (BM25)** → captures exact matches  

Combined → improved robustness

---

### 5.4 Reranking (Critical Component)

- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Reorders retrieved documents
- Filters weak matches

---

### 5.5 Context Cleaning

- Removes noisy chunks
- Filters short/irrelevant text
- Deduplicates results

---

### 5.6 LLM Integration

Supports:
- Groq (LLaMA-based)
- Gemini API

### Strict Prompting Strategy:
- Answer ONLY from context
- If insufficient → return fallback
- Prevent hallucination

---

### 5.7 Caching Strategy (Redis)

Two-level caching:

#### 🔹 Retrieval Cache
- Stores retrieved documents

#### 🔹 Answer Cache
- Stores final LLM output

#### 🔹 Query Normalization
Example:
"can you summarize this"
"summary"
"please summarize"

→ all map to `"summary"`

---

## 6. Tech Stack

### Backend
- FastAPI
- Uvicorn

### AI / ML
- Sentence Transformers
- Cross-Encoder Reranker
- Whisper

### Infra
- Pinecone (Vector DB)
- Redis (Caching)
- Render (Deployment)

### Frontend
- Chrome Extension (Popup UI)

---

## 7. Deployment Architecture

### Backend
- Hosted on Render

### Cache
- Redis (Upstash)

### Vector DB
- Pinecone (serverless)

---

## 8. Engineering Challenges & Solutions

### ❌ Weak Retrieval Quality
✔️ Fixed using hybrid + reranking

---

### ❌ Hallucination
✔️ Strict prompt constraints + context filtering

---

### ❌ Slow Response Time
✔️ Redis caching

---

### ❌ Noisy Real-World Data
✔️ Chunk filtering + semantic thresholding

---

### ❌ Deployment Issues
✔️ Fixed:
- Absolute imports (`backend.*`)
- Port binding (`$PORT`)
- Package structure

---

## 9. Performance Characteristics

### Improvements Achieved:
- Faster responses via caching
- Higher relevance via reranking
- Reduced hallucination via strict prompts

---

## 10. Usage

### Run Locally

uvicorn backend.main:app --reload

## 🔗 API Endpoints

### Ingest Text  
**POST /ingest**

Indexes raw text into the system.

---

### Ingest Video  
**POST /ingest_video**

Processes and indexes YouTube video content.

---

### Query  
**POST /query**

Retrieves answers from indexed content using hybrid retrieval + LLM.

---

## 🧩 Chrome Extension

### Features

- Chat-like interface  
- Query any webpage  
- Instant answers  
- Context-aware responses  

---

## ⚠️ Limitations

- Whisper is slow on CPU  
- Dependent on transcript quality  
- Not optimized for extremely long documents  

---

## 🚀 Future Improvements

- Streaming responses (like ChatGPT)  
- Better chunking (semantic segmentation)  
- Advanced ranking (ColBERT / hybrid fusion)  
- Multi-document memory  
- Fine-tuned domain models  

---

## 🧠 Conclusion

HybridSearch AI demonstrates that:

**Retrieval quality is the real bottleneck in modern AI systems.**

By combining:

- Hybrid search  
- Reranking  
- Strict prompting  
- Caching  

This system moves from a basic project to a **production-grade intelligent retrieval system**.

---

## ⚖️ Disclaimer

This project is intended for:

- Educational use  
- Research exploration  
- System design learning  

Not a fully hardened enterprise system.

---

## 👨‍💻 Author

**Tilak Kateghar**
