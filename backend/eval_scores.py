import json
from app.analyzers.message import analyze_message_content
from app.analyzers.url import analyze_url_target
from app.analyzers.website import analyze_website_content
from app.config import settings

with open(settings.DEMO_DATASET_PATH, 'r', encoding='utf-8') as f:
    records = json.load(f)

for r in records:
    itype = r['input_type']
    c = r['submitted_content']
    if itype == 'message':
        res = analyze_message_content(c)
    elif itype == 'url':
        res = analyze_url_target(c, perform_live_check=False)
    else:
        res = analyze_website_content(html_content=c)
    print(f"{r['case_id']}: score={res['risk_score']} level={res['risk_level']} exp_lvl={r['expected_risk_level']} exp_cls={r['expected_classification']}")
