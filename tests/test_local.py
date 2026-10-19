from pathlib import Path
from src.config import INDEX, NAMESPACE
from src.ingest import load_chunks

def test_settings_defaults():
    assert INDEX
    assert NAMESPACE

def test_ingestion_has_unique_ids_if_pdfs_present():
    folder=Path('data/policies')
    if any(folder.glob('*.pdf')):
        docs=load_chunks(folder)
        ids=[d.metadata['chunk_id'] for d in docs]
        assert len(ids)==len(set(ids))
        assert all(d.metadata['page_number']>=1 for d in docs)
