# -*- coding: utf-8 -*-
# Copyright (C) 2023 gbchr

from resources.lib import routing, utils, parser, tmdb, dialog
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
from datetime import datetime

plugin = routing.Plugin()
FIRST_PAGE = 1

@plugin.route('/')
def index():
	current_year = datetime.now().year
	years = reversed(range(1892, current_year + 1))
	utils.createWelcomeItem(utils.localStr(32002), utils.localStr(32003), index)
	utils.createFolder(search, utils.localStr(32000), ['NO_QUERY_VALUE', FIRST_PAGE], utils.icon_img, utils.localStr(32000), utils.icon_img)
	utils.createFolder(top_rated, utils.localStr(32032), [FIRST_PAGE], utils.icon_img, utils.localStr(32032), utils.icon_img)
	utils.createFolder(list_popular, utils.localStr(32001), [FIRST_PAGE], utils.icon_img, utils.localStr(32001), utils.icon_img)
	for item in years:
		# context menu items
		item_cm = []
		if item > 1928: # first oscar at 1929
			item_cm.append( (utils.localStr(32027), 'Container.Update(%s)' % plugin.url_for(oscar, str(item), 'true') ) )
			item_cm.append( (utils.localStr(32028), 'Container.Update(%s)' % plugin.url_for(oscar, str(item), 'false') ) )
		# list item
		utils.createFolder(list_items,
						str(item),
						[item, FIRST_PAGE],
						utils.icon_img,
						str(item),
						utils.icon_img,
						item_cm )
	utils.set_container_type(utils.get_setting('container_type'))
	utils.set_view('widelist')
	utils.endDirectory()
	
@plugin.route('/show_dialog/<title>/<year>/<tmdb_id>/<mediatype>/<elementum_type>/<season>/<episode>')
@plugin.route('/show_dialog/<title>/<year>/<tmdb_id>/<mediatype>/<elementum_type>/<season>')
@plugin.route('/show_dialog/<title>/<year>/<tmdb_id>/<mediatype>/<elementum_type>')
def show_dialog(title, year, tmdb_id, mediatype, elementum_type, season = 1, episode = 1):
	mediatype = 'tv' if mediatype == 'tvshow' else 'movie'
	try: ext_ids = tmdb.get_external_ids(tmdb_id, mediatype)
	except: ext_ids = {}
	try: imdb_id = ext_ids["imdb_id"]
	except: imdb_id = utils.localStr(32018)
	try: tvdb_id = ext_ids['tvdb_id']
	except: tvdb_id = utils.localStr(32019)

	if utils.is_japanese(title): # force english title if title is japanese
		try:
			req = tmdb.IdDetails(tmdb_id, mediatype, force_english_lang=True)
			title = req['title'] if mediatype == 'movie' else req['name']
			title_str = f'{title} ({utils.localStr(32034)})'
		except:
			title_str = f'{title} ({utils.localStr(32035)})'
	else:
		title_str = title
	
	item_str = '%s: %s[CR]TMDB: %s[CR]IMDB: %s[CR]TVDB: %s' % (utils.localStr(32020), title_str, tmdb_id, imdb_id, tvdb_id)
	players = dialog.create_players_dict(title, year, tmdb_id, imdb_id, tvdb_id, mediatype, elementum_type, season, episode)

	window = dialog.DialogSelect("Dialog.xml", utils.home, "Default", title = 'Year Explorer', items = players, item_info = item_str)
	window.doModal()
	retval = window.retval
	del window
	return retval

