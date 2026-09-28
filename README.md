# Quantum Computing RAG Chatbot

A local, fully free RAG (Retrieval-Augmented Generation) chatbot that answers questions about quantum computing using content extracted from your own PDF books. Runs entirely on your machine using Ollama (local LLM), ChromaDB (local vector database), and sentence-transformers (local embeddings) — no API keys, no cost.

## How it works

1. Your PDF books are extracted into raw text (`extract_books.py`)
2. Text is split into small overlapping chunks (`chunking.py`)
3. Each chunk is converted into a vector embedding and stored in ChromaDB (`ingest.py`)
4. When you ask a question, the app embeds your question, retrieves the most relevant chunks, and passes them to a local LLM (via Ollama) to generate a grounded answer (`main.py`)

## Project structure

```
rag/
├── books/            # Your source PDF books (not included — add your own)
├── chroma_db/         # Auto-generated vector database (created by ingest.py)
├── chunking.py        # Splits extracted text into chunks
├── extract_books.py   # Extracts text from PDF files
├── ingest.py           # One-time script: extracts, chunks, embeds, stores books
├── main.py             # FastAPI server exposing the /api/chat endpoint
├── requirements.txt    # Python dependencies
└── .gitignore
```

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed on your machine

## Setup instructions

### 1. Install Ollama and pull a model

Download and install Ollama from [ollama.com](https://ollama.com), then pull a model:

```bash
ollama pull llama3.1:8b
```

If your machine has limited RAM, use a smaller model instead:

```bash
ollama pull llama3.2:3b
```

If you use the smaller model, update the `model` name in `main.py` accordingly.

### 2. Clone the repo and set up a virtual environment

```bash
git clone https://github.com/yourusername/rag.git
cd rag
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist yet, install manually:

```bash
pip install fastapi uvicorn chromadb ollama sentence-transformers pymupdf python-dotenv
```

### 4. Add your books

Create a `books/` folder in the project root (if not already present) and add your PDF files:

```
books/
├── book1.pdf
├── book2.pdf
└── book3.pdf
```

> Note: Books are excluded from this repo via `.gitignore`. If they're copyrighted material, do not commit them to a public repository.

### 5. Run ingestion (one-time step)

This extracts, chunks, embeds, and stores your books in the local vector database:

```bash
python ingest.py
```

This will take a few minutes depending on book length. Re-run this only if you add or change books.

### 6. Start the API server

```bash
uvicorn main:app --reload --port 8000
```

### 7. Test it

Open `http://localhost:8000/docs` in your browser — this gives you an interactive UI to test the `/api/chat` endpoint directly.

Try a POST request to `/api/chat`:

```json
{
  "question": "What is quantum superposition?"
}
```

Expected response:

```json
{
  "answer": "...",
  "sources": ["Book1", "Book2"]
}
```

## Connecting to a frontend

The FastAPI backend is CORS-enabled for `http://localhost:3000` by default — update the `allow_origins` list in `main.py` to match your frontend's URL (including your production domain once deployed).

## Troubleshooting

| Error | Likely cause | Fix |
|---|---|---|
| `model 'X' not found (404)` | Model wasn't pulled | Run `ollama pull <model-name>` |
| `listen tcp 127.0.0.1:11434: bind` on `ollama serve` | Ollama is already running in the background | This is expected — no action needed, just check `ollama list` |
| Empty/irrelevant answers | Books weren't ingested | Re-run `python ingest.py` and confirm it completes without errors |
| 500 Internal Server Error | Check the terminal running `uvicorn`, not the browser | The full Python traceback appears there |

## Notes

- This project runs entirely locally — no data leaves your machine, and there are no API costs.
- To deploy this publicly, Ollama needs a machine with sufficient RAM (a small VPS, e.g. Hetzner or DigitalOcean, works well) since most free hosting platforms don't support running local LLMs.
