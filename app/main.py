from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import app.embeddings as embeddings
from app.indexer import FAISSIndexer
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'records.json')

app = FastAPI(title='Medical Records Similarity API')

app.mount('/static', StaticFiles(directory=os.path.join(os.path.dirname(__file__), '..', 'frontend')), name='static')


class RecordIn(BaseModel):
    Nombre: str
    edad: int
    sexo: str
    Sintomas: str


class Predictor:
    def __init__(self):
        self.records = []
        self.texts = []
        self.indexer = None
        self.dim = None

    def load(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'records.json'))
        with open(path, 'r', encoding='utf-8') as f:
            self.records = json.load(f)
        self.texts = [self._record_to_text(r) for r in self.records]
        vecs = embeddings.embed_texts(self.texts)
        self.dim = vecs.shape[1]
        self.indexer = FAISSIndexer(self.dim)
        self.indexer.build(vecs.astype('float32'), self.records)

    def _record_to_text(self, r):
        return f"Nombre: {r.get('Nombre')} Edad: {r.get('edad')} Sexo: {r.get('sexo')} Sintomas: {r.get('Sintomas')}"

    def predict(self, record: dict, top_k: int = 3):
        text = self._record_to_text(record)
        vec = embeddings.embed_texts([text])[0]
        res = self.indexer.query(vec.astype('float32'), top_k=top_k)[0]
        # enrich matches with percentage similarity
        # FAISS returns inner product on normalized vectors -> cosine similarity in [-1,1]
        # map to percentage: percent = (sim + 1) / 2 * 100
        scores = {}
        counts = {}
        enriched_matches = []
        for item in res:
            sim = float(item['score'])
            percent = (sim + 1.0) / 2.0 * 100.0
            meta = item['meta']
            enriched = {'score': sim, 'similarity_percent': round(percent, 2), 'meta': meta}
            enriched_matches.append(enriched)
            diag = meta.get('Posible Diagnostico')
            scores[diag] = scores.get(diag, 0.0) + sim
            counts[diag] = counts.get(diag, 0) + 1

        # aggregate per-diagnosis average similarity and sort
        preds = []
        for diag, total_sim in scores.items():
            avg_sim = total_sim / counts.get(diag, 1)
            percent = (avg_sim + 1.0) / 2.0 * 100.0
            preds.append({'diagnostico': diag, 'avg_score': float(avg_sim), 'similarity_percent': round(percent, 2)})
        preds = sorted(preds, key=lambda x: x['avg_score'], reverse=True)

        return {'matches': enriched_matches, 'predictions': preds}

    def save_records_to_file(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'records.json'))
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def add_and_predict(self, record: dict, top_k: int = 3):
        # predict using current index
        pred = self.predict(record, top_k=top_k)
        # choose top prediction if available
        top_diag = None
        top_percent = None
        if pred.get('predictions'):
            top = pred['predictions'][0]
            top_diag = top.get('diagnostico')
            top_percent = top.get('similarity_percent')
        if not top_diag:
            top_diag = 'Desconocido'
            top_percent = 0.0
        # attach possible diagnosis to record (include percent)
        saved = record.copy()
        saved['Posible Diagnostico'] = f"{top_diag} ({top_percent:.2f}%)"
        # append to in-memory records
        self.records.append(saved)
        # update texts and index incrementally
        text = self._record_to_text(saved)
        vec = embeddings.embed_texts([text])[0]
        # ensure indexer exists
        if self.indexer is None:
            self.dim = vec.shape[0]
            self.indexer = FAISSIndexer(self.dim)
            self.indexer.build(np.array([vec]).astype('float32'), [saved])
        else:
            self.indexer.add(vec.astype('float32'), saved)
        # persist to disk
        self.save_records_to_file()
        return {'saved': saved, 'predictions': pred.get('predictions', []), 'matches': pred.get('matches', [])}


predictor = Predictor()


@app.on_event('startup')
def startup_event():
    predictor.load()


@app.get('/records')
def get_records():
    return JSONResponse(predictor.records)


@app.post('/predict')
def predict(r: RecordIn):
    try:
        out = predictor.predict(r.dict(), top_k=5)
        return JSONResponse(out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/add_record')
def add_record(r: RecordIn):
    try:
        out = predictor.add_and_predict(r.dict(), top_k=5)
        return JSONResponse(out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/')
def index():
    # serve frontend page
    index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html'))
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read())
    return HTMLResponse('<html><body><h2>Frontend not found</h2></body></html>')
