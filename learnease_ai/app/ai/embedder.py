from sentence_transformers import SentenceTransformer
from .config import LOCAL_EMBED_MODEL
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(LOCAL_EMBED_MODEL)
    return _model

def embed_text(text):
    m = get_model()
    emb = m.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0]
    return emb

def embed_texts(texts, batch_size=32):
    m = get_model()
    return m.encode(texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
