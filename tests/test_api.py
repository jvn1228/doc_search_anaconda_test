import pytest
from fastapi.testclient import TestClient

from doc_search import app, store
from doc_search.models import Document

# Create a test client
client = TestClient(app)

# Reset the store before each test
@pytest.fixture(autouse=True)
def reset_store():
    # Reset the store by creating a new instance
    global store
    store.__init__()
    yield

class TestAPI:
    """Tests for the FastAPI application."""

    def test_insert_document(self):
        """Test POST /documents/{doc_id} endpoint."""
        # Insert a document
        response = client.post(
            "/documents/doc1",
            json={"content": "This is a test document"}
        )
        assert response.status_code == 200
        
        # Check document was inserted in the store
        assert store.active_documents["doc1"].content == "This is a test document"

    def test_delete_document(self):
        """Test DELETE /documents/{doc_id} endpoint."""
        # Insert a document first
        store.upsert("doc1", Document(content="This is a test document"))
        
        # Delete the document
        response = client.delete("/documents/doc1")
        assert response.status_code == 200

        # Check document is added to deleted_documents
        assert "doc1" in store.deleted_documents

    def test_delete_nonexistent_document(self):
        """Test DELETE /documents/{doc_id} with non-existent document."""
        # Try to delete a document that doesn't exist
        response = client.delete("/documents/nonexistent")
        assert response.status_code == 400
        assert "Document does not exist" in response.json()["detail"]

    def test_get_deleted_ids(self):
        """Test GET /documents/deleted endpoint."""
        # Initially no deleted documents
        response = client.get("/documents/deleted")
        assert response.status_code == 200
        assert response.json() == []
        
        # Insert and delete a document
        store.upsert("doc1", Document(content="This is a test document"))
        store.delete("doc1")
        
        # Get deleted IDs
        response = client.get("/documents/deleted")
        assert response.status_code == 200
        assert response.json() == ["doc1"]

    def test_search(self):
        """Test GET /search endpoint."""
        # Insert a document
        store.upsert("doc1", Document(content="This is a test document"))
        store.upsert("doc2", Document(content="This is another document"))
        
        # Search for "TEST"
        response = client.get("/search?keyword=TEST")
        assert response.status_code == 200
        # case insensitive
        assert response.json() == ["doc1"]
        
        # Search for "document" (both docs have it)
        response = client.get("/search?keyword=document")
        assert response.status_code == 200
        assert set(response.json()) == {"doc1", "doc2"}
        
        # Search for a non-existent word
        response = client.get("/search?keyword=nonexistent")
        assert response.status_code == 200
        assert response.json() == []
        
        # Search with empty keyword
        response = client.get("/search?keyword=")
        assert response.status_code == 400
        assert "Keyword must not be empty" in response.json()["detail"]
