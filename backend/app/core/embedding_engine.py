from sentence_transformers import SentenceTransformer

# We use the miniLM as specified
# Load it lazy to avoid slowing down imports
_model = None

def get_embedding(text: str) -> list[float]:
    global _model
    if _model is None:
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model.encode(text).tolist()
