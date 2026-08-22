import numpy as np

_MODEL = None

def get_model(name: str = 'all-MiniLM-L6-v2'):
    global _MODEL
    if _MODEL is None:
        # lazy import to avoid heavy dependency at module import time
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(name)
    return _MODEL


def embed_texts(texts):
    model = get_model()
    emb = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    # normalize for cosine similarity
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms[norms==0] = 1.0
    emb = emb / norms
    return emb
