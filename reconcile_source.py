"""Independent latest-year aggregation cross-check against awarding-agency endpoint."""
import concurrent.futures,csv,json,urllib.request
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]

def fetch(code,year):
    path=ROOT/'data/validation'/f'{year}_{code}.json'; path.parent.mkdir(exist_ok=True)
    body={'filters':{'time_period':[{'start_date':f'{year-1}-10-01','end_date':f'{year}-09-30'}],
          'award_type_codes':['A','B','C','D'],'naics_codes':{'require':[code]}},'spending_level':'transactions','limit':100,'page':1}
    if not path.exists():
        req=urllib.request.Request('https://api.usaspending.gov/api/v2/search/spending_by_category/awarding_agency/',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=90) as r: data=json.load(r)
        if data['page_metadata']['hasNext']: raise ValueError('Agency results need pagination; do not validate a truncated list')
        path.write_text(json.dumps({'request':body,'response':data},indent=2))
    return code,json.loads(path.read_text())['response']['results']

def main():
    cfg=json.loads((ROOT/'config.json').read_text()); year=max(cfg['years'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=dict(pool.map(lambda c:fetch(c,year),cfg['categories']))
    rows=list(csv.DictReader((ROOT/'data/processed/annual_segments.csv').open()))
    checks=[]
    for r in rows:
        if int(r['fiscal_year'])!=year:continue
        match=[a for a in results[r['naics']] if a['name']==r['agency']]
        if len(match)!=1: raise ValueError('Agency missing or ambiguous')
        diff=Decimal(r['net_obligations'])-Decimal(str(match[0]['amount']))
        tolerance=Decimal('0.005')*(Decimal(r['recipient_count'])+1)
        checks.append({'agency':r['agency'],'naics':r['naics'],'difference_usd':float(diff),'tolerance_usd':float(tolerance),'exact_match':diff==0,'passed':abs(diff)<=tolerance})
    (ROOT/'reports/source_reconciliation.json').write_text(json.dumps(checks,indent=2))
    if not all(r['passed'] for r in checks): raise ValueError('Source mismatch: inspect source revision or pagination')
    print(f'{len(checks)} latest-year segments match independent agency aggregates within the documented recipient-rounding tolerance.')
if __name__=='__main__':main()
