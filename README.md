# Medical Records Similarity App

Prototype app using FastAPI (backend), FAISS + sentence-transformers for embeddings and similarity, and a simple HTML/JS frontend plus a Streamlit dashboard.

Quick start:

1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the FastAPI app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Open the frontend at http://localhost:8000

4. (Optional) Run Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

Disclaimer: Prototype only. Not for clinical use.
