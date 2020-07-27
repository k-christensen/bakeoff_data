import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np

url = 'https://en.wikipedia.org/wiki/The_Great_British_Bake_Off_(series_1)'

page = requests.get(url)

soup = BeautifulSoup(page.content)

for t in soup.find_all("table"):
    if "Elimination chart" in t.th.text:
        elim_chart = t

# takes the elimination chart, creates list of names
def cont_name_list(elim_chart):
    contestant_name_list = []
    for d in elim_chart.find_all('td'):
        if d.has_attr('align'):
            contestant_name_list.append(d.text)
        elif 'align' in d.get('style'):
            contestant_name_list.append(d.text) 
    return [name.rstrip() for name in contestant_name_list]

contestant_name_list = cont_name_list(elim_chart)

ep_counter = 0
tech_results_list = []
ep_tech = {1:{name:0 for name in contestant_name_list}}
for h in soup.findAll('h3'):
    if "Episode" in h.text:
        names = []
        place = []
        for item in h.find_next_siblings(limit=3)[2].findAll('th'):
            if "Technical" in item.text:
                result_tables = item.parent.parent.findAll('td')
                ep_counter += 1
        ep_list = list(range(2,ep_counter+2))
        for t in result_tables:
            if t.text in contestant_name_list:
                names.append(t.text)
                place.append([x for x in re.split("(\d?\d|N/A)",t.find_next_siblings(limit=2)[1].text) if x][0])
        if 'N/A' in place:
            num_list = [int(p) for p in place if str(p).isnumeric()]
            ave = np.average(num_list)
            place = [ave if x == 'N/A' else x for x in place]
        place = [float(x) for x in place]
        episode_placement = dict(zip(names,place))
        tech_results_list.append(episode_placement)

ep_tech.update(dict(zip(ep_list,tech_results_list)))

tech_tuple = {}
for k,v in ep_tech.items():
    for n,p in v.items():
        tech_tuple.update({(n,k):p})

tech_tuple

# placement_list = []
# name_and_ep = list(tuple(zip(df['name'], df['episode'])))
# for item in name_and_ep:
#     placement_list.append(tech_tuple[item])