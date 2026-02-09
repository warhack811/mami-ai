import chromadb
from chromadb.config import Settings
from app.core.config import settings

class VectorStoreService:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                self._client = chromadb.HttpClient(
                    host=settings.CHROMA_DB_HOST,
                    port=int(settings.CHROMA_DB_PORT)
                )
            except Exception as e:
                print(f"Failed to connect to ChromaDB: {e}")
                # Fallback to ephemeral client for testing/dev if server is down?
                # Or just raise/return None
                pass
        return self._client

    def get_collection(self, user_id: str):
        if not self.client:
            return None
        return self.client.get_or_create_collection(name=f"user_{user_id}")

    def add_documents(self, user_id: str, documents: list, metadatas: list):
        collection = self.get_collection(user_id)
        if collection:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=[str(hash(doc)) for doc in documents] # Simple hash ID
            )

    def query(self, user_id: str, query_text: str, n_results: int = 5):
        collection = self.get_collection(user_id)
        if collection:
            return collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
        return {"documents": [], "metadatas": []}

vector_store = VectorStoreService()
