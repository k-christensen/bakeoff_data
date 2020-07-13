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

def cont_name_list(elim_chart):
    contestant_name_list = []
    for d in elim_chart.find_all('td'):
        if d.has_attr('align'):
            contestant_name_list.append(d.text)
        elif 'align' in d.get('style'):
            contestant_name_list.append(d.text) 
    return [name.rstrip() for name in contestant_name_list]

contestant_name_list = cont_name_list(elim_chart)

contestant_name_age_town = {item.td.text:
[int(item.td.find_next_siblings(limit = 3)[0].text), 
item.td.find_next_siblings(limit = 3)[2].a.get('href')] 
for item in 
soup.find("table", class_="wikitable").find_all('tr')
if item.td is not None}
# at this point the dict is 
# key =  contesntant full name
# value = list containing contestant age and wiki url snippet 
# (i.e. '/wiki/Essex')

def area_stats(url_snippet):
    stats_dict = {'density':None, 'pop':None}

    if type(url_snippet) == str:
        area_url = 'https://en.wikipedia.org{}'.format(url_snippet)  
        area_page = requests.get(area_url)

        area_soup = BeautifulSoup(area_page.content)

        for item in area_soup.find_all('th'):
            if 'Density' in item.text:
                if item.find_next_sibling().text:
                    density_str = item.find_next_sibling().text
                    for elem in density_str.split():
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
                    stats_dict['pop']= int(pop_str.split()[0].replace(',',''))
    return [url_snippet.split('/')[-1], stats_dict]

for l in contestant_name_age_town.values():
    town = l[-1]
    l.extend(area_stats(town))
    l.pop(1)

# this bit takes the area stats func 
# and replaces the url snippet with the actual area stats
# then it takes out the url snippet as that's no longer needed

long_names = list(contestant_name_age_town.keys())

for shorter in contestant_name_list:
    for longer in list(contestant_name_age_town.keys()):
        if shorter in longer:
            contestant_name_age_town[shorter] = contestant_name_age_town[longer]
# this makes a duplicate dict entry 
# with the key being the shorter name 
# instead of the full name

for name in list(contestant_name_age_town.keys()):
    if name in long_names:
        del contestant_name_age_town[name]

# this takes out the entries with the full name

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

cont_and_colors
df = pd.DataFrame.from_dict(cont_and_colors, orient = 'index')

outcome_dummies = pd.get_dummies(df['outcome'])

df_with_dummies = df.join(outcome_dummies)

df_with_dummies.drop(columns='outcome', inplace=True)

for h in soup.findAll('h3'):
    if "Episode" in h.text:
        print([item for item in re.split("(?:\D)", h.text) if item][0])

