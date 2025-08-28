from typing import List, Dict
import chromadb, os
from chromadb.utils import embedding_functions

from infrastructure.config import settings


class RAGPipeline:
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_function = None

    def init_blocking(self):
        print("Initializing RAGPipeline...")
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        print("ChromaDB client initialized.")
        self.embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        )
        print("Embedding function initialized.")
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        print("ChromaDB collection initialized.")

    def retrieve(self, user_text: str) -> Dict:
        # 1) vector search
        res = self.collection.query(
            query_texts=[user_text],
            n_results=settings.RAG_TOP_K_VECTOR,
            include=["metadatas","documents","distances"]
        )

        # 2) pick top few for LLM context
        picks = []
        for i in range(min(settings.RAG_TOP_K_LLM_CONTEXT, len(res["ids"][0]))):
            meta = res["metadatas"][0][i] or {}
            doc  = res["documents"][0][i] or ""
            dist = res["distances"][0][i]
            picks.append({
                "title": meta.get("title",""),
                "tags": meta.get("tags", ""),
                "snippet": doc[:400]
            })

        # rag_summary_text = "Candidați potriviți: " + ", ".join([p["title"] for p in picks if p["title"]])

        return {
            "query": user_text,
            "full_results": res,
            "picks": picks
        }
