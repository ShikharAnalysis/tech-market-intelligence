"""Standard-library analytical pipeline. Run from any working directory."""
import csv, hashlib, json, math, sqlite3
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def cents(value):
    return int((Decimal(str(value))*100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def concentration(values):
    """HHI on positive recipient NET obligations, not gross transaction obligations."""
    positive = sorted((v for v in values if v > 0), reverse=True)
    total = sum(positive)
    if not total: return None, None
    return sum((v/total)**2 for v in positive), sum(positive[:5])/total

def normalize(values):
    lo, hi = min(values), max(values)
    return [0.5]*len(values) if hi == lo else [(v-lo)/(hi-lo) for v in values]

def rank_segments(segments, weights, minimum):
    eligible = [dict(s) for s in segments if s['net_obligations'] >= minimum and s['cagr'] is not None and s['hhi'] is not None]
    if not eligible: return []
    raw = {'size':[math.log1p(s['net_obligations']) for s in eligible],
           'growth':[s['cagr'] for s in eligible], 'fragmentation':[1-s['hhi'] for s in eligible]}
    for key, values in raw.items():
        for row, value in zip(eligible, normalize(values)): row[key+'_component'] = value
    total = sum(weights.values())
    if total <= 0 or any(v<0 for v in weights.values()): raise ValueError('Weights must be nonnegative and total > 0')
    for row in eligible:
        row['score'] = 100 * sum(row[k+'_component']*v/total for k,v in weights.items())
    eligible.sort(key=lambda x:(-x['score'],x['agency'],x['naics']))
    for i,row in enumerate(eligible,1): row['rank']=i
    return eligible

def write_csv(path, rows):
    if not rows: raise ValueError(f'No rows for {path}')
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def main():
    cfg=json.loads((ROOT/'config.json').read_text())
    out=ROOT/'data/processed'; out.mkdir(parents=True,exist_ok=True)
    manifest_path=ROOT/'data/raw/manifest.sha256.json'
    if not manifest_path.exists(): raise ValueError('Run src/fetch_data.py to complete all source downloads first')
    manifest=json.loads(manifest_path.read_text())
    rows=[]; dates=[]; source_files=[]; seen_segments=set(); seen_keys=set(); missing_ids=0
    for name,expected in manifest.items():
        p=ROOT/'data/raw'/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected: raise ValueError(f'Hash mismatch: {name}')
        d=json.loads(p.read_text())
        if not d['complete']: raise ValueError('Incomplete source')
        segment=(d['year'],d['agency'],d['naics'])
        if segment in seen_segments: raise ValueError('Duplicate source segment')
        seen_segments.add(segment); dates.append(d['retrieved_at_utc']); source_files.append(name)
        for index,page in enumerate(d['pages'],1):
            if page['request']['page'] != index: raise ValueError('Missing source page')
            if page['response'].get('spending_level') != 'transactions': raise ValueError('Wrong spending grain')
            if page['response']['page_metadata']['hasNext'] != (index<len(d['pages'])): raise ValueError('Pagination inconsistent')
            for r in page['response']['results']:
                identifier=r.get('uei') or r.get('recipient_id') or r.get('id')
                if identifier is None:
                    missing_ids+=1; identifier='UNIDENTIFIED:'+str(r.get('name','UNKNOWN'))
                key=(*segment,str(identifier))
                if key in seen_keys: raise ValueError(f'Duplicate recipient group: {key}')
                seen_keys.add(key)
                rows.append({'fiscal_year':d['year'],'agency':d['agency'],'naics':d['naics'],
                             'category':cfg['categories'][d['naics']], 'recipient_id':str(identifier),
                             'recipient_name':' '.join(str(r.get('name') or 'UNKNOWN').split()),
                             'obligation_cents':cents(r['amount']), 'source_file':name})
    expected={(y,a,c) for y in cfg['years'] for a in cfg['agencies'] for c in cfg['categories']}
    if seen_segments != expected: raise ValueError('Source scope differs from config. Re-fetch complete scope in a fresh raw folder.')
    write_csv(out/'recipient_year.csv',rows)
    groups=defaultdict(list)
    for r in rows: groups[(r['fiscal_year'],r['agency'],r['naics'])].append(r)
    annual=[]
    for year,agency,code in sorted(expected):
        values=[r['obligation_cents'] for r in groups[(year,agency,code)]]
        hhi,top5=concentration(values)
        annual.append({'fiscal_year':year,'agency':agency,'naics':code,'category':cfg['categories'][code],
            'net_obligations':sum(values)/100,'positive_recipient_net':sum(v for v in values if v>0)/100,
            'negative_recipient_net':sum(v for v in values if v<0)/100,
            'recipient_count':len(values),'positive_recipients':sum(v>0 for v in values),'hhi':hhi,'top5_share':top5})
    lookup={(a['fiscal_year'],a['agency'],a['naics']):a for a in annual}
    first,last=min(cfg['years']),max(cfg['years'])
    segments=[]
    for agency in cfg['agencies']:
        for code in cfg['categories']:
            row=dict(lookup[(last,agency,code)])
            base=lookup[(first,agency,code)]['net_obligations']; prev=lookup[(last-1,agency,code)]['net_obligations']
            row.update({'base_obligations':base,'cagr':(row['net_obligations']/base)**(1/(last-first))-1 if base>0 and row['net_obligations']>0 else None,
                        'yoy':row['net_obligations']/prev-1 if prev>0 else None})
            segments.append(row)
    ranked=rank_segments(segments,cfg['weights'],cfg['minimum_latest_spend'])
    if not ranked: raise ValueError('No eligible segments')
    scenarios={'balanced':cfg['weights'],'size_led':{'size':.60,'growth':.20,'fragmentation':.20},
               'growth_led':{'size':.20,'growth':.60,'fragmentation':.20},'fragmentation_led':{'size':.20,'growth':.20,'fragmentation':.60}}
    sens=[]
    for scenario,w in scenarios.items():
        for r in rank_segments(segments,w,cfg['minimum_latest_spend']):
            sens.append({'scenario':scenario,'agency':r['agency'],'naics':r['naics'],'rank':r['rank'],'score':r['score']})
    for r in ranked:
        ranks=[s['rank'] for s in sens if s['agency']==r['agency'] and s['naics']==r['naics']]
        r['top3_scenarios']=sum(k<=3 for k in ranks); r['best_rank']=min(ranks); r['worst_rank']=max(ranks)
    write_csv(out/'annual_segments.csv',annual); write_csv(out/'opportunity_ranking.csv',ranked); write_csv(out/'sensitivity.csv',sens)
    db=sqlite3.connect(out/'market.db')
    db.executescript('DROP TABLE IF EXISTS recipient_year; CREATE TABLE recipient_year (fiscal_year INTEGER, agency TEXT, naics TEXT, category TEXT, recipient_id TEXT, recipient_name TEXT, obligation_cents INTEGER, source_file TEXT, PRIMARY KEY(fiscal_year,agency,naics,recipient_id));')
    db.executemany('INSERT INTO recipient_year VALUES (?,?,?,?,?,?,?,?)',[tuple(r.values()) for r in rows]); db.commit()
    # Execute the portfolio SQL, not a decorative query copy.
    sql=(ROOT/'sql/analysis.sql').read_text()
    db.executescript(sql)
    check=db.execute('SELECT SUM(net_cents) FROM segment_annual').fetchone()[0]
    assert check==sum(r['obligation_cents'] for r in rows)
    sql_metrics=db.execute('SELECT fiscal_year,agency,naics,hhi,top5_share FROM concentration').fetchall()
    for y,a,c,h,t in sql_metrics:
        py=lookup[(y,a,c)]
        assert (h is None and py['hhi'] is None) or math.isclose(h,py['hhi'],abs_tol=1e-10)
        assert (t is None and py['top5_share'] is None) or math.isclose(t,py['top5_share'],abs_tol=1e-10)
    db.close()
    quality={'source':'USAspending live API snapshot','synthetic_data':False,'first_retrieval_utc':min(dates),'last_retrieval_utc':max(dates),
             'source_files':len(source_files),'recipient_year_rows':len(rows),'expected_segments':len(expected),'observed_segments':len(seen_segments),
             'missing_recipient_ids':missing_ids,'negative_rows':sum(r['obligation_cents']<0 for r in rows),
             'duplicate_keys':0,'raw_hashes_verified':True,'sql_python_totals_match':True,'sql_python_concentration_match':True}
    (ROOT/'reports/data_quality.json').write_text(json.dumps(quality,indent=2))
    payload={'config':cfg,'quality':quality,'annual':annual,'ranking':ranked,'sensitivity':sens}
    (out/'dashboard_data.json').write_text(json.dumps(payload,indent=2))
    import render_dashboard
    render_dashboard.render(payload)
    lines=['# Decision memo: technology market opportunity','',f'**Evidence:** real USAspending snapshot; FY{first}–FY{last}; 4 selected awarding agencies × 3 NAICS categories. USD nominal net contract obligations.','',
           '**Decision:** shortlist segments for further customer and procurement research. The score does not establish eligibility, forecast wins, or measure obtainable revenue.','',
           '## Priority shortlist','', '| Rank | Agency / service | Latest obligations | Two-year CAGR | HHI | Top 3 in scenarios |','|---|---|---:|---:|---:|---:|']
    for r in ranked[:3]:
        lines.append(f"| {r['rank']} | {r['agency']} / {r['category']} | ${r['net_obligations']/1e6:,.1f}m | {r['cagr']:.1%} | {r['hhi']:.3f} | {r['top3_scenarios']}/4 |")
    lines += ['', '## Interpretation','',f"The base-case leader is **{ranked[0]['agency']} — {ranked[0]['category']}**. Its rank ranges from {ranked[0]['best_rank']} to {ranked[0]['worst_rank']} across four preference scenarios. This describes sensitivity to chosen weights, not statistical confidence.",
              '', 'The shortlist trades off logarithmic market size, historical CAGR and recipient fragmentation. A smaller segment may rank above a larger one. Read the component columns before drawing a conclusion.',
              '', '## Action plan','', '1. Days 1–30: examine solicitations, procurement vehicles, set-asides, security requirements and internal delivery capability in the top segments. Historical obligations are not open opportunities.',
              '2. Days 31–60: interview potential delivery partners and agency procurement contacts through appropriate public channels; establish a qualified opportunity register.',
              '3. Days 61–90: pursue a limited number of validated opportunities. Track qualification rate, time spent, bid cost and stage progression. Do not invent a win rate from spending history.',
              '', '## Reasons to reject or defer a segment','', 'Ineligible procurement requirements, poor delivery fit, a closed vehicle, an incumbent relationship advantage, or no forthcoming solicitation can outweigh its quantitative score.',
              '', '## Limits','', 'Selected agency/service scope is not the total technology market. Agencies are awarding, not funding agencies; procurement on behalf of other agencies can shift the interpretation. Recipient entities are not consolidated corporate parents. HHI excludes negative recipient-net values from its denominator; net market totals retain them. Three annual observations cannot support a reliable forecasting model. Source revisions can change historical values. Broad NAICS codes are not AI/cloud/cybersecurity labels.',
              '', 'See `docs/METHODOLOGY.md`, `docs/SOURCES.md` and `reports/data_quality.json` for calculation definitions and provenance.']
    largest=max(ranked,key=lambda r:r['net_obligations'])
    insight=['', '## What changes the decision', '',
        f"The largest eligible segment is {largest['agency']} / {largest['category']} at ${largest['net_obligations']/1e9:.2f}bn, but it ranks {largest['rank']} in the base case. Size alone does not produce the recommendation.", '',
        f"The third base-case candidate, {ranked[2]['agency']} / {ranked[2]['category']}, appears in the top three in only {ranked[2]['top3_scenarios']} of four scenarios. Treat that slot as provisional and discuss the client's priorities before committing resources.", '',
        'The first priority is stable across the specified scenarios; the rest of the shortlist is more preference-sensitive. Start qualification with the stable leader, keep a comparison candidate, and resolve the third slot through capability and procurement-access evidence. This is a proposed sequence, not an optimized budget allocation.']
    lines.extend(insight)
    (ROOT/'reports/DECISION_MEMO.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(quality,indent=2)); print('Top segment:',ranked[0]['agency'],ranked[0]['category'])
if __name__=='__main__': main()
