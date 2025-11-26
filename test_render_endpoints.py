import requests

tests = [
    ('/api/teams', 'Basic teams'),
    ('/api/hcl/teams', 'HCL teams'),
    ('/api/hcl/teams?season=2025', 'HCL teams 2025'),
    ('/health', 'Health')
]

for path, name in tests:
    r = requests.get(f'https://h-c-lombardo-app.onrender.com{path}')
    print(f'{name:25s} {path:40s} => {r.status_code}')
