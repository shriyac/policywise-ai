import os
from dotenv import load_dotenv
load_dotenv()
INDEX = os.getenv("PINECONE_INDEX_NAME", "policywise-index")
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "policywise-v1")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

def require_secret(key):
    value = os.getenv(key, "").strip()
    if not value:
        raise RuntimeError(f"Missing environment variable: {key}. Set it in Replit Secrets.")
    return value
