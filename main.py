# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import ollama
from sentence_transformers import SentenceTransformer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading embedding model...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="quantum_books")

class ChatRequest(BaseModel):
    question: str

def embed_text(text: str) -> list[float]:
    return embed_model.encode(text).tolist()

@app.post("/api/chat")
def chat(req: ChatRequest):
    # 1. Embed the question
    question_embedding = embed_text(req.question)

    # 2. Retrieve top 5 relevant chunks from your 3 books
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5
    )
    retrieved_chunks = results["documents"][0]
    sources = [m["book"] for m in results["metadatas"][0]]

    context = "\n\n---\n\n".join(retrieved_chunks)

    system_prompt = (
        "You are a quantum computing tutor. Answer the user's question "
        "using ONLY the provided context from their textbooks. "
        "If the context doesn't contain the answer, say so honestly "
        "instead of guessing."
    )

    # 3. Ask local Ollama model
    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {req.question}"}
        ]
    )

    answer = response["message"]["content"]

    return {
        "answer": answer,
        "sources": list(set(sources))
    }

@app.get("/")
def health_check():
    return {"status": "running"}