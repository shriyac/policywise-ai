import sys
from src.store import search

def main():
    question = " ".join(sys.argv[1:]) or "What is GitLab's paid time off policy?"
    for i, (doc, score) in enumerate(search(question), 1):
        print(f"\n#{i} score={score:.4f} file={doc.metadata.get('filename')} page={doc.metadata.get('page_number')} id={doc.metadata.get('chunk_id')}")
        print(doc.page_content[:600])

if __name__ == "__main__":
    main()
