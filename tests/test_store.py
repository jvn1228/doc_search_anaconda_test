import pytest

from doc_search.store import DocumentStore, StoreError
from doc_search.models import Document

class TestDocumentStore:
    """Tests for the DocumentStore class."""

    def test_upsert(self):
        """Test upsert functionality."""
        store = DocumentStore()
        doc = Document(content="This is a test document")

        store.upsert("doc1", doc)
        
        # Check document is in active_documents
        assert "doc1" in store.active_documents
        assert store.active_documents["doc1"] == doc
        
        # Check index
        for token in ["this", "is", "a", "test", "document"]:
            assert "doc1" in store.index[token]

        # try inserting another doc
        doc2 = Document(content="This is another document")
        store.upsert("doc2", doc2)
        
        # Check document is in active_documents
        assert "doc2" in store.active_documents
        assert store.active_documents["doc2"] == doc2
        
        # Check index
        for token in ["this", "is", "another", "document"]:
            assert "doc2" in store.index[token]
        
        # Check that doc1 is still in index
        for token in ["this", "is", "a", "test", "document"]:
            assert "doc1" in store.index[token]

    def test_upsert_update(self):
        """Test updating an existing document."""
        store = DocumentStore()
        doc1 = Document(content="This is a test document")
        doc1_updated = Document(content="This is an updated document")
        
        store.upsert("doc1", doc1)
        store.upsert("doc1", doc1_updated)
        
        # Check document is updated
        assert store.active_documents["doc1"] == doc1_updated
        
        # Check index has been updated
        assert "doc1" in store.index["updated"]
        
        # The word "test" should no longer be in the index for this document
        assert "test" not in store.index

    def test_search(self):
        """Test search functionality."""
        store = DocumentStore()
        doc1 = Document(content="This is a test document")
        doc2 = Document(content="Another document with different words")
        
        store.upsert("doc1", doc1)
        store.upsert("doc2", doc2)
        
        # Search for words in doc1
        assert "doc1" in store.search("test")
        assert "doc1" not in store.search("another")
        
        # Search for words in doc2
        assert "doc2" in store.search("another")
        assert "doc2" not in store.search("test")
        
        # Search for common words
        assert set(store.search("document")) == {"doc1", "doc2"}
        
        # Search should be case-insensitive
        assert "doc1" in store.search("TEST")
        
        # Search for non-existent word
        assert store.search("nonexistent") == []

    def test_delete(self):
        """Test delete functionality."""
        store = DocumentStore()
        doc = Document(content="This is a test document")

        store.upsert("doc1", doc)
        store.delete("doc1")
        
        # Check document is removed from active_documents
        assert "doc1" not in store.active_documents
        
        # Check document is added to deleted_documents
        assert "doc1" in store.deleted_documents
        assert store.deleted_documents["doc1"] == doc

        # Index should now be empty too
        assert store.index == {}

    def test_get_deleted_ids(self):
        """Test get_deleted_ids functionality."""
        store = DocumentStore()
        doc1 = Document(content="Document 1")
        doc2 = Document(content="Document 2")
        
        store.upsert("doc1", doc1)
        store.upsert("doc2", doc2)
        store.delete("doc1")

        assert store.get_deleted_ids() == ["doc1"]
        
        store.delete("doc2")

        assert set(store.get_deleted_ids()) == {"doc1", "doc2"}

        # Check delete raises StoreError for non-existent document
        with pytest.raises(StoreError, match="Document does not exist"):
            store.delete("nonexistent")

    def test_restore(self):
        """Test restore functionality."""
        store = DocumentStore()
        doc = Document(content="This is a test document")
        
        store.upsert("doc1", doc)
        store.delete("doc1")
        store.restore("doc1")
        
        assert "doc1" in store.active_documents
        assert store.active_documents["doc1"] == doc
        assert "doc1" not in store.deleted_documents
        
        # Check restore raises StoreError for non-existent document
        with pytest.raises(StoreError, match="Document does not exist"):
            store.restore("nonexistent")

    # Index is tested above as well so this is redundant but kept
    # for completeness sake
    def test_add_index(self):
        """Test add_index functionality."""
        store = DocumentStore()
        doc = Document(content="This is a test")
        
        store.add_index("doc1", doc)
        
        assert "doc1" in store.index["this"]
        assert "doc1" in store.index["is"]
        assert "doc1" in store.index["a"]
        assert "doc1" in store.index["test"]

    def test_delete_index(self):
        """Test delete_index functionality."""
        store = DocumentStore()
        doc1 = Document(content="This is a test")
        doc2 = Document(content="This is another test")
        
        store.add_index("doc1", doc1)
        store.add_index("doc2", doc2)
        
        assert set(store.index["this"]) == {"doc1", "doc2"}
        
        store.delete_index("doc1")
        
        assert "doc1" not in store.index["this"]
        assert "doc2" in store.index["this"]
        
        assert "a" not in store.index
