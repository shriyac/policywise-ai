"""Captures LIVE execution outcomes; never fabricates relevance or faithfulness labels."""
import csv
import json
import time
from pathlib import Path
from src.graph import ask

ROOT = Path(__file__).parent

def run():
    with (ROOT/'questions.csv').open(newline='') as f:
        questions = list(csv.DictReader(f))
    rows = []
    for q in questions:
        start = time.perf_counter()
        try:
            result = ask(q['question'])
            status, answer = result.get('status', 'unknown'), result.get('answer', '')
            chunks = [d.get('id') for d in result.get('retrieved', [])]
            citations = [c.get('chunk_id') for c in result.get('citations', [])]
            error = ''
        except Exception as ex:
            status, answer, chunks, citations, error = 'error', '', [], [], type(ex).__name__
        rows.append(dict(id=q['id'], category=q['category'], question=q['question'],
                         status=status, answer=answer, retrieved_chunk_ids=json.dumps(chunks),
                         citation_chunk_ids=json.dumps(citations), latency_seconds=round(time.perf_counter()-start, 3),
                         error_type=error, manual_hit_at_5='', manual_faithfulness='', manual_citation_support='', reviewer_notes=''))
        print(q['id'], status)
    with (ROOT/'results.csv').open('w', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    print('Saved evaluation/results.csv — manual evidence review is required before scoring.')

if __name__ == '__main__':run()