def make_default_directory(result,
							folder_function,
							page = 1,
							previous_page_args = [],
							next_page_args = [],
							view = utils.get_setting('view_mode'),
							create_previous_page = True,
							create_next_page = True ):
	for item in result:
		year = item['data'][0:4]
		title_url = plugin.url_for(show_dialog, item['titulo'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		real_title_url = plugin.url_for(show_dialog, item['titulo_original'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		url = title_url if item['tipo'] == 'movie' else plugin.url_for(list_seasons, item['tmdb'])
		isFolder = False if item['tipo'] == 'movie' else True
		utils.createItem(url,
							item['titulo'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							title_search = title_url,
							real_title_search = real_title_url,
							isFolder = isFolder )
	if int(page) > 1 and create_previous_page:
		utils.createFolder(folder_function, utils.localStr(32004), previous_page_args, 'previouspage.png', "", 'previouspage.png')
	if len(result) > 0 and create_next_page:
		utils.createFolder(folder_function, utils.localStr(32005), next_page_args, 'nextpage.png', "", 'nextpage.png')
	utils.set_container_type(utils.get_setting('container_type'))
	utils.set_view(view)
	utils.endDirectory()

@plugin.route('/search/<query>/<page>')
def search(query, page):
	if query == 'NO_QUERY_VALUE':
		query = utils.keyboard(utils.read_query(), utils.localStr(32000))
		if query == None or query == '':
			index()
			return
	utils.save_query(query)
	result = parser.get_search_results(query, page)
	make_default_directory(result, search, page, [query, int(page) - 1], [query, int(page) + 1])

@plugin.route('/oscar/<year>/<only_winners>')
def oscar(year, only_winners):
	result = parser.get_oscars(year, only_winners)
	make_default_directory(result, oscar, create_next_page=False, create_previous_page=False)

@plugin.route('/top_rated/<page>')
def top_rated(page):
	result = parser.get_top_rated(page)
	make_default_directory(result, top_rated, page, [int(page) - 1], [int(page) + 1])

@plugin.route('/year/<year>/<page>')
def list_items(year, page):
	result = parser.get_data_from_year(year, page)
	make_default_directory(result, list_items, page, [year, int(page) - 1], [year, int(page) + 1])


@plugin.route('/similar/<id>/<type>/<page>')
def list_similar(id, type, page):
	result = parser.get_similar_content_data(id, type, page)
	make_default_directory(result, list_similar, page, [id, type, int(page) - 1], [id, type, int(page) + 1])

@plugin.route('/popular/<page>')
def list_popular(page):
	result = parser.get_trending(page)
	make_default_directory(result, list_popular, page, [int(page) - 1], [int(page) + 1])

@plugin.route('/list_seasons/<tmdb_id>')
def list_seasons(tmdb_id):
	item = parser.get_show_seasons(tmdb_id)
	for temporada in item['temporadas']:
		year = item['data'][0:4]
		title = '%s %s' % (item['titulo'], temporada['nome'])
		real_title = '%s S%s' % (item['titulo_original'], utils.add_ep_zero(temporada['numero_temporada']))
		title_url = plugin.url_for(show_dialog, title, year, item['tmdb'], item['tipo'], item['metodo_busca'], temporada['numero_temporada'])
		real_title_url = plugin.url_for(show_dialog, real_title, year, item['tmdb'], item['tipo'], item['metodo_busca'], temporada['numero_temporada'])
		url = plugin.url_for(list_episodes, item['tmdb'], temporada['numero_temporada'], title, real_title, utils.base64_encode_url(item['background']))
		utils.createItem(url,
							temporada['nome'],
							image = temporada['imagem'],
							plot = temporada['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							title_search = title_url,
							real_title_search = real_title_url,
							isFolder = True )
	utils.set_container_type(utils.get_setting('container_type'))
	utils.set_view('widelist')
	utils.endDirectory()


@plugin.route('/list_episodes/<tmdb_id>/<season>/<title>/<original_title>/<background>')
def list_episodes(tmdb_id, season, title, original_title, background):
	background = utils.base64_decode_url(background)
	episodes = parser.get_season_episodes(tmdb_id, season)
	for item in episodes:
		year = item['data'][0:4]
		title_url = plugin.url_for(show_dialog, title, year, tmdb_id, item['tipo'], item['metodo_busca'], item['temporada'], item['episodio'])
		real_title_url = plugin.url_for(show_dialog, original_title + 'E%s' % utils.add_ep_zero(item['episodio']), year, tmdb_id, item['tipo'], item['metodo_busca'], item['temporada'], item['episodio'])
		utils.createItem(title_url,
							item['nome'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = background,
							current_year = year,
							id = tmdb_id,
							mediatype = item['tipo'],
							title_search = title_url,
							real_title_search = real_title_url )
	utils.set_container_type(utils.get_setting('container_type'))
	utils.set_view('widelist')
	utils.endDirectory()

if __name__ == '__main__':
	utils.plugin = plugin
	utils.log('init')
	plugin.run()
