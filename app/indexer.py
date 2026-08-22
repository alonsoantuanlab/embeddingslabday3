import faiss
import numpy as np
from typing import List

class FAISSIndexer:
    def __init__(self, dim: int):
        self.dim = dim
        # use inner product on normalized vectors => cosine similarity
        self.index = faiss.IndexFlatIP(dim)
        self.id2meta = []

    def build(self, vectors: np.ndarray, metas: List[dict]):
        if vectors.dtype != np.float32:
            vectors = vectors.astype('float32')
        self.index.reset()
        self.index.add(vectors)
        self.id2meta = metas

    def query(self, vector: np.ndarray, top_k: int = 5):
        if vector.dtype != np.float32:
            vector = vector.astype('float32')
        if vector.ndim == 1:
            vector = vector.reshape(1, -1)
        D, I = self.index.search(vector, top_k)
        results = []
        for dist_row, idx_row in zip(D, I):
            row = []
            for dist, idx in zip(dist_row, idx_row):
                if idx < 0:
                    continue
                meta = self.id2meta[idx]
                row.append({'score': float(dist), 'meta': meta})
            results.append(row)
        return results
