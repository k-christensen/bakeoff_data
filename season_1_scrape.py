import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from pprint import pprint

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
    cols_and_vals['town_name'] = l[1]
    for k,v in l[2].items():
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

episode_info = {'episode':0, 'fraction_done':0}
template_dict = {k:0 for k in color_meaning_dict.values()}
total_template_dict = {"total_{}".format(k):0 for k in color_meaning_dict.values()}
full_template_dict = {**episode_info, **template_dict, **total_template_dict}

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
    color_list = [color.lower() for color in color_list]
    num = 0
    episode_and_outcome = []
    while num<max_ep:
        ep_dict = full_template_dict.copy()
        current_episode = num+1
        cont_history = color_list[:num]
        ep_dict['episode'] = current_episode
        ep_dict['fraction_done'] = current_episode/max_ep
        if cont_history:
            ep_dict[color_meaning_dict[cont_history[-1]]] = 1
            ep_dict.update({"total_{}".format(color_meaning_dict[item]):
            color_list.count(item) 
            for item in list(set(cont_history))})
        if color_meaning_dict[color_list[num]] in ['eliminated', 'runner-up']:
            ep_dict['eliminated'] = 1
        if color_meaning_dict[color_list[num]] is not 'not_in_comp':
            episode_and_outcome.append(ep_dict)
        num += 1
    for d in episode_and_outcome:
        d.update(df_dict[name])
        d['name'] = name
    key_list = ["{}_episode_{}".format(name.rstrip(), num) for num in list(range(1,max_ep+1))]
    cont_and_colors.update(dict(zip(key_list, episode_and_outcome)))


df = pd.DataFrame.from_dict(cont_and_colors, orient = 'index')
# current df has person's bio info and outcomes

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

placement_list = []
name_and_ep = list(tuple(zip(df['name'], df['episode'])))
for item in name_and_ep:
    placement_list.append(tech_tuple[item])

df['technical'] = placement_list


pattern = re.compile(r"Episode_\d:")

pprint(soup.find(text=pattern).__dict__)

# for h in soup(text = ):
#     print(h.parent)
#     # if "Episode" in h.text:
#     #     print(h.find_next_siblings(limit=3)[2])

for h in soup(id = pattern):
    print(h.find_all_next(limit=5)[4])
