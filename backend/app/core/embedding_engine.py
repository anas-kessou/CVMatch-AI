# app/core/embedding_engine.py
import numpy as np
from typing import List
from FlagEmbedding import FlagModel
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        # We load the BAAI/bge-m3 dense model.
        # Set use_fp16=True to speed up computation on supported devices.
        logger.info("Loading BAAI/bge-m3 model...")
        self.model = FlagModel('BAAI/bge-m3', 
                               query_instruction_for_retrieval="Represent this text for retrieving matching concepts: ",
                               use_fp16=True)
        logger.info("Successfully loaded bge-m3")

    def get_embedding(self, text: str) -> List[float]:
        """Compute the embedding vector for a given string."""
        if not text or not text.strip():
            return [0.0] * 1024 # bge-m3 produces 1024 dimension dense embeddings
            
        vector = self.model.encode(text)
        return vector.tolist()

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Fast retrieval cosine similarity score between two texts."""
        if not text1.strip() or not text2.strip():
            return 0.0
            
        v1 = self.model.encode(text1)
        v2 = self.model.encode(text2)
        
        # Calculate cosine similarity
        score = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return float(score)

embedding_service = EmbeddingService()

# For backward compatibility if other modules use the old method name
def get_embedding(text: str) -> List[float]:
    return embedding_service.get_embedding(text)
