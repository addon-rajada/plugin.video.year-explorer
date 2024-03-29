# -*- coding: utf-8 -*-
# Copyright (C) 2023 gbchr

from resources.lib import routing
from concurrent.futures import ThreadPoolExecutor, as_completed
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory
import sys, base64

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

def localStr(id):
	return addon.getLocalizedString(id)

def get_setting(key):
	return addon.getSetting(key)

def keyboard(placeholder, title):
	kb = xbmc.Keyboard(placeholder, title)
	kb.doModal()
	if kb.isConfirmed(): return kb.getText()
	else: return None

def get_kodi_version():
	full_version_info = xbmc.getInfoLabel('System.BuildVersion')
	baseversion = full_version_info.split(".")
	intbase = int(baseversion[0])
	return intbase

def indexed_threadpool(function, data, func_args, max_threads = 16):
	"""
		function MUST have following signature -> (id, arg1, arg2, ...) and return -> (id, ...)
		data MUST be an array of List, Tuple or Object
		func_args MUST be an object:
			{
				'arg1': index/key for each item at data array,
				...
			}
		example:
			def myfunc(id, value1, value2): return (id, value1*value2)
			values = [[1,2],[2,3],[3,4],[4,5],[5,6]]
			result = indexed_threadpool(myfunc, values, {'value1':0, 'value2':1})
	"""
	size = len(data)
	workers = size if (size > 0 and size <= max_threads) else max_threads
	counter = 0
	final_result = []
	with ThreadPoolExecutor(max_workers = workers) as executor:
		futures = []
		for item in data:
			args_dict = {'id': counter}
			for argument, index in func_args.items(): args_dict[argument] = item[index]
			futures.append(executor.submit(function, **args_dict))
			args_dict = {}
			counter += 1
		for f in as_completed(futures):
			result = f.result()
			final_result.append(result)
	return [value[1] for value in sorted(final_result, key = lambda x: x[0])] # sort by id then remove it

def base64_encode_url(value):
    encoded = str(base64.b64encode(bytes(value, "utf-8")), 'utf-8')
    return encoded.replace('=', '').replace('+', '-').replace('/', '_')

def base64_decode_url(data):
    value = data.replace('-', '+').replace('_', '/')
    value += '=' * (len(value) % 4)
    return str(base64.b64decode(value), 'utf-8') # urlsafe_

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

def set_container_type(type):
	# update container content: movies, albums, videos ...
	xbmcplugin.setContent(plugin.handle, type)

def set_view(name):
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

def add_ep_zero(ep):
	if int(ep) <= 9: return '0%s' % ep
	return ep

def remove_dict_duplicates(array):
	res_list = [i for n, i in enumerate(array)
				if i not in array[:n]]
	return res_list

def youtube_url(id):
	return 'plugin://plugin.video.youtube/play/?video_id=' + id + '&incognito=true'

def torrest_url(title, year):
	# ref: https://github.com/i96751414/plugin.video.flix/blob/master/lib/navigation.py
	query = "%s+%s" % (title, year)
	return 'plugin://plugin.video.flix/providers/play_query?query=%s' % query

def jacktook_url(type, title, tmdb, imdb, tvdb, season = 1, episode = 1):
	# ref: https://github.com/Sam-Max/plugin.video.jacktook/blob/main/resources/lib/navigation.py
	if type == 'movie':
		return f'plugin://plugin.video.jacktook/search?mode={type}&query={title}&ids={tmdb}%2C%20{tvdb}%2C%20{imdb}'
	elif type == 'tv':
		episode_name = title.replace(',',' ')
		episode_num = str(episode)
		season_num = str(season)
		extra = f'&tvdata={episode_name}%2C%20{episode_num}%2C%20{season_num}'
		#extra = f'&tvdata={episode_num}%2C%20{season_num}'
		return f'plugin://plugin.video.jacktook/search?mode={type}&query={title}&ids={tmdb}%2C%20{tvdb}%2C%20{imdb}' + extra

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

def haru_url(title):
	# ref: https://github.com/pikdum/plugin.video.haru/blob/master/resources/lib/nyaa.py
	return f'plugin://plugin.video.haru/?action=nyaa_search_results&text={quote(title)}&category=1_0&sort=seeders&order=desc'

def play(url, mode = 'resolved', li = None):
	if li == None:
		li = xbmcgui.ListItem(path=url)
	# play url
	if mode == 'resolved':
		xbmcplugin.setResolvedUrl(plugin.handle, True, li)
	elif mode == 'media':
		xbmc.executebuiltin("PlayMedia(%s)" % url)
	elif mode == 'plugin':
		xbmc.executebuiltin('RunPlugin(%s)' % url)
	elif mode == 'player':
		xbmc.Player().play(url, li)

def createFolder(function, label, arguments_list, image = icon_img, plot = '', thumb = icon_img, cm_items = []):
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
	if len(cm_items) > 0: li.addContextMenuItems(cm_items)
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
		similar_item = (localStr(32014), 'Container.Update(%s)' % (similar_link))
		CM_items.append(similar_item)
		# context menu for title search
		title_search = (localStr(32000), 'RunPlugin(%s)' % (kwargs['title_search']))
		CM_items.append(title_search)
		# context menu for original title search
		title_item = (localStr(32015), 'RunPlugin(%s)' % (kwargs['real_title_search']))
		CM_items.append(title_item)
		# add context menu to ListItem
		li.addContextMenuItems(CM_items)

	except Exception as e:
		import traceback
		log(traceback.format_exc())
		log(e)

	isFolder = kwargs['isFolder'] if 'isFolder' in kwargs else False
	addDirectoryItem(plugin.handle, url, li, isFolder = isFolder)

def endDirectory():
	endOfDirectory(plugin.handle, succeeded=True, cacheToDisc=True)

