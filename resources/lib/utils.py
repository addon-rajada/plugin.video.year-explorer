# -*- coding: utf-8 -*-
# Copyright (C) 2023 gbchr

from resources.lib import routing
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

import sys
if sys.version_info[0] == 2:
	from urllib import quote
else:
	from urllib.parse import quote

plugin = None

addon = xbmcaddon.Addon()
home = addon.getAddonInfo('path')
icon = addon.getAddonInfo('icon')
name = addon.getAddonInfo('name')
version = addon.getAddonInfo('version')
profile = addon.getAddonInfo('profile')

icon_img = 'icon.png'
fanart_img = 'fanart.jpg'

def bold(text):
	# return bold text
	return '[B]' + text + '[/B]'

def colorful(text, color = 'white'):
	# return colored text
	# i.e. crimson, palegreen, red, darkgray, lightskyblue, turquoise, sienna ...
	return '[COLOR ' + color + ']' + text + '[/COLOR]'

def img(file):
	# return link or local path for image
	if 'http' not in file.lower():
		return home + '/resources/media/' + file
	else:
		return file

def log(itemOrMessage, opt_label = ''):
	# log message
	xbmc.log('[COLOR blue]' + opt_label + repr(itemOrMessage) + '[/COLOR]', level=xbmc.LOGDEBUG)

def refresh():
	xbmc.executebuiltin('Container.Refresh()')

def update(path):
	xbmc.executebuiltin('Container.Update(%s)' % path)

def notify(text, icon = icon, time = 3000):
	# create notification
	dialog = xbmcgui.Dialog()
	dialog.notification(name, text, icon, time)
	del dialog

def current_view_id():
	win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
	return str(win.getFocusId())

def set_view(name):
	# update container content and view type
	xbmcplugin.setContent(plugin.handle, 'albums')
	# ref: https://github.com/xbmc/xbmc/tree/master/addons/skin.estuary/xml
	views_dict = {
		'list': 50,
		'poster': 51,
		'iconwall': 52,
		'shift': 53,
		'infowall': 54,
		'widelist': 55,
		'wall': 500,
		'banner': 501,
		'fanart': 502
	}

	#for i in range(10): # assert view mode is set
	xbmc.executebuiltin('Container.SetViewMode(%s)' % (views_dict[name]))
	#	xbmc.sleep(10)

def youtube_url(id):
	return 'plugin://plugin.video.youtube/play/?video_id=' + id + '&incognito=true'

def elementum_url(type, title, year = '', id = ''):
	# ref: https://github.com/elgatito/elementum/blob/master/api/routes.go
	title = title.replace(' ', '+')
	query = "%s+%s" % (title, year)
	if type == 'context':
		url = "plugin://plugin.video.elementum" + quote("/context/media/%s/%s/play" % ('movie', query))
	elif type == 'context_query':
		url = "plugin://plugin.video.elementum/context/media/query/%s/play" % (quote(query))
	elif type == 'movie':
		url = "plugin://plugin.video.elementum" + quote("/movie/%s/play/%s" % (id, query))
	elif type == 'tv':
		url = "plugin://plugin.video.elementum" + quote("/show/%s/play" % (id))
	elif type == 'search':
		url = "plugin://plugin.video.elementum/search?q=" + quote(query)
	return url

def play(url):
	# play url
	xbmcplugin.setResolvedUrl(plugin.handle, True, xbmcgui.ListItem(path=url))
	#xbmc.executebuiltin("PlayMedia(%s)" % url)
	#xbmc.executebuiltin('RunPlugin(%s)' % url)
	#xbmc.Player().play(url)

def createFolder(function, label, arguments_list, image = icon_img, plot = '', thumb = icon_img):
	# create folder linked to some function and given arguments
	li = ListItem(bold(label))
	li.setArt({
		'icon': img(thumb), 'thumb': img(thumb),
		'poster': img(image), 'banner': img(image)
	})
	li.setInfo(type="video", infoLabels = {
		"plot": bold(plot)
	})
	li.setProperty("fanart_image", img(fanart_img))
	addDirectoryItem(plugin.handle, plugin.url_for(function, *arguments_list), li, True)

def createWelcomeItem(message, plot, entrypoint_function):
	# create first item of addon
	welcomeItem = ListItem(bold(message))
	welcomeItem.setInfo(type="video", infoLabels = {
		"plot": bold(plot)
	})
	welcomeItem.setArt({'icon': img(icon_img)})
	welcomeItem.setProperty("fanart_image", img(fanart_img))
	addDirectoryItem(plugin.handle, plugin.url_for(entrypoint_function), welcomeItem, True)

def createItem(url, label, **kwargs):
	# create playable item
	li = ListItem(bold(label))
	try:
		li.setInfo(type="video", infoLabels = {
			"title": label,
			"plot": kwargs['plot'],
			"mediatype": kwargs['mediatype']
		})
		# check and fix for original elementum context menu
		if kwargs['mediatype'] == 'tvshow':
			li.setInfo(type="video", infoLabels = {
				"tvshowtitle": label,
				"season": 1,
				"mediatype": "season"
			})
		li.setArt({
			'icon': kwargs['image'], 'thumb': kwargs['image'],
			'poster': kwargs['image'], 'banner': kwargs['image']
		})
		li.setProperty("fanart_image", kwargs['fanart'])
		li.setProperty('IsPlayable', 'false')
		li.setProperty('tmdb_id', str(kwargs['id']))
		li.setProperty("year", str(kwargs['current_year']))
		#li.setProperty("show_dialog_busy", "false")

		CM_items = []
		# context menu for similar content
		similar_link = plugin.base_url + '/similar/%s/%s/1' % (kwargs['id'], kwargs['mediatype'])
		similar_item = ('Conteúdo similar', 'Container.Update(%s)' % (similar_link))
		CM_items.append(similar_item)
		# context menu for original title search
		title_item = ('Buscar com título original', 'RunPlugin(%s)' % (kwargs['real_title_search']))
		CM_items.append(title_item)
		# add context menu to ListItem
		li.addContextMenuItems(CM_items)

	except Exception as e:
		log(e)
	addDirectoryItem(plugin.handle, url, li)

def endDirectory():
	endOfDirectory(plugin.handle, succeeded=True, cacheToDisc=True)

