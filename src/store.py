"""Pinecone vector store; bring-your-own 384-dimensional MiniLM vectors."""
from functools import lru_cache
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from src.config import INDEX, NAMESPACE, EMBED_MODEL, require_secret

@lru_cache(maxsize=1)
def embeddings():
    model = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    if len(model.embed_query("test")) != 384:
        raise RuntimeError("Embedding model is not 384-dimensional; check Pinecone index configuration")
    return model

@lru_cache(maxsize=1)
def vectorstore():
    pc = Pinecone(api_key=require_secret("PINECONE_API_KEY"))
    desc = pc.describe_index(INDEX)
    if int(desc.dimension) != 384 or str(desc.metric).lower() != "cosine":
        raise RuntimeError(f"Index {INDEX} must be 384-dimension cosine dense; found {desc.dimension}, {desc.metric}")
    return PineconeVectorStore(index_name=INDEX, embedding=embeddings(), namespace=NAMESPACE,
                               pinecone_api_key=require_secret("PINECONE_API_KEY"))

def upload(docs, batch_size=32):
    store = vectorstore()
    for start in range(0, len(docs), batch_size):
        batch = docs[start:start+batch_size]
        store.add_documents(batch, ids=[d.metadata['chunk_id'] for d in batch])
    return len(docs)

def search(question, k=5):
    return vectorstore().similarity_search_with_score(question, k=k)
