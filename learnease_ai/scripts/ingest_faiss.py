import os
import json
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from app.ai.config import CHUNKS_FILE, EMB_PATH, FAISS_DIR, LOCAL_EMBED_MODEL
from app.ai.indexer import build_faiss_from_memmap


def load_chunks(chunks_file):
    """Stream all chunks from JSONL into a list of (id, text)."""
    ids = []
    texts = []
    with open(chunks_file, "r", encoding="utf-8") as fr:
        for line in fr:
            obj = json.loads(line)
            ids.append(obj["id"])
            texts.append(obj["text"])   
    return ids, texts


if __name__ == "__main__":
    print("Using CHUNKS_FILE:", CHUNKS_FILE)
    print("Using EMB_PATH:", EMB_PATH)
    print("Using FAISS_DIR:", FAISS_DIR)
    os.makedirs(os.path.dirname(EMB_PATH), exist_ok=True)
    os.makedirs(FAISS_DIR, exist_ok=True)

    # 1) Load chunks
    print("Loading chunks...")
    ids, texts = load_chunks(CHUNKS_FILE)
    n = len(texts)
    print(f"Total chunks: {n}")

    # 2) Load embedding model
    print(f"Loading embedding model: {LOCAL_EMBED_MODEL}")
    embed_model = SentenceTransformer(LOCAL_EMBED_MODEL)

    # 3) Compute embeddings in batches and stack into a float32 matrix
    BATCH = 256
    all_embs = []
    for i in tqdm(range(0, n, BATCH), desc="Batches"):
        batch_texts = texts[i : i + BATCH]
        embs = embed_model.encode(
            batch_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        # ensure float32
        embs = embs.astype("float32")
        all_embs.append(embs)

    # Stack to (N, D)
    emb_matrix = np.vstack(all_embs).astype("float32")
    print("Final embedding matrix shape:", emb_matrix.shape)

    # 4) Save to .npy in proper numeric format
    np.save(EMB_PATH, emb_matrix)
    print(f"Embeddings saved to {EMB_PATH}")

    # 5) Build FAISS index from this numeric file
    print("Building FAISS index...")
    build_faiss_from_memmap(emb_path=EMB_PATH, chunks_file=CHUNKS_FILE, out_dir=FAISS_DIR)
    print("FAISS index built successfully.")
