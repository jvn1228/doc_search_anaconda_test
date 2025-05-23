from dataclasses import dataclass, field
from .models import Document

# To do: distinguish store errors from incorrect input
# versus internal error
class StoreError(Exception):
    def __init__(self, message: str):
        self.message = message

@dataclass
class DocumentStore:
    """
        In memory document store with index for keyword search

        The index contains document tokens generated during insert associated
        with the specific document. The current scope is limited to whole word
        search and the index is O(1) for matching whole keywords (at the expense
        of memory)
    """
    active_documents: dict[str, Document] = field(default_factory=dict)
    deleted_documents: dict[str, Document] = field(default_factory=dict)
    index: dict[str, list[str]] = field(default_factory=dict)

    def add_index(self, id: str, document: Document):
        """
        Index document with tokens derived from basic white space splitting
        Does not currently have a keyword minimum length
        """
        tokens = document.content.split()

        for token in tokens:
            token = token.lower()
            if token not in self.index:
                self.index[token] = []

            self.index[token].append(id)

    def delete_index(self, id: str):
        """
        Delete document id and unique tokens from index.
        
        This can be an expensive operation. An alternative
        can be to filter deleted documents from results

        Args:
            id (str): ID of document to delete
        """
        tokens_to_delete: list[str] = []

        for token in self.index:
            if id in self.index[token]:
                self.index[token].remove(id)

                if self.index[token] == []:
                    tokens_to_delete.append(token)

        for token in tokens_to_delete:
            del self.index[token]

    def search(self, keyword: str) -> list[str]:
        """
        Retrieves ids of documents that have been
        indexed to contain the keyword

        Args:
            keyword (str): Keyword to search for

        Returns:
            list[str]: List of document ids that contain the keyword
        """

        return self.index.get(keyword.lower(), [])

    def upsert(self, id: str, document: Document):
        """
        Insert or update document into store and add to index

        Args:
            document (Document): Document to upsert
        """
        if id in self.active_documents:
            self.delete_index(id)

        self.active_documents[id] = document

        self.add_index(id, document)
    
    def delete(self, id: str):
        """
        Delete document from store.

        Also deletes from index

        Args:
            id (str): ID of document to delete
        """
        if id not in self.active_documents:
            raise StoreError("Document does not exist")

        self.deleted_documents[id] = self.active_documents.pop(id)
        self.delete_index(id)
    
    def get_deleted_ids(self) -> list[str]:
        return list(self.deleted_documents.keys())
        
    def restore(self, id: str):
        """
        Restore document from deleted documents

        Args:
            id (str): ID of document to restore
        """
        if id not in self.deleted_documents:
            raise StoreError("Document does not exist")

        self.upsert(id, self.deleted_documents.pop(id))
        