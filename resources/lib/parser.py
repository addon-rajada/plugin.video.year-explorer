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
	movie_page = int(page) * 2
	m1 = tmdb.GetTrending('movie', movie_page - 1)
	m2 = tmdb.GetTrending('movie', movie_page)
	s = tmdb.GetTrending('tv', page)
	all = []
	# movies
	if m1 != None: all += parse_movies_result(m1)
	else: utils.notify('Falha ao carregar filmes')
	if m2 != None: all += parse_movies_result(m2)
	else: utils.notify('Falha ao Carregar Filmes')
	# tv shows
	if s != None: all += parse_shows_result(s)
	else: utils.notify('Falha ao carregar séries')
	return sorted_results(all)



def get_data_from_year(year, page = 1):
	movie_page = int(page) * 2
	m1 = tmdb.DiscoverByYear(year, 'movie', movie_page - 1)
	m2 = tmdb.DiscoverByYear(year, 'movie', movie_page)
	s = tmdb.DiscoverByYear(year, 'tv', page)
	all = []

	# movies
	if m1 != None: all += parse_movies_result(m1)
	else: utils.notify('Falha ao carregar filmes')
	if m2 != None: all += parse_movies_result(m2)
	else: utils.notify('Falha ao Carregar Filmes')

	# tv shows
	if s != None: all += parse_shows_result(s)
	else: utils.notify('Falha ao carregar séries')

	return sorted_results(all)


def get_similar_content_data(id, mediatype, page = 1):
	s = tmdb.GetSimilar(mediatype, id, 'similar', page)
	r = tmdb.GetSimilar(mediatype, id, 'recommendations', page)
	all = []

	if mediatype == 'movie' and s != None: all += parse_movies_result(s)
	elif mediatype == 'tvshow' and s != None: all += parse_shows_result(s)
	else: utils.notify('Falha ao carregar conteúdo similar')

	if mediatype == 'movie' and r != None: all += parse_movies_result(r)
	elif mediatype == 'tvshow' and r != None: all += parse_shows_result(r)
	else: utils.notify('Falha ao carregar conteúdo recomendado')

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
				'imagem': 'https://image.tmdb.org/t/p/w780' + r['poster_path'],
				'background': 'https://image.tmdb.org/t/p/w780' + r['backdrop_path'],
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
