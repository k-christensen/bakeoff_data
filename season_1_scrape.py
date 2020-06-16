import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://en.wikipedia.org/wiki/The_Great_British_Bake_Off_(series_1)'

page = requests.get(url)

soup = BeautifulSoup(page.content)

tables = list(soup.find_all('table'))

header = tables[2].find_all('th')

tables[2].find_all('tr')[2].contents[1]
name_list = []

what_comes_next = []


rows = tables[2].find_all('tr')

for row in rows:
    cells = row.find_all('td')
    
    
    if len(cells) > 1:
        rank = cells[0]
        name_list.append(rank.text.strip())

        the_next = cells[1]
        what_comes_next.append(the_next)
        

what_comes_next
name_list

soup.find_all("table", limit=3)

for t in soup.find_all("table"):
    if "Elimination chart" in t.th.text:
        elim_chart = t

for d in elim_chart.find_all('td'):
    if d.has_attr('style'):
        print(d.get('style'))

for d in elim_chart.find_all('td'):
    if d.has_attr('style'):
        print(d.text)

elim_chart.td

'Runner-up' in elim_chart.find('td', text = 'Ruth').find_next().find_next().find_next().find_next().text





# notes
# light blue - through to next round
# cornflower blue - judge fav
# orangered - eliminated
# plum - least fav but not eliminated