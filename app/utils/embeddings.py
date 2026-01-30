from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once (lazy loading could be better but sticking to simple for now)
try:
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Embedding model loaded.")
except Exception as e:
    print(f"Failed to load embedding model: {e}")
    model = None

def embed(text: str):
    """
    Generates a 384-dim embedding for the given text.
    """
    if not model:
        return [0.0] * 384
        
    try:
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * 384
