# -*- coding: utf-8 -*-
# Copyright (C) 2023 gbchr

from resources.lib import utils, tmdb
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from math import pow, sqrt

def sorted_results(content):
	# 0.1 * float(r['data'][5:7]) + 0.9 * float(r['nota'])
	# float(r['nota']) * float(r['votos'])
	return sorted(content, key = lambda r: pow(float(r['nota']), 2) * sqrt(float(r['votos'])), reverse=True)


def get_trending(page = 1):
	def thread_trending(id, type, page):
		return (id, tmdb.GetTrending(type, page))
	movie_page = int(page) * 2
	all_requests = [('movie', movie_page - 1), ('movie', movie_page), ('tv', page)]
	all_requests = utils.indexed_threadpool(thread_trending, all_requests, {'type':0, 'page':1})
	m1 = all_requests[0]
	m2 = all_requests[1]
	s = all_requests[2]
	all = []
	# movies
	if m1 != None: all += parse_movies_result(m1)
	else: utils.notify(utils.localStr(32009))
	if m2 != None: all += parse_movies_result(m2)
	else: utils.notify(utils.localStr(32010))
	# tv shows
	if s != None: all += parse_shows_result(s)
	else: utils.notify(utils.localStr(32011))
	return sorted_results(all)



def get_data_from_year(year, page = 1):
	def thread_year(id, year, type, page):
		return (id, tmdb.DiscoverByYear(year, type, page))
	movie_page = int(page) * 2
	all_requests = [(year, 'movie', movie_page - 1), (year, 'movie', movie_page), (year, 'tv', page)]
	all_requests = utils.indexed_threadpool(thread_year, all_requests, {'year':0, 'type':1, 'page':2})
	m1 = all_requests[0]
	m2 = all_requests[1]
	s = all_requests[2]
	all = []

	# movies
	if m1 != None: all += parse_movies_result(m1)
	else: utils.notify(utils.localStr(32009))
	if m2 != None: all += parse_movies_result(m2)
	else: utils.notify(utils.localStr(32010))

	# tv shows
	if s != None: all += parse_shows_result(s)
	else: utils.notify(utils.localStr(32011))

	return sorted_results(all)


def get_similar_content_data(id, mediatype, page = 1):
	def thread_similar(id, media, tmdb_id, type, page):
		return (id, tmdb.GetSimilar(media, tmdb_id, type, page))
	all_requests = [(mediatype, id, 'similar', page), (mediatype, id, 'recommendations', page)]
	all_requests = utils.indexed_threadpool(thread_similar, all_requests, {'media':0,'tmdb_id':1,'type':2,'page':3})
	s = all_requests[0]
	r = all_requests[1]
	all = []

	if mediatype == 'movie' and s != None: all += parse_movies_result(s)
	elif mediatype == 'tvshow' and s != None: all += parse_shows_result(s)
	else: utils.notify(utils.localStr(32012))

	if mediatype == 'movie' and r != None: all += parse_movies_result(r)
	elif mediatype == 'tvshow' and r != None: all += parse_shows_result(r)
	else: utils.notify(utils.localStr(32013))

	return sorted_results(all)

def get_search_results(query, page = 1):
	def thread_search(id, type, query, page):
		return (id, tmdb.QuerySearch(type, query, page))
	all_requests = [('movie', query, page), ('tv', query, page)]
	all_requests = utils.indexed_threadpool(thread_search, all_requests, {'type':0, 'query':1, 'page':2})
	m = all_requests[0]
	s = all_requests[1]
	all = []
	if m != None: all += parse_movies_result(m)
	else: utils.notify(utils.localStr(32009))
	if s != None: all += parse_shows_result(s)
	else: utils.notify(utils.localStr(32011))
	return sorted_results(all)

def parse_movies_result(json):
	all = []
	for r in json['results']:
		try:
			all.append({
				'tipo': 'movie',
				'metodo_busca': 'search',
				'tmdb': r['id'],
				'titulo': r['title'],
				'titulo_original': r['original_title'],
				'sinopse': 'Filme\nAno: %s\nNota: %s (%s votos)\n\n%s' % (r['release_date'][0:4], str(r['vote_average']), str(r['vote_count']), r['overview']),
				# w500, w780, original
				'imagem': 'https://image.tmdb.org/t/p/w780' + r['poster_path'],
				# w500, w780, w1280, w1920, original
				'background': 'https://image.tmdb.org/t/p/w1280' + r['backdrop_path'],
				'data': r['release_date'],
				'nota': r['vote_average'],
				'votos': r['vote_count']
			})
		except Exception as e: utils.log(e)
	return all

def parse_shows_result(json):
	all = []
	for r in json['results']:
		try:
			all.append({
				'tipo': 'tvshow',
				'metodo_busca': 'search',
				'tmdb': r['id'],
				'titulo': r['name'],
				'titulo_original': r['original_name'],
				'sinopse': 'Série\nAno: %s\nNota: %s (%s votos)\n\n%s' % (r['first_air_date'][0:4], str(r['vote_average']), str(r['vote_count']), r['overview']),
				# w500, w780, original
				'imagem': 'https://image.tmdb.org/t/p/w780' + r['poster_path'],
				# w500, w780, w1280, w1920, original
				'background': 'https://image.tmdb.org/t/p/w1280' + r['backdrop_path'],
				'data': r['first_air_date'],
				'nota': r['vote_average'],
				'votos': r['vote_count']
			})
		except Exception as e: utils.log(e)
	return all
