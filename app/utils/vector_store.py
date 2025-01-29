import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class VectorStore:
    def __init__(self):
        self.index = None
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunk_embeddings = []

    def create_index(self, chunks):
        """
        Creates a FAISS index for the document chunks.
        """
        self.chunk_embeddings = [self.model.encode(chunk) for chunk in chunks]
        embeddings_array = np.vstack(self.chunk_embeddings)
        self.index = faiss.IndexFlatL2(embeddings_array.shape[1])
        self.index.add(embeddings_array)

    def query(self, query_text, top_k=5):
        """
        Retrieves the top_k most relevant chunks for a given query.
        """
        query_embedding = self.model.encode(query_text).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)
        return [(self.chunk_embeddings[i], distances[i]) for i in indices[0]]