from .embedder import embed_text
from .indexer import load_faiss_index, load_chunks_map, faiss_search
from .llm_provider import call_openai, call_gemini, call_local
from .config import CHUNKS_FILE

_index = None
_ids = None
_chunks_map = None

PROMPT_TEMPLATE = """You are an exam assistant. Use ONLY the CONTEXT below to write an exam-friendly {marks}-mark answer.

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- Use textbook text where it fits; if context is messy, say "Supplemented by model knowledge".
- Output should be concise, exam-friendly, with a source citation [Book — p.X] where applicable.
Answer:
"""

def init_all():
    global _index, _ids, _chunks_map
    if _chunks_map is None:
        _chunks_map = load_chunks_map(CHUNKS_FILE)
    if _index is None:
        _index, _ids = load_faiss_index()
    return _index, _ids, _chunks_map

def build_context(retrieved):
    ctx = ""
    for i, r in enumerate(retrieved):
        meta = r.get('meta', r)
        ctx += f"[{i+1}] {meta.get('book')} — p.{meta.get('page')}\n{meta.get('text')}\n\n"
        if meta.get('figures'):
            for f in meta.get('figures'):
                ctx += f"Figure: {f.get('figure_id')} caption: {(f.get('caption') or '')[:200]}\n"
    return ctx

def ask(question, marks=5, top_k=6, prefer=None):
    try:
        index, ids, chunks_map = init_all()
        q_emb = embed_text(question)
        hits = faiss_search(index, ids, q_emb, top_k=top_k)
        enriched = []
        for h in hits:
            meta = chunks_map.get(h['id'], {})
            enriched.append({**h, 'meta': meta})
        context = build_context(enriched)
        prompt = PROMPT_TEMPLATE.format(context=context, question=question, marks=marks)
        # try chosen provider then fallbacks
        if prefer == "openai":
            try: return {"answer": call_openai(prompt), "provider":"openai", "sources": enriched}
            except Exception: pass
        if prefer == "gemini":
            try: return {"answer": call_gemini(prompt), "provider":"gemini", "sources": enriched}
            except Exception: pass
        # fallback
        try: return {"answer": call_openai(prompt), "provider":"openai", "sources": enriched}
        except Exception:
            try: return {"answer": call_gemini(prompt), "provider":"gemini", "sources": enriched}
            except Exception:
                return {"answer": call_local(prompt), "provider":"local", "sources": enriched}
    except Exception as e:
        return {"error": str(e)}
