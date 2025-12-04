 LearnEase AI Layer Setup Guide
LearnEase – AI Layer Setup Guide

This document explains how to set up and run the AI Answer Generation Layer locally.
You do NOT need to preprocess PDFs, generate embeddings, or build FAISS.
All required data files will be provided by the AI developer.

📌 1. Requirements

Before running the AI layer, install:

✔ Python 3.10 or above
✔ Git
✔ (Optional) Conda (or use Python venv)
📌 2. Clone the Repository
git clone <YOUR_REPO_URL>
cd LearnEase/learnease_ai

📌 3. Create & Activate Virtual Environment
On Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

On macOS/Linux
python3 -m venv venv
source venv/bin/activate


You should now see:

(venv) C:\Users\...\learnease_ai>

📌 4. Install Required Packages

Make sure you are inside the learnease_ai/ folder:

pip install -r requirements.txt

📌 5. Place the AI Data Files (VERY IMPORTANT)

The AI developer will give you a ZIP file containing:

all_chunks_with_pages.jsonl
embeddings.npy
index.faiss
ids.npy


Extract and place them exactly in the following paths:

learnease_ai/
 └── data/
     ├── cleaned/
     │    └── all_chunks_with_pages.jsonl
     ├── embeddings_store/
     │    └── embeddings.npy
     └── faiss_index/
          ├── index.faiss
          └── ids.npy


✔ DO NOT rename these files
✔ DO NOT rebuild them
✔ DO NOT delete FAISS or embeddings files

These files are the entire AI knowledge base.

📌 6. Create .env File

Inside learnease_ai/ create a file named .env:

OPENAI_API_KEY=
GENIE_API_KEY=
PREFERRED_PROVIDER=local

DATA_DIR=data
CHUNKS_FILE=data/cleaned/all_chunks_with_pages.jsonl
EMB_PATH=data/embeddings_store/embeddings.npy
FAISS_DIR=data/faiss_index

LOCAL_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
LOCAL_LLM=google/flan-t5-small


👉 If you don't have OpenAI or Gemini keys, leave them empty.
👉 The system will automatically fallback to LOCAL AI.

📌 7. Start the AI Server

Run:

python -m app.ai.server


You should see:

Loading chunks...
Loading FAISS index...
Server running on http://0.0.0.0:8700


This means the AI layer is active.

📌 8. Test API (Optional)

Use curl:

curl -s -X POST "http://127.0.0.1:8700/api/ask" ^
-H "Content-Type: application/json" ^
-d "{\"question\":\"Explain DFA minimization\",\"marks\":5,\"prefer_provider\":\"local\"}"


OR use Postman / Thunder Client.

You should receive a JSON response like:

{
  "answer": "...",
  "sources": [
    { "book": "Aho Compilers", "page": 209, "score": 0.57 }
  ],
  "time": 0.35
}

📌 9. Connecting With Flutter Frontend

Frontend should call:

POST http://<your-ai-server-ip>:8700/api/ask
Content-Type: application/json

{
  "question": "Explain DFA minimization",
  "marks": 5,
  "prefer_provider": "local"
}


Response:

{
  "answer": "... formatted answer ...",
  "sources": [...],
  "time": 0.32
}


⚠ The frontend NEVER does embeddings, preprocessing, or FAISS operations.

📌 10. Important Notes
❌ Do NOT run scripts/ingest_faiss.py
❌ Do NOT place PDFs in raw/
❌ Do NOT regenerate embeddings
❌ Do NOT rebuild FAISS
✔ Only run python -m app.ai.server

Because the entire knowledge base is already built and provided.

📌 11. Folder Structure Summary
learnease_ai/
 ├── app/
 │   ├── ai/
 │   │   ├── server.py      # FastAPI server
 │   │   ├── rag_engine.py  # RAG logic
 │   │   ├── config.py      # Paths & model config
 │   │   └── models_local.py
 │   └── ...
 ├── data/
 │   ├── cleaned/
 │   ├── embeddings_store/
 │   └── faiss_index/
 ├── scripts/               # ingestion scripts (NOT used by teammates)
 ├── venv/
 ├── .env
 └── README.md
