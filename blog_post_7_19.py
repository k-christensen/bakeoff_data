import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

url = 'https://en.wikipedia.org/wiki/The_Great_British_Bake_Off_(series_1)'

page = requests.get(url)

soup = BeautifulSoup(page.content)

# identify desired chart
# in this case the elimination chart
for t in soup.find_all("table"):
    if "Elimination chart" in t.th.text:
        elim_chart = t

# get chart headers
# in this case baker and 1-6
header_list = []
for head in elim_chart.findAll('th'):
    if head.text.startswith('Elim') is False:
        header_list.append(head.text.rstrip())

# get list of dicts, 
# each dict contains column name and entry for that row
row_list = []
for name in elim_chart.findAll('td', align = 'left'):
    row = [name.text]
    tag_list = name.find_next_siblings(limit = 6)
    for item in tag_list:
        color = item.get('style')
        col = 1
        if item.has_attr('colspan'):
            col = int(item.get('colspan'))
        row.extend([x for x in 
        re.split("(?:background:\s?)(\w*)(?:;)”?", color) 
        if x] * col)
    row_list.append(dict(zip(header_list,row)))

df = pd.DataFrame.from_dict(row_list)


meaning_list = soup.find('b', text=re.compile('Colour key:')).find_all_next('dd', limit = 6)

color_list = []
meaning_text_list = []
for item in meaning_list:
    color_list.append(re.split('(?:background-color:)(\w*)',item.span.get('style'))[1])
    meaning_text_list.append(re.split('(– )',item.text)[-1])
meaning_text_list

full_text_meaning_dict = dict(zip(color_list, meaning_text_list))
full_text_meaning_dict['LightBlue'] = 'next_round'
full_text_meaning_dict['OrangeRed'] = 'eliminated'
full_text_meaning_dict['Plum'] = 'least_fav'
full_text_meaning_dict['CornflowerBlue'] = 'fav'
full_text_meaning_dict['LimeGreen'] = 'runner_up'
full_text_meaning_dict['Yellow'] = 'winner'
full_text_meaning_dict['silver'] = 'not_in_comp'




