# server.py -- LearnEase AI microservice (robust multi-provider)
import os
import json
import time
import inspect
from typing import List, Optional, Tuple

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import uvicorn

import numpy as np
import faiss

# load .env if present
from dotenv import load_dotenv
load_dotenv()

# ---------------- Config ----------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(ROOT, "..", "data"))
CHUNKS_FILE = os.getenv("CHUNKS_FILE", os.path.join(DATA_DIR, "cleaned", "all_chunks_with_pages.jsonl"))
FAISS_DIR = os.getenv("FAISS_DIR", os.path.join(DATA_DIR, "faiss_index"))
EMB_PATH = os.getenv("EMB_PATH", os.path.join(DATA_DIR, "embeddings_store", "embeddings.npy"))
EMBED_MODEL = os.getenv("LOCAL_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LOCAL_LLM = os.getenv("LOCAL_LLM", "google/flan-t5-small")
ALLOW_LOCAL_FALLBACK = os.getenv("ALLOW_LOCAL_FALLBACK", "true").lower() in ("1", "true", "yes")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# FastAPI
app = FastAPI(title="LearnEase AI service (robust)")

# ---------------- Load resources ----------------
print("Loading chunks from:", CHUNKS_FILE)
chunks = []
try:
    with open(CHUNKS_FILE, "r", encoding="utf-8") as fr:
        for line in fr:
            obj = json.loads(line)
            chunks.append(obj)
except Exception as e:
    raise RuntimeError(f"Failed to load chunks file {CHUNKS_FILE}: {e}")
print("Total chunks loaded =", len(chunks))

index_file = os.path.join(FAISS_DIR, "index.faiss")
if not os.path.exists(index_file):
    raise RuntimeError("FAISS index not found at: " + index_file)
print("Loading FAISS index:", index_file)
index = faiss.read_index(index_file)

if not os.path.exists(EMB_PATH):
    raise RuntimeError("Embedding memmap not found at: " + EMB_PATH)
print("Loading embeddings header:", EMB_PATH)
embs_mmap = np.load(EMB_PATH, mmap_mode="r")
if len(embs_mmap.shape) != 2:
    raise RuntimeError("Unexpected embeddings shape: " + str(embs_mmap.shape))
emb_dim = embs_mmap.shape[1]
print("Embedding dim:", emb_dim)

print("Loading embedding model:", EMBED_MODEL)
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer(EMBED_MODEL)
except Exception as e:
    raise RuntimeError(f"Failed to load embedding model '{EMBED_MODEL}': {e}")

# ---------------- Request model ----------------
class AskRequest(BaseModel):
    question: str
    marks: Optional[int] = 5
    top_k: Optional[int] = 6
    prefer_provider: Optional[str] = "openai"  # openai | gemini | local | any

# ---------------- Retrieval helper ----------------
def retrieve(question: str, top_k: int = 6) -> List[Tuple[float, dict]]:
    q_emb = embedder.encode(question)
    q_emb = np.array(q_emb, dtype="float32")
    if q_emb.ndim == 1:
        q_emb = q_emb.reshape(1, -1)
    D, I = index.search(q_emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(chunks):
            continue
        results.append((float(score), chunks[idx]))
    return results

# ---------------- Context decision & prompt builder ----------------
def decide_context_usage(retrieved: List[Tuple[float, dict]]):
    qualities = []
    for score, ch in retrieved:
        q = ch.get("quality")
        if q is None:
            continue
        try:
            qualities.append(float(q))
        except:
            pass
    if not qualities:
        avg = 0.5
    else:
        avg = float(sum(qualities) / len(qualities))
    if avg >= 0.7:
        instr = "Context looks high-quality. Use it as primary source and cite pages."
    elif avg >= 0.4:
        instr = "Context is mixed. Use it where helpful; use general knowledge where context is broken."
    else:
        instr = "Context is low-quality. Use general knowledge to produce a clean answer; mark cited pages as candidate sources with confidence."
    return avg, instr

def build_prompt(question: str, marks: int, retrieved: List[Tuple[float, dict]]):
    avg_q, context_instr = decide_context_usage(retrieved)
    context_lines = []
    for score, ch in retrieved:
        txt = ch.get("text", "").replace("\n", " ").strip()
        if len(txt) > 900:
            txt = txt[:900] + "..."
        qtag = f" (quality={ch.get('quality')})" if ch.get('quality') is not None else ""
        context_lines.append(f"[Source: {ch.get('book')} — Page {ch.get('page')}{qtag}] {txt}")
    context = "\n\n".join(context_lines)
    prompt = f"""
You are LearnEase — an exam answer assistant.

Context quality average: {avg_q:.2f}
Context guidance: {context_instr}

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Write a {marks}-mark concise textbook/exam answer.
- If the context is broken, use general knowledge to produce a correct, well-formatted answer.
- Still attempt to list candidate sources (book + page) with confidence (0.0-1.0).
- Format: brief definition -> bullet key points -> short example (if relevant) -> conclusion.
Answer:
"""
    return prompt

# ---------------- Local LLM ----------------
def call_local(prompt: str) -> str:
    if not ALLOW_LOCAL_FALLBACK:
        raise RuntimeError("Local fallback disabled by ALLOW_LOCAL_FALLBACK")
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import torch
    except Exception as e:
        raise RuntimeError(f"transformers/torch not installed or failed: {e}")
    model_name = os.getenv("LOCAL_LLM", LOCAL_LLM)
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    inputs = tok(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
    gen = model.generate(**inputs, max_new_tokens=512, do_sample=False)
    text = tok.batch_decode(gen, skip_special_tokens=True)[0]
    return text

# ---------------- OpenAI caller (robust) ----------------
def call_openai(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if not key:
        return None, None
    model_name = os.getenv("OPENAI_MODEL", OPENAI_MODEL)
    # 1) Try the new OpenAI client (openai.OpenAI)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        # Try chat completions API on new client
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.2,
            )
            # parse common shapes
            if hasattr(resp, "choices") and resp.choices:
                choice = resp.choices[0]
                if hasattr(choice, "message"):
                    msg = getattr(choice, "message")
                    if isinstance(msg, dict):
                        return msg.get("content"), "openai"
                # dict-like fallback
                if isinstance(choice, dict) and "message" in choice:
                    return choice["message"].get("content"), "openai"
            if isinstance(resp, dict) and "choices" in resp:
                return resp["choices"][0]["message"]["content"], "openai"
        except Exception as e:
            # If new client chat API shape not available, try responses.create
            print("OpenAI new client chat attempt failed, trying responses.create:", e)
            try:
                # some new clients support client.responses.create(...)
                resp2 = client.responses.create(model=model_name, input=prompt, max_tokens=600, temperature=0.2)
                # resp2 may have 'output' or 'choices' or 'content'
                if hasattr(resp2, "output") and resp2.output:
                    # join textual pieces if present
                    out = []
                    for item in resp2.output:
                        if isinstance(item, dict):
                            if "content" in item:
                                c = item["content"]
                                if isinstance(c, list):
                                    for sub in c:
                                        if isinstance(sub, dict) and "text" in sub:
                                            out.append(sub["text"])
                                        elif isinstance(sub, str):
                                            out.append(sub)
                                elif isinstance(c, str):
                                    out.append(c)
                    if out:
                        return " ".join(out), "openai"
                if isinstance(resp2, dict) and "output" in resp2:
                    # best-effort combine
                    return str(resp2), "openai"
            except Exception as e2:
                print("OpenAI new client responses.create also failed:", e2)
    except Exception as e:
        print("New OpenAI client not available or failed:", e)

    # 2) Try legacy openai package (older interface)
    try:
        import openai
        openai.api_key = key
        resp = openai.ChatCompletion.create(model=model_name, messages=[{"role":"user","content":prompt}], max_tokens=600, temperature=0.2)
        if "choices" in resp:
            return resp["choices"][0]["message"]["content"], "openai"
    except Exception as e:
        print("OpenAI legacy client failed:", e)
    return None, None

# ---------------- Gemini caller (robust) ----------------
def call_gemini(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GENIE_API_KEY")
    if not key:
        return None, None
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
    except Exception as e:
        print("google.generativeai import/config failed:", e)
        return None, None

    # pick a model from list if possible
    model_name = os.getenv("GEMINI_MODEL")
    try:
        models_iter = genai.list_models()
        model_names = [m.name for m in models_iter] if models_iter is not None else []
        if not model_name and model_names:
            # prefer suitable models
            for cand in ["models/gemini-2.5-pro", "models/gemini-2.5-flash", "models/gemini-2.0-pro", "models/gemini-1.5-mini"]:
                if cand in model_names:
                    model_name = cand
                    break
            if not model_name:
                model_name = model_names[0]
    except Exception as e:
        print("genai.list_models() failed (non-fatal):", e)
        model_name = model_name or "models/gemini-2.5-pro"

    # create generative model wrapper
    try:
        m = genai.GenerativeModel(model_name)
    except Exception as e:
        print("Failed to create GenerativeModel:", e)
        return None, None

    # generate_content: different SDK versions accept different signatures.
    # We'll introspect the method signature and call accordingly.
    try:
        gen_fn = getattr(m, "generate_content")
        sig = None
        try:
            sig = inspect.signature(gen_fn)
        except Exception:
            sig = None

        # try safe call patterns in order until one works
        tries = []

        def try_call_positional():
            # some SDKs accept single positional 'prompt' or 'content'
            try:
                return gen_fn(prompt)
            except Exception as e:
                raise e

        def try_call_kwargs_safe():
            # some SDKs accept 'prompt' as keyword; others accept 'content' or 'messages'
            try:
                return gen_fn(prompt=prompt)
            except TypeError:
                pass
            try:
                return gen_fn(content=prompt)
            except TypeError:
                pass
            try:
                return gen_fn(contents=[prompt])
            except TypeError:
                pass
            try:
                # older form: gen_fn(prompt, max_output_tokens=..., temperature=...)
                return gen_fn(prompt, max_output_tokens=800)
            except Exception:
                raise

        # 1) positional
        try:
            resp = try_call_positional()
        except Exception as e_pos:
            tries.append(("positional", str(e_pos)))
            # 2) kwargs variations
            try:
                resp = try_call_kwargs_safe()
            except Exception as e_kw:
                tries.append(("kwargs", str(e_kw)))
                # 3) try with a simple dictionary call if permitted
                try:
                    resp = gen_fn({"prompt": prompt})
                except Exception as e_dict:
                    tries.append(("dict", str(e_dict)))
                    raise RuntimeError("All Gemini call styles failed: " + str(tries))
    except Exception as e:
        print("Gemini call exception:", e)
        return None, None

    # parse response robustly
    try:
        if hasattr(resp, "text") and isinstance(resp.text, str):
            return resp.text, "gemini"

        if hasattr(resp, "candidates") and resp.candidates:
            c0 = resp.candidates[0]
            if isinstance(c0, dict):
                for k in ("content", "output", "text"):
                    if k in c0 and isinstance(c0[k], str):
                        return c0[k], "gemini"
            if hasattr(c0, "content") and isinstance(c0.content, str):
                return c0.content, "gemini"

        if hasattr(resp, "output") and resp.output:
            # often resp.output[0].content -> list of dicts with 'text'
            first = resp.output[0]
            if isinstance(first, dict) and "content" in first:
                contents = first["content"]
                if isinstance(contents, list) and contents:
                    pieces = []
                    for c in contents:
                        if isinstance(c, dict) and "text" in c:
                            pieces.append(c["text"])
                        elif isinstance(c, str):
                            pieces.append(c)
                    if pieces:
                        return " ".join(pieces), "gemini"

        # fallback to string
        return str(resp), "gemini"
    except Exception as e:
        print("Failed to parse Gemini response:", e)
        return None, None

# ---------------- Router: try providers in order ----------------
def call_llm_with_fallback(prompt: str, prefer: str = "openai") -> Tuple[str, str]:
    prefer = (prefer or "openai").lower()
    order = []
    if prefer == "openai":
        order = [call_openai, call_gemini, (lambda p: (call_local(p), "local") if ALLOW_LOCAL_FALLBACK else (None, None))]
    elif prefer == "gemini":
        order = [call_gemini, call_openai, (lambda p: (call_local(p), "local") if ALLOW_LOCAL_FALLBACK else (None, None))]
    elif prefer == "local":
        order = [(lambda p: (call_local(p), "local")), call_openai, call_gemini]
    else:
        order = [call_openai, call_gemini, (lambda p: (call_local(p), "local") if ALLOW_LOCAL_FALLBACK else (None, None))]

    tried = []
    for fn in order:
        try:
            if fn == call_openai:
                text, prov = call_openai(prompt)
            elif fn == call_gemini:
                text, prov = call_gemini(prompt)
            else:
                # lambda wrappers
                res = fn(prompt)
                if isinstance(res, tuple) and len(res) == 2 and isinstance(res[0], tuple):
                    # rare wrapper shape
                    text, prov = res[0][0], res[1]
                else:
                    text, prov = res
        except Exception as e:
            print(f"Provider {getattr(fn,'__name__',str(fn))} raised error:", e)
            text, prov = None, None
        tried.append(prov or "none")
        if text:
            return text, prov or "unknown"
    raise RuntimeError(f"No LLM provider available. Tried: {tried}")

# ---------------- API endpoint ----------------
@app.post("/api/ask")
def ask(req: AskRequest):
    start = time.time()
    if not req.question:
        raise HTTPException(status_code=400, detail="question required")

    retrieved = retrieve(req.question, top_k=req.top_k or 6)
    if not retrieved:
        raise HTTPException(status_code=404, detail="No retrieval results found")

    prompt = build_prompt(req.question, req.marks or 5, retrieved)

    try:
        text, provider = call_llm_with_fallback(prompt, prefer=(req.prefer_provider or "openai"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")

    elapsed = time.time() - start
    sources = []
    for i, (score, ch) in enumerate(retrieved[:6]):
        conf = None
        q = ch.get("quality")
        try:
            conf = float(q) if q is not None else None
        except:
            conf = None
        sources.append({
            "book": ch.get("book"),
            "page": ch.get("page"),
            "raw_score": float(score),
            "quality": conf
        })

    return {
        "answer": text,
        "provider": provider,
        "sources": sources,
        "time": elapsed,
    }

# ---------------- Optional: configure Gemini SDK at startup if key present ----------------
try:
    import google.generativeai as genai  # may fail, that's okay
    GENIE_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GENIE_API_KEY")
    if GENIE_KEY:
        genai.configure(api_key=GENIE_KEY)
except Exception:
    pass

# ---------------- Run server ----------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8700)))
