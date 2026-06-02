import re
from datetime import datetime

with open('pmforge_dashboard/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 2) Extract sprint schedule
# Match common sprint date patterns found in the file
# Pattern 1: { num: 15, label: 'Sprint 15', sub: 'UI & UX Polish', start: '2026-05-18', end: '2026-05-30' }
sprint_pattern_obj = re.compile(r"\{\s*num:\s*(\d+),\s*label:\s*'Sprint \d+',\s*sub:.*?, \s*start:\s*'(\d{4}-\d{2}-\d{2})',\s*end:\s*'(\d{4}-\d{2}-\d{2})'")
# Pattern 2: Sprint 1 (S1): 2025-10-13 to 2025-10-24 (older format)
sprint_pattern_txt = re.compile(r'Sprint\s+(\d+)\s+\(S\d+\):\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})')

sprints = []
matches = list(sprint_pattern_obj.finditer(content)) + list(sprint_pattern_txt.finditer(content))
for m in matches:
    s_id, start, end = m.groups()
    sprints.append({
        'id': f'S{s_id}',
        'start': datetime.strptime(start, '%Y-%m-%d'),
        'end': datetime.strptime(end, '%Y-%m-%d')
    })

target_date = datetime.strptime('2026-05-18', '%Y-%m-%d')
active_sprints = [s['id'] for s in sprints if s['start'] <= target_date <= s['end']]
print(f"Sprint including 2026-05-18: {', '.join(set(active_sprints)) if active_sprints else 'None'}")

# 3) Prints whether S15 starts on 2026-05-18
s15 = next((s for s in sprints if s['id'] == 'S15'), None)
s15_starts = s15['start'].strftime('%Y-%m-%d') == '2026-05-18' if s15 else False
print(f'S15 starts on 2026-05-18: {s15_starts}')

# 4) Parses Product Backlog item objects
item_pattern = re.compile(r"\{\s*id:'(.*?)',\s*feature:'(.*?)',\s*cat:'(.*?)',\s*pri:'(.*?)',\s*effort:'(.*?)',\s*sprint:'(.*?)',\s*status:'(.*?)'\s*\}")
items = []
for m in item_pattern.finditer(content):
    items.append({
        'id': m.group(1),
        'feature': m.group(2),
        'cat': m.group(3),
        'pri': m.group(4),
        'effort': m.group(5),
        'sprint': m.group(6),
        'status': m.group(7)
    })

# 5) Prints counts by status and sprint
status_counts = {}
sprint_counts = {}
for item in items:
    status_counts[item['status']] = status_counts.get(item['status'], 0) + 1
    sprint_counts[item['sprint']] = sprint_counts.get(item['sprint'], 0) + 1

print('Counts by Status:', status_counts)
print('Counts by Sprint:', sprint_counts)

# 6) Prints all remaining (status=Backlog) items in priority order
pri_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
backlog_items = [i for i in items if i['status'] == 'Backlog']
backlog_items.sort(key=lambda x: pri_order.get(x['pri'], 99))

print('\nRemaining Backlog Items (Priority Order):')
# Print top 5 to keep it concise but show the order
for i in backlog_items[:5]:
    print(f"{i['id']} | {i['cat']} | {i['pri']} | {i['effort']} | {i['sprint']} | {i['feature']}")
print('...')

# 7) ML-related remaining backlog items
ml_keywords = ['model', 'predict', 'elo', 'xgb']
ml_backlog = [
    i for i in backlog_items 
    if i['cat'] == 'ML' or any(kw in i['feature'].lower() for kw in ml_keywords)
]

print('\nML-related Remaining Backlog Items:')
for i in ml_backlog:
    print(f"{i['id']} | {i['cat']} | {i['pri']} | {i['effort']} | {i['sprint']} | {i['feature']}")
