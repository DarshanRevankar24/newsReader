
def embed(text: str):
    """
    Generates an embedding for the given text.
    Currently returns a dummy vector because no embedding model is configured.
    """
    # Return a 384-dimensional zero vector (common size for small models)
    return [0.0] * 384
