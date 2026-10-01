"""Generate a self-contained dashboard. No server, CDN, npm or API key required."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render(payload):
    template=(ROOT/'src/dashboard_template.html').read_text()
    data=json.dumps(payload).replace('<','\\u003c')
    (ROOT/'index.html').write_text(template.replace('__DATA__',data),encoding='utf-8')
    render_ranking(payload)

def render_ranking(payload):
    """Static SVG result chart for the README, generated without extra packages."""
    from html import escape
    names={'Department of Veterans Affairs':'Veterans Affairs','Department of Health and Human Services':'Health & Human Services','Department of Energy':'Energy','National Aeronautics and Space Administration':'NASA'}
    cats={'541511':'Custom programming','541512':'Systems design','541519':'Other computer services'}
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="780" viewBox="0 0 1160 780">',
           '<rect width="1160" height="780" fill="#f4f7fa"/>',
           '<rect width="1160" height="135" fill="#102b41"/>',
           '<text x="42" y="38" fill="#70d8ce" font-family="sans-serif" font-size="13" letter-spacing="3">MARKETLENS / DECISION INTELLIGENCE</text>',
           '<text x="42" y="78" fill="white" font-family="sans-serif" font-size="30" font-weight="bold">A market shortlist built on evidence and trade-offs</text>',
           '<text x="42" y="108" fill="#c7d5df" font-family="sans-serif" font-size="15">FY2023–FY2025 · 4 agencies · 3 service categories · Real USAspending data</text>']
    for x,label,color in [(42,'Size · 35%','#102b41'),(200,'Growth · 35%','#047e82'),(380,'Fragmentation · 30%','#c58929')]:
        parts.append(f'<rect x="{x}" y="158" width="11" height="11" fill="{color}"/><text x="{x+18}" y="169" fill="#334e62" font-family="sans-serif" font-size="13">{label}</text>')
    left,width=475,550
    for value in range(0,101,20):
        x=left+width*value/100
        parts.append(f'<line x1="{x}" y1="191" x2="{x}" y2="675" stroke="#dce5ed"/><text x="{x}" y="695" text-anchor="middle" fill="#5f7181" font-family="sans-serif" font-size="12">{value}</text>')
    for i,r in enumerate(payload['ranking']):
        y=210+i*39
        label=escape(f"{i+1:02d}   {names[r['agency']]} / {cats[r['naics']]}")
        parts.append(f'<text x="42" y="{y+5}" fill="#102b41" font-family="sans-serif" font-size="14">{label}</text>')
        x=left
        for key,color in [('size','#102b41'),('growth','#047e82'),('fragmentation','#c58929')]:
            points=100*r[key+'_component']*payload['config']['weights'][key]/sum(payload['config']['weights'].values())
            w=width*points/100
            parts.append(f'<rect x="{x}" y="{y-13}" width="{w}" height="23" fill="{color}"/>');x+=w
        parts.append(f'<text x="{x+9}" y="{y+4}" fill="#102b41" font-family="sans-serif" font-size="13" font-weight="bold">{r["score"]:.1f}</text>')
    parts += ['<text x="750" y="718" text-anchor="middle" fill="#5f7181" font-family="sans-serif" font-size="13">Relative screening score / 100</text>',
              '<text x="42" y="747" fill="#5f7181" font-family="sans-serif" font-size="12">Scope-specific priorities, not win probabilities. Procurement access and delivery fit require separate validation.</text>',
              '<text x="42" y="767" fill="#5f7181" font-family="sans-serif" font-size="12">Source: saved USAspending snapshot, 1 October 2026. Methodology and raw requests included in repository.</text></svg>']
    (ROOT/'reports/ranking-preview.svg').write_text(''.join(parts))
