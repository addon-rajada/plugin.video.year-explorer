# -*- coding: utf-8 -*-
# Copyright (C) 2023 gbchr

import requests
from kodi_six import xbmc, xbmcgui, xbmcaddon

lang = xbmcaddon.Addon().getSetting('idioma')

API_key = 'bc96b19479c7db6c8ae805744d0bdfe2' # from umbrella

find_url = 'https://api.themoviedb.org/3/find/%s?language=%s&api_key=%s&external_source=%s' % ('%s', lang, API_key, '%s')
# https://api.themoviedb.org/3/find/tt0081505?api_key=bc96b19479c7db6c8ae805744d0bdfe2&external_source=imdb_id&language=pt-BR

details_url = 'https://api.themoviedb.org/3/%s/%s?api_key=%s&language=%s' % ('%s', '%s', API_key, lang)
# https://api.themoviedb.org/3/movie/tt0081505?api_key=bc96b19479c7db6c8ae805744d0bdfe2&language=pt-BR
# https://api.themoviedb.org/3/tv/1402?api_key=bc96b19479c7db6c8ae805744d0bdfe2&language=pt-BR
# https://api.themoviedb.org/3/person/3027?api_key=bc96b19479c7db6c8ae805744d0bdfe2&language=pt-BR

externalids_url = 'https://api.themoviedb.org/3/%s/%s/external_ids?api_key=%s&language=%s' % ('%s', '%s', API_key, lang)
# https://api.themoviedb.org/3/movie/694/external_ids?api_key=bc96b19479c7db6c8ae805744d0bdfe2
# https://api.themoviedb.org/3/tv/1402/external_ids?api_key=bc96b19479c7db6c8ae805744d0bdfe2

discover_year_url = 'https://api.themoviedb.org/3/discover/%s?api_key=%s&%s=%s&language=%s&page=%s&sort_by=%s' % ('%s', API_key, '%s', '%s', lang, '%s', '%s')
# https://api.themoviedb.org/3/discover/movie?api_key=bc96b19479c7db6c8ae805744d0bdfe2&primary_release_year=1999&language=pt-BR&page=1
# https://api.themoviedb.org/3/discover/tv?api_key=bc96b19479c7db6c8ae805744d0bdfe2&first_air_date_year=1999&language=pt-BR&page=1

similar_url = 'https://api.themoviedb.org/3/%s/%s/%s?api_key=%s&language=%s&sort_by=%s&page=%s' % ('%s', '%s', '%s', API_key, lang, '%s', '%s')
# https://api.themoviedb.org/3/movie/694/similar?api_key=bc96b19479c7db6c8ae805744d0bdfe2
# https://api.themoviedb.org/3/tv/1402/similar?api_key=bc96b19479c7db6c8ae805744d0bdfe2

trending_url = 'https://api.themoviedb.org/3/trending/%s/week?api_key=%s&page=%s&language=%s&sort_by=%s' % ('%s', API_key, '%s', lang, '%s')
# https://api.themoviedb.org/3/trending/movie/day?api_key=bc96b19479c7db6c8ae805744d0bdfe2&page=1&language=pt-BR
# https://api.themoviedb.org/3/trending/tv/day?api_key=bc96b19479c7db6c8ae805744d0bdfe2&page=1&language=pt-BR
# https://api.themoviedb.org/3/trending/all/week?api_key=bc96b19479c7db6c8ae805744d0bdfe2&page=1&language=pt-BR

def get_request(url):
	try:
		try: response = requests.get(url)
		except requests.exceptions.SSLError:
			response = requests.get(url, verify=False)
	except requests.exceptions.ConnectionError:
		xbmcgui.Dialog().notification(message="Connection Error")
	if '200' in str(response):
		return response.json()
	elif 'Retry-After' in response.headers: # API REQUESTS ARE BEING THROTTLED, INTRODUCE WAIT TIME (TMDb removed rate-limit on 12-6-20)
		throttleTime = response.headers['Retry-After']
		#xbmcgui.Dialog().notification(heading='TMDb', message='TMDB Throttling Applied, Sleeping for %s seconds' % throttleTime) # error
		#xbmc.sleep((int(throttleTime) + 1) * 1000)
		return get_request(url)
	else:
		return None

def IdLookup(imdb, mediatype):
	result = None
	if not imdb: return result
	try:
		url = find_url % (imdb, 'imdb_id')
		result = get_request(url)
		if not result: raise Exception()
		if mediatype == 'movie':
			result = result.get('movie_results')[0]
		else:
			result = result.get('tv_results')[0]
	except:
		pass
	return result

def IdDetails(imdb, mediatype):
	result = None
	if not imdb: return result
	try:
		url = details_url % (mediatype, imdb)
		result = get_request(url)
		if not result: raise Exception()
	except:
		pass
	return result

def get_external_ids(tmdb, mediatype):
	result = None
	if not tmdb: return result
	try:
		url = externalids_url % (mediatype, tmdb)
		result = get_request(url)
	except:
		pass
	return result

def DiscoverByYear(year, mediatype, page = 1):
	result = None
	try:
		parameter = 'first_air_date_year' if mediatype == 'tv' else 'primary_release_year'
		sortBy = 'vote_count.desc' # 'popularity'
		url = discover_year_url % (mediatype, parameter, year, page, sortBy)
		result = get_request(url)
		if not result: raise Exception()
	except:
		pass
	return result

def GetSimilar(type, id, endpoint, page = 1):
	result = None
	try:
		sortBy = 'popularity.desc' # 'vote_count'
		if type == 'tvshow': type = 'tv'
		url = similar_url % (type, id, endpoint, sortBy, page)
		result = get_request(url)
		if not result: raise Exception()
	except:
		pass
	return result

def GetTrending(type, page = 1):
	result = None
	try:
		sortBy = 'popularity.desc' # 'vote_count'
		if type == 'tvshow': type = 'tv'
		url = trending_url % (type, page, sortBy)
		result = get_request(url)
		if not result: raise Exception()
	except:
		pass
	return result
