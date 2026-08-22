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
        # simple vote weighted by similarity
        scores = {}
        for item in res:
            diag = item['meta'].get('Posible Diagnostico')
            scores[diag] = scores.get(diag, 0.0) + item['score']
        # sort
        preds = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return {'matches': res, 'predictions': [{'diagnostico': d, 'score': float(s)} for d, s in preds]}

    def save_records_to_file(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'records.json'))
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def add_and_predict(self, record: dict, top_k: int = 3):
        # predict using current index
        pred = self.predict(record, top_k=top_k)
        # choose top prediction if available
        top_diag = None
        if pred.get('predictions'):
            top_diag = pred['predictions'][0]['diagnostico']
        if not top_diag:
            top_diag = 'Desconocido'
        # attach possible diagnosis to record
        saved = record.copy()
        saved['Posible Diagnostico'] = top_diag
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
        return {'saved': saved, 'predictions': pred.get('predictions', [])}


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
