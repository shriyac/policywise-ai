"""Reports conservative descriptive metrics from reviewed CSV; blank scores are excluded."""
import csv
from pathlib import Path

def report(path=Path('evaluation/results.csv')):
    with path.open(newline='') as f: rows=list(csv.DictReader(f))
    print('Total:',len(rows),'status counts:',{s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})})
    for field in ('manual_hit_at_5','manual_faithfulness','manual_citation_support'):
        vals=[float(r[field]) for r in rows if r.get(field,'').strip() in ('0','1','0.0','1.0')]
        print(field, f'{sum(vals):.0f}/{len(vals)}' if vals else 'not manually scored')

if __name__ == '__main__':report()
