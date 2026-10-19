from src.ingest import load_chunks
from src.store import upload

def main():
    docs = load_chunks()
    count = upload(docs)
    print(f"Upserted {count} chunks (stable IDs). No index was recreated.")

if __name__ == "__main__":
    main()
