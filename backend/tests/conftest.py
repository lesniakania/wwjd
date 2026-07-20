import os


# Keep unit tests deterministic and offline; production uses real multilingual embeddings.
os.environ["EMBEDDING_MODEL"] = ""
os.environ["HF_TOKEN"] = ""
