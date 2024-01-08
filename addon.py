# -*- coding: utf-8 -*-
# Copyright (C) 2023 gbchr

from resources.lib import routing, utils, parser
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
from datetime import datetime

plugin = routing.Plugin()

welcome_label = 'Bem-vindo ao Year Explorer'
welcome_plot = 'Necessário Elementum e Rajada para realizar busca dos Torrents\n\nContato pelo email:\naddon.rajada@proton.me'

@plugin.route('/')
def index():
	current_year = datetime.now().year
	years = reversed(range(1894, current_year + 1))
	utils.createWelcomeItem(welcome_label, welcome_plot, index)
	utils.createFolder(list_popular, "Popular", [1], 'icon.png', "Popular", 'icon.png')
	for item in years:
		utils.createFolder(list_items,
						str(item),
						[item, 1],
						'icon.png',
						str(item),
						'icon.png')
	utils.set_view('widelist')
	utils.endDirectory()
	

@plugin.route('/year/<year>/<page>')
def list_items(year, page):
	for item in parser.get_data_from_year(year, page):
		elementum = utils.elementum_url(item['metodo_busca'], item['titulo'], year, item['tmdb'])
		utils.createItem(elementum,
							item['titulo'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							real_title_search = utils.elementum_url(item['metodo_busca'], item['titulo_original'], year, item['tmdb']) )
	if int(page) > 1:
		utils.createFolder(list_items, 'Página anterior', [year, int(page) - 1], 'previouspage.png', "", 'previouspage.png')
	utils.createFolder(list_items, 'Próxima página', [year, int(page) + 1], 'nextpage.png', "", 'nextpage.png')
	utils.set_view('infowall')
	utils.endDirectory()


@plugin.route('/similar/<id>/<type>/<page>')
def list_similar(id, type, page):
	for item in parser.get_similar_content_data(id, type, page):
		year = item['data'][0:4]
		elementum = utils.elementum_url(item['metodo_busca'], item['titulo'], year, item['tmdb'])
		utils.createItem(elementum,
							item['titulo'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							real_title_search = utils.elementum_url(item['metodo_busca'], item['titulo_original'], year, item['tmdb']) )
	if int(page) > 1:
		utils.createFolder(list_similar, 'Página anterior', [id, type, int(page) - 1], 'previouspage.png', "", 'previouspage.png')
	utils.createFolder(list_similar, 'Próxima página', [id, type, int(page) + 1], 'nextpage.png', "", 'nextpage.png')
	utils.set_view('infowall')
	utils.endDirectory()

@plugin.route('/popular/<page>')
def list_popular(page):
	for item in parser.get_trending(page):
		year = item['data'][0:4]
		elementum = utils.elementum_url(item['metodo_busca'], item['titulo'], year, item['tmdb'])
		utils.createItem(elementum,
							item['titulo'],
							image = item['imagem'],
							plot = item['sinopse'],
							fanart = item['background'],
							current_year = year,
							id = item['tmdb'],
							mediatype = item['tipo'],
							real_title_search = utils.elementum_url(item['metodo_busca'], item['titulo_original'], year, item['tmdb']) )
	if int(page) > 1:
		utils.createFolder(list_popular, 'Página anterior', [int(page) - 1], 'previouspage.png', "", 'previouspage.png')
	utils.createFolder(list_popular, 'Próxima página', [int(page) + 1], 'nextpage.png', "", 'nextpage.png')
	utils.set_view('infowall')
	utils.endDirectory()

if __name__ == '__main__':
	utils.plugin = plugin
	utils.log('init')
	plugin.run()
