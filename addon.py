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
	years = reversed(range(1894, current_year + 1))
	utils.createWelcomeItem(utils.localStr(32002), utils.localStr(32003), index)
	utils.createFolder(search, utils.localStr(32000), ['NO_QUERY_VALUE', FIRST_PAGE], utils.icon_img, utils.localStr(32000), utils.icon_img)
	utils.createFolder(list_popular, utils.localStr(32001), [FIRST_PAGE], utils.icon_img, utils.localStr(32001), utils.icon_img)
	for item in years:
		utils.createFolder(list_items,
						str(item),
						[item, FIRST_PAGE],
						utils.icon_img,
						str(item),
						utils.icon_img)
	utils.set_container_type('albums')
	utils.set_view('widelist')
	utils.endDirectory()
	

@plugin.route('/show_dialog/<title>/<year>/<tmdb_id>/<mediatype>/<elementum_type>')
def show_dialog(title, year, tmdb_id, mediatype, elementum_type = ''):
	mediatype = 'tv' if mediatype == 'tvshow' else 'movie'
	ext_ids = tmdb.get_external_ids(tmdb_id, mediatype)
	try: imdb_id = ext_ids["imdb_id"]
	except: imdb_id = utils.localStr(32018)
	try: tvdb_id = ext_ids['tvdb_id']
	except: tvdb_id = utils.localStr(32019)

	item_str = 'TMDB: %s[CR]IMDB: %s[CR]TVDB: %s' % (tmdb_id, imdb_id, tvdb_id)
	players = dialog.create_players_dict(title, year, tmdb_id, imdb_id, tvdb_id, mediatype, elementum_type)

	window = dialog.DialogSelect("Dialog.xml", utils.home, "Default", title = 'Year Explorer', items = players, item_info = item_str)
	window.doModal()
	retval = window.retval
	del window
	return retval

@plugin.route('/search/<query>/<page>')
def search(query, page):
	if query == 'NO_QUERY_VALUE':
		query = utils.keyboard('', utils.localStr(32000))
		if query == None or query == '': return
	for item in parser.get_search_results(query, page):
		year = item['data'][0:4]
		url = plugin.url_for(show_dialog, item['titulo'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		real_title_url = plugin.url_for(show_dialog, item['titulo_original'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		utils.createItem(url,
							item['titulo'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							real_title_search = real_title_url )
	if int(page) > 1:
		utils.createFolder(search, utils.localStr(32004), [query, int(page) - 1], 'previouspage.png', "", 'previouspage.png')
	utils.createFolder(search, utils.localStr(32005), [query, int(page) + 1], 'nextpage.png', "", 'nextpage.png')
	utils.set_container_type('albums')
	utils.set_view('infowall')
	utils.endDirectory()

@plugin.route('/year/<year>/<page>')
def list_items(year, page):
	for item in parser.get_data_from_year(year, page):
		url = plugin.url_for(show_dialog, item['titulo'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		real_title_url = plugin.url_for(show_dialog, item['titulo_original'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		utils.createItem(url,
							item['titulo'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							real_title_search = real_title_url )
	if int(page) > 1:
		utils.createFolder(list_items, utils.localStr(32004), [year, int(page) - 1], 'previouspage.png', "", 'previouspage.png')
	utils.createFolder(list_items, utils.localStr(32005), [year, int(page) + 1], 'nextpage.png', "", 'nextpage.png')
	utils.set_container_type('albums')
	utils.set_view('infowall')
	utils.endDirectory()


@plugin.route('/similar/<id>/<type>/<page>')
def list_similar(id, type, page):
	for item in parser.get_similar_content_data(id, type, page):
		year = item['data'][0:4]
		url = plugin.url_for(show_dialog, item['titulo'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		real_title_url = plugin.url_for(show_dialog, item['titulo_original'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		utils.createItem(url,
							item['titulo'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							real_title_search = real_title_url )
	if int(page) > 1:
		utils.createFolder(list_similar, utils.localStr(32004), [id, type, int(page) - 1], 'previouspage.png', "", 'previouspage.png')
	utils.createFolder(list_similar, utils.localStr(32005), [id, type, int(page) + 1], 'nextpage.png', "", 'nextpage.png')
	utils.set_container_type('albums')
	utils.set_view('infowall')
	utils.endDirectory()

@plugin.route('/popular/<page>')
def list_popular(page):
	for item in parser.get_trending(page):
		year = item['data'][0:4]
		url = plugin.url_for(show_dialog, item['titulo'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		real_title_url = plugin.url_for(show_dialog, item['titulo_original'], year, item['tmdb'], item['tipo'], item['metodo_busca'])
		utils.createItem(url,
							item['titulo'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							real_title_search = real_title_url )
	if int(page) > 1:
		utils.createFolder(list_popular, utils.localStr(32004), [int(page) - 1], 'previouspage.png', "", 'previouspage.png')
	utils.createFolder(list_popular, utils.localStr(32005), [int(page) + 1], 'nextpage.png', "", 'nextpage.png')
	utils.set_container_type('albums')
	utils.set_view('infowall')
	utils.endDirectory()

if __name__ == '__main__':
	utils.plugin = plugin
	utils.log('init')
	plugin.run()
