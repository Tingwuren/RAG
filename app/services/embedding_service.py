from functools import lru_cache
from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def _load_model(model_path="./models/bge-m3"):
    return SentenceTransformer(model_path)

def get_embeddings(text, model_path="./models/bge-m3", dimensions=None):
    model = _load_model(model_path)
    embeddings = model.encode(text)
    return embeddings