import os
import sys
import json

# ensure project root in path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

import numpy as np

try:
    # monkeypatch embed_texts to avoid heavy model downloads
    import app.embeddings as embeddings
    import app.main as main
except Exception as e:
    print('Import error:', e)
    raise


def fake_embed_texts(texts):
    # return deterministic normalized vectors for testing
    dim = 64
    vecs = []
    for t in texts:
        h = sum(ord(c) for c in t) % 1000
        rng = np.random.RandomState(h)
        v = rng.rand(dim).astype('float32')
        v = v / (np.linalg.norm(v) + 1e-9)
        vecs.append(v)
    return np.vstack(vecs)


def run_test():
    embeddings.embed_texts = fake_embed_texts
    predictor = main.predictor
    predictor.load()
    print('Loaded', len(predictor.records), 'records')

    new = {
        'Nombre': 'Test Usuario',
        'edad': 30,
        'sexo': 'M',
        'Sintomas': 'Dolor de cabeza y fiebre'
    }

    out = predictor.add_and_predict(new, top_k=3)
    print('Add and predict output:')
    print(json.dumps(out, ensure_ascii=False, indent=2))

    # verify last record persisted
    data_path = os.path.join(ROOT, 'data', 'records.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    print('Total records after add:', len(records))


if __name__ == '__main__':
    run_test()
