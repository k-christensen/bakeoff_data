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
    elif 'align' in d.get('style'):
        contestant_name_list.append(d.text) 

contestant_name_list = [name.rstrip() for name in contestant_name_list]


contestant_name_age_town = {item.td.text:
[int(item.td.find_next_sibling().text), 
item.td.find_next_sibling().find_next_sibling().find_next_sibling().a.get('href')] 
for item in 
soup.find("table", class_="wikitable").find_all('tr')
if item.td is not None}

[item[-1].split('/')[-1] for item in contestant_name_age_town.values()]

area_url = 'https://en.wikipedia.org/wiki/Milton_Keynes'  
area_page = requests.get(area_url)

area_soup = BeautifulSoup(area_page.content)

stats_dict = {}
for item in area_soup.find_all('th'):
    if 'Density' in item.text:
        stats_dict['density'] = item.find_next_sibling().text.split()[0]
    if 'Population' in item.text:
        stats_dict['pop'] = item.find_next_sibling().text.split()[0]
    if 'Area' in item.text:
        stats_dict['area'] = item.find_next_sibling().text.split()[0]

stats_dict



color_meaning_dict = {'lightblue':'next_round', 
'cornflowerblue':'judge_fav',
'plum': 'least_fav', 
'orangered': 'eliminated', 
'yellow': 'winner',
'limegreen': 'runner-up',
'lemonchiffon': 'star_baker',
'silver': 'not_in_comp',
'chocolate': 'withdrew',
'darkgrey': 'not_in_comp',
'gainsboro': 'unable_to_compete_week'}

max_ep = 0
for item in elim_chart.find_all('th'):
    if item.text.rstrip().isnumeric() and int(item.text.rstrip())> max_ep:
        max_ep = int(item.text.rstrip())

cont_and_colors = {}
len_of_chart = int(elim_chart.th.get('colspan'))

for name in contestant_name_list:
    name_tag = elim_chart.find('td', text = re.compile(name))
    if name_tag is None:
        name_tag = elim_chart.find('span', text = re.compile(name))
    tag = name_tag.find_next()
    color_list = []
    while len(color_list) < max_ep:
        colspan = 1
        if tag.has_attr('style'):
            color = tag.get('style')
        if tag.has_attr('colspan'):
            colspan = int(tag.get('colspan'))
        color_list.extend([x for x in 
        re.split("(?:background:\s?)(\w*)(?:;)”?", color) 
        if x] * colspan)
        tag = tag.find_next_sibling()
    color_list = color_list[:max_ep]
    meaning_list = [color_meaning_dict[color.lower()] for color in color_list]
    episode_num_list = [num for num in list(range(1,max_ep+1))]
    episode_and_outcome = [list(item) for item in list(zip(episode_num_list,meaning_list))]
    key_list = ["{}_episode_{}".format(name.rstrip(), num) for num in list(range(1,max_ep+1))]
    cont_and_colors.update(dict(zip(key_list, episode_and_outcome)))

for entry in list(cont_and_colors):
    if 'not_in_comp' in cont_and_colors[entry]:
        cont_and_colors.pop(entry)

df = pd.DataFrame.from_dict(cont_and_colors, orient = 'index', columns = ['episode', 'outcome'])
df



# elim_chart.find('td', text = re.compile('Terry'))

# def fn(tag, num =1):
#     cycle = 0
#     while cycle<num:
#         tag = tag.find_next_sibling()
#         cycle += 1
#     return tag

# fn(elim_chart.find('td', text = re.compile('Terry')),4)

# tag_list = []
# for name in contestant_name_list:
#     name_tag = elim_chart.find('td', text = re.compile(name))
#     if name_tag is None:
#         print(name)
#         name_tag = elim_chart.find('span', text = re.compile(name))
#         print(name_tag)


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