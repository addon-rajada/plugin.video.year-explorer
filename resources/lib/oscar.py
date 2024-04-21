# -*- coding: utf-8 -*-
# Copyright (C) 2024 gbchr

import requests
from resources.lib import utils

# mock
#class utils:
#	def localStr(id): return f'string {id}'

main_url = 'https://raw.githubusercontent.com/addon-rajada/oscars-json/main/year/%s.json'

def is_valid_category(category):
	if 'Actor' in category: return True
	if 'Actress' in category: return True
	if 'Directing' in category: return True
	return False

def parse(year):
	response = requests.get(main_url % year)
	try: js = response.json()
	except: return []
	titles = []
	movies = []
	for k,v in js.items():
		for entry in v:

			current_entry = None
			if 'title' in entry['tmdb'].keys():
				current_entry = entry['tmdb'] # movie is at tmdb object
				current_entry['custom_title'] = current_entry['title']
			elif 'award_movie' in entry['tmdb'].keys() and 'error' not in entry['tmdb']['award_movie'].keys():
				current_entry = entry['tmdb']['award_movie'] # movie is at award_movie object
				current_entry['custom_title'] = current_entry['title']
				if 'error' not in entry['tmdb'].keys() and is_valid_category(entry['category']): # there is a person and valid category
					current_entry['custom_title'] = entry['tmdb']['name']
					current_entry['poster_path'] = entry['tmdb']['profile_path']
				elif 'error' not in entry['tmdb'].keys() and not is_valid_category(entry['category']): # there is a person and not valid category
					pass
				elif 'error' in entry['tmdb'].keys() and is_valid_category(entry['category']): # there is no person and valid category
					current_entry['custom_title'] = entry['first_label']
				else: # there is no person and not valid category
					pass
			else:
				continue # no movie data

			if current_entry['custom_title'] not in titles:
				current_entry['categories'] = [{'category':entry['category'], 'winner':entry['winner']}]
				movies.append(current_entry)
				titles.append(current_entry['custom_title'])
			else:
				for m in movies:
					if m['custom_title'] == current_entry['custom_title']:
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
