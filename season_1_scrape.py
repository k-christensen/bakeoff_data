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

def area_stats(url_snippet):
    stats_dict = {'density':None}
    if type(url_snippet) == str:
        area_url = 'https://en.wikipedia.org{}'.format(url_snippet)  
        area_page = requests.get(area_url)

        area_soup = BeautifulSoup(area_page.content)

        for item in area_soup.find_all('th'):
            if 'Density' in item.text:
                if item.find_next_sibling().text:
                    density_str = item.find_next_sibling().text
                    for elem in item.find_next_sibling().text.split():
                        if "/km" in elem:
                            d = int([item for item in re.split("(\d*,?\d*)",elem) if len(item)>1][0].replace(',',''))
                            stats_dict['density'] = d
            if 'Population' in item.text:
                if item.find_next_sibling() is None:
                    stats_dict['pop'] = re.split('(\d*,\d*)',item.parent.find_next_sibling().text)[1]
                elif item.find_next_sibling().text.startswith('%'):
                    pass
                else:
                    pop_str = item.find_next_sibling().text
                    stats_dict['pop']= pop_str.split()[0]
    return {url_snippet.split('/')[-1]:stats_dict}

for l in contestant_name_age_town.values():
    area = l[-1]
    l.append(area_stats(area))

for l in contestant_name_age_town.values():
    l.pop(1)

long_names = list(contestant_name_age_town.keys())

for shorter in contestant_name_list:
    for longer in list(contestant_name_age_town.keys()):
        if shorter in longer:
            contestant_name_age_town[shorter] = contestant_name_age_town[longer]

for name in list(contestant_name_age_town.keys()):
    if name in long_names:
        del contestant_name_age_town[name]

contestant_name_age_town

df_dict = {}

for name, l in contestant_name_age_town.items():
    cols_and_vals = {}
    df_dict[name] = cols_and_vals
    cols_and_vals['age'] = l[0]
    cols_and_vals['town_name'] = list(l[1].keys())[0]
    for di in list(l[1].values()):
        for k,v in di.items():
            cols_and_vals[k] = v 

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
    episode_fraction_list = [num/max_ep for num in list(range(1,max_ep+1))]
    episode_and_outcome = [list(item) for item in list(zip(episode_num_list,meaning_list, episode_fraction_list))]
    episode_and_outcome_dict = [{'episode':l[0], 'outcome':l[1], 'fraction_done':l[2]}for l in episode_and_outcome]
    for d in episode_and_outcome_dict:
        d.update(df_dict[name])
    episode_and_outcome_dict
    key_list = ["{}_episode_{}".format(name.rstrip(), num) for num in list(range(1,max_ep+1))]
    cont_and_colors.update(dict(zip(key_list, episode_and_outcome_dict)))

for entry in list(cont_and_colors):
    if 'not_in_comp' in cont_and_colors[entry]['outcome']:
        cont_and_colors.pop(entry)


df = pd.DataFrame.from_dict(cont_and_colors, orient = 'index')

outcome_dummies = pd.get_dummies(df['outcome'])

df_with_dummies = df.join(outcome_dummies)

df_with_dummies.drop(columns='outcome', inplace=True)

for h in soup.findAll('h3'):
    if "Episode" in h.text:
        print([item for item in re.split("(?:\D)", h.text) if item][0])


# a = ['a', 's', 'd']
# b = ['q', 'w', 'e']
# c = ['p', 'o', 'l']

# list(zip(a,b,c))


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