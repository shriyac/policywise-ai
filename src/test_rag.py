import sys
from src.graph import ask
if __name__ == '__main__':
    q = ' '.join(sys.argv[1:]) or 'What does the paid time off policy say?'
    result = ask(q)
    print('Status:', result.get('status'))
    print(result.get('answer'))
    for c in result.get('citations', []):
        print('Source:', c['filename'], 'page', c['page'], 'chunk', c['chunk_id'])
