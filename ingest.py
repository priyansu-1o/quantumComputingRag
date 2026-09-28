# ingest.py
import chromadb
from sentence_transformers import SentenceTransformer
from extract_books import extract_text_from_pdf
from chunking import chunk_text

# Load the free local embedding model (downloads once, ~80MB)
print("Loading embedding model...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Set up local vector database
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="quantum_books")

def embed_text(text: str) -> list[float]:
    return embed_model.encode(text).tolist()

def ingest_book(pdf_path: str, book_name: str):
    print(f"Extracting {book_name}...")
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    print(f"  {len(chunks)} chunks found. Embedding...")

    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        collection.add(
            ids=[f"{book_name}_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"book": book_name}]
        )
    print(f"  Done: {book_name}")

if __name__ == "__main__":
    ingest_book("books/book1.pdf", "Book1")
    ingest_book("books/book2.pdf", "Book2")
    ingest_book("books/book3.pdf", "Book3")
    print("All books ingested successfully.")