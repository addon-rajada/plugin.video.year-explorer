# -*- coding: utf-8 -*-
# Copyright (C) 2024 gbchr

import requests
from resources.lib import utils

main_url = 'https://raw.githubusercontent.com/addon-rajada/oscars-json/main/year/%s.json'

def parse(year):
	response = requests.get(main_url % year)
	try: js = response.json()
	except: return []
	titles = []
	movies = []
	for k,v in js.items():
		for entry in v:
			if 'error' in entry['tmdb'].keys(): continue # no movie data
			if entry['tmdb']['original_title'] not in titles:
				entry['tmdb']['categories'] = [{'category':entry['category'], 'winner':entry['winner']}]
				movies.append(entry['tmdb'])
				titles.append(entry['tmdb']['original_title'])
			else:
				for m in movies:
					if m['original_title'] == entry['tmdb']['original_title']:
						m['categories'].append({'category':entry['category'], 'winner':entry['winner']})
	return movies

def make_category_string(movie):
	win = '  '
	nom = '  '
	for cat in movie['categories']:
		if cat['winner'] == True: win += (cat['category'].replace('--', ' - ') + ', ')
		else: nom += (cat['category'].replace('--', ' - ') + ', ')
	win_str = f'{utils.localStr(32025)}:{win[:-2]}\n\n' if win != '  ' else ''
	nom_str = f'{utils.localStr(32026)}:{nom[:-2]}\n\n' if nom != '  ' else ''
	return '%s%s' % (win_str, nom_str)

def winners(year):
	result = parse(year)
	only_winners = []
	for movie in result:
		for cat in movie['categories']:
			if cat['winner'] == True and movie not in only_winners:
				movie['overview'] = make_category_string(movie) + movie['overview']
				only_winners.append(movie)
	return only_winners

def winners_and_nominees(year):
	result = parse(year)
	for movie in result:
		movie['overview'] = make_category_string(movie) + movie['overview']
	return result

#print(winners(2024))
#print(winners_and_nominees(2024))
