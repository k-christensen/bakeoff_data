import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

url = 'https://en.wikipedia.org/wiki/The_Great_British_Bake_Off_(series_1)'

page = requests.get(url)

soup = BeautifulSoup(page.content)

for t in soup.find_all("table"):
    if "Elimination chart" in t.th.text:
        elim_chart = t

contestant_name_list = []

for d in elim_chart.find_all('td'):
    if d.has_attr('align'):
        contestant_name_list.append(d.text)

cont_and_colors = {}
len_of_chart = int(elim_chart.th.get('colspan'))
for name in contestant_name_list:
    name_tag = elim_chart.find('td', text = name)
    tag = name_tag.find_next()
    color_list = []
    while tag.has_attr('align') == False:
        colspan = 1
        if tag.has_attr('style'):
            color = tag.get('style')
        if tag.has_attr('colspan'):
            colspan = int(tag.get('colspan'))
        color_list.extend([x for x in re.split("(?:background:)(\w*)(?:;)", color) if x] * colspan)
        tag = tag.find_next()
    color_list = list(filter(None, color_list))
    cont_and_colors[name] = color_list[:len_of_chart-1]

cont_and_colors

test_list = list(cont_and_colors.values())[0]

[re.split("(?:background:)(\w*)(?:;)", item)[1] for item in test_list]












# notes
# light blue - through to next round
# cornflower blue - judge fav
# orangered - eliminated
# plum - least fav but not eliminated


# for d in elim_chart.find_all('td'):
#     if d.has_attr('style'):
#         print(d.get('style'))

# for d in elim_chart.find_all('td'):
#     if d.has_attr('style'):
#         print(d.text)