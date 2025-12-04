import os, json, numpy as np
import faiss

from .config import FAISS_DIR, CHUNKS_FILE, EMB_PATH

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def load_chunks_map(path=CHUNKS_FILE):
    m = {}
    with open(path, "r", encoding="utf-8") as fr:
        for line in fr:
            obj = json.loads(line)
            m[obj["id"]] = obj
    return m

def build_faiss_from_memmap(emb_path=EMB_PATH, chunks_file=CHUNKS_FILE, out_dir=FAISS_DIR):
    ensure_dir(out_dir)
    embs = np.load(emb_path, mmap_mode='r')
    N, d = embs.shape
    index = faiss.IndexFlatIP(d)   # using inner product on normalized embeddings
    index.add(np.array(embs, dtype=np.float32))
    faiss.write_index(index, os.path.join(out_dir, "index.faiss"))
    ids = []
    with open(chunks_file, "r", encoding="utf-8") as fr:
        for line in fr:
            obj = json.loads(line)
            ids.append(obj["id"])
    np.save(os.path.join(out_dir, "ids.npy"), np.array(ids, dtype=object))
    return index, ids

def load_faiss_index(index_dir=FAISS_DIR):
    idx_file = os.path.join(index_dir, "index.faiss")
    ids_file = os.path.join(index_dir, "ids.npy")
    if not os.path.exists(idx_file) or not os.path.exists(ids_file):
        raise FileNotFoundError("FAISS index or ids.npy missing")
    index = faiss.read_index(idx_file)
    ids = np.load(ids_file, allow_pickle=True)
    return index, ids

def faiss_search(index, ids, query_emb, top_k=6):
    import numpy as np
    q = np.asarray(query_emb, dtype=np.float32).reshape(1, -1)
    D, I = index.search(q, top_k)
    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx < 0:
            continue
        results.append({"id": ids[idx].item() if hasattr(ids[idx],"item") else ids[idx], "dist": float(dist)})
    return results
