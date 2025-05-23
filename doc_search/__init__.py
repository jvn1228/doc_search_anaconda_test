from fastapi import FastAPI, HTTPException
from .store import DocumentStore, StoreError
from .models import Document

app = FastAPI()
store = DocumentStore()

@app.post("/documents/{doc_id}")
def insert_document(doc_id: str, document: Document):
    try:
        store.upsert(doc_id, document)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    try:
        store.delete(doc_id)
    except StoreError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/deleted")
def get_deleted_ids() -> list[str]:
    try:
        return store.get_deleted_ids()
    except StoreError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
def search(keyword: str) -> list[str]:
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")
    
    try:
        return store.search(keyword)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    