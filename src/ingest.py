"""Load policy PDFs into LangChain Documents; preserve source and 1-based page numbers."""
import hashlib
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PDF_DIR = Path("data/policies")

def load_chunks(folder: Path = PDF_DIR):
    paths = sorted(folder.glob("*.pdf"))
    if not paths:
        raise RuntimeError(f"No PDFs under {folder}. Copy your approved policy briefs there.")
    pages = []
    for path in paths:
        loaded = PyPDFLoader(str(path), mode="page").load()
        if not loaded:
            raise ValueError(f"No pages extracted from {path.name}")
        for page in loaded:
            if not page.page_content.strip():
                raise ValueError(f"Unreadable/empty page in {path.name}, page {page.metadata.get('page', 0)+1}")
            page.metadata.update(filename=path.name, page_number=int(page.metadata.get("page", 0))+1,
                                 source=str(path), title=path.stem)
            pages.append(page)
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(pages)
    per_page = {}
    for ch in chunks:
        key = (ch.metadata["filename"], ch.metadata["page_number"])
        per_page[key] = per_page.get(key, 0)+1
        ch.metadata["chunk_index"] = per_page[key]
        digest = hashlib.sha256((ch.metadata["filename"]+str(ch.metadata["page_number"])+
                  str(ch.metadata["chunk_index"])+ch.page_content).encode()).hexdigest()[:16]
        ch.metadata["chunk_id"] = f"{Path(ch.metadata['filename']).stem}_p{ch.metadata['page_number']}_c{per_page[key]}_{digest}"
    print(f"PDFs: {len(paths)} | Pages: {len(pages)} | Chunks: {len(chunks)}")
    return chunks

if __name__ == "__main__":
    docs = load_chunks()
    print("Sample:", docs[0].metadata, docs[0].page_content[:200])
