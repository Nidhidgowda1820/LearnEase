import os
from dotenv import load_dotenv

# load .env from project root (if present)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, ".env"))

# Base data directory (can override in .env)
DATA_DIR = os.getenv("DATA_DIR", os.path.join(ROOT, "data"))
DATA_DIR = os.path.abspath(DATA_DIR)

# Files & directories (can override in .env)
CHUNKS_FILE = os.path.abspath(os.getenv(
    "CHUNKS_FILE",
    os.path.join(DATA_DIR, "cleaned", "all_chunks_with_pages.jsonl")
))

FAISS_DIR = os.path.abspath(os.getenv(
    "FAISS_DIR",
    os.path.join(DATA_DIR, "faiss_index")
))

EMB_PATH = os.path.abspath(os.getenv(
    "EMB_PATH",
    os.path.join(DATA_DIR, "embeddings_store", "embeddings.npy")
))

# Optional small helpers: create directories if missing (safe: exist_ok=True)
for d in (
    os.path.dirname(CHUNKS_FILE),
    FAISS_DIR,
    os.path.dirname(EMB_PATH),
):
    if d and not os.path.exists(d):
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            # ignore permission errors — calling code should surface problems
            pass

# API keys (set in .env or environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
GENIE_API_KEY = os.getenv("GENIE_API_KEY", None)

# Local model defaults (can override in .env)
LOCAL_EMBED_MODEL = os.getenv("LOCAL_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LOCAL_LLM = os.getenv("LOCAL_LLM", "google/flan-t5-small")

# Helpful debug info (optional — comment out if noisy)
def _debug_print():
    print("CONFIG ROOT:", ROOT)
    print("DATA_DIR:", DATA_DIR)
    print("CHUNKS_FILE:", CHUNKS_FILE)
    print("FAISS_DIR:", FAISS_DIR)
    print("EMB_PATH:", EMB_PATH)
    print("OPENAI_API_KEY set:", bool(OPENAI_API_KEY))
    print("GENIE_API_KEY set:", bool(GENIE_API_KEY))
    print("LOCAL_EMBED_MODEL:", LOCAL_EMBED_MODEL)
    print("LOCAL_LLM:", LOCAL_LLM)

# Uncomment to see config when module is imported (useful first-run)
# _debug_print()
