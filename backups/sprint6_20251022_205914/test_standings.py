import requests
from bs4 import BeautifulSoup

url = 'https://www.teamrankings.com/nfl/standings/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', class_='tr-table')
print(f'Found table: {table is not None}')

if table:
    rows = table.find_all('tr')[1:]  # Skip header
    print(f'Total rows: {len(rows)}')
    print('\nFirst 10 teams:')
    for i, row in enumerate(rows[:10]):
        cells = row.find_all('td')
        if len(cells) >= 3:
            team_name = cells[1].get_text(strip=True)
            record = cells[2].get_text(strip=True)
            print(f'{i+1}. {team_name:30s} {record}')
