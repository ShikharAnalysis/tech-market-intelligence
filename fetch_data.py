"""Download complete recipient aggregates; preserve requests and responses for audit."""
import concurrent.futures, datetime, hashlib, json, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://api.usaspending.gov/api/v2/search/spending_by_category/recipient/'

def fetch_segment(year, agency, code):
    stem = f'{year}_{agency.replace(" ", "_")}_{code}'
    path = ROOT / 'data/raw' / (stem + '.json')
    if path.exists():
        saved = json.loads(path.read_text())
        if saved.get('complete') and saved.get('source_url') == BASE:
            return stem, 'cached'
    pages, page = [], 1
    while True:
        body = {'filters': {'time_period': [{'start_date': f'{year-1}-10-01', 'end_date': f'{year}-09-30'}],
                'award_type_codes': ['A','B','C','D'], 'naics_codes': {'require': [code]},
                'agencies': [{'type': 'awarding', 'tier': 'toptier', 'name': agency}]},
                'spending_level': 'transactions', 'limit': 100, 'page': page}
        for attempt in range(4):
            try:
                req = urllib.request.Request(BASE, data=json.dumps(body).encode(), headers={'Content-Type':'application/json','User-Agent':'PortfolioResearch/1.0'})
                with urllib.request.urlopen(req, timeout=90) as response:
                    result = json.load(response)
                if not isinstance(result.get('results'), list) or 'hasNext' not in result.get('page_metadata', {}):
                    raise ValueError('Unexpected API schema; refusing incomplete output')
                break
            except Exception:
                if attempt == 3: raise
                time.sleep(2 ** attempt)
        pages.append({'request':body,'response':result})
        if not result['page_metadata']['hasNext']: break
        page += 1
        if page > 1000: raise RuntimeError('Pagination safety stop')
    payload = {'source_url':BASE,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'year':year,'agency':agency,'naics':code,'complete':True,'pages':pages}
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(payload, indent=2))
    temp.replace(path)
    return stem, f'{page} pages'

def main():
    cfg = json.loads((ROOT/'config.json').read_text())
    jobs = [(y,a,c) for y in cfg['years'] for a in cfg['agencies'] for c in cfg['categories']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch_segment,*job) for job in jobs]
        for f in concurrent.futures.as_completed(futures): print(*f.result(), flush=True)
    manifest = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'data/raw').glob('*.json'))}
    (ROOT/'data/raw/manifest.sha256.json').write_text(json.dumps(manifest,indent=2))
if __name__ == '__main__': main()
