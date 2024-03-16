# -*- coding: utf-8 -*-
# Copyright (C) 2024 gbchr

from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import os
from resources.lib import utils

ADDON_PATH = utils.home

# Constants
ACTION_LEFT = 1
ACTION_RIGHT = 2
ACTION_UP = 3
ACTION_DOWN = 4
ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6
ACTION_SELECT_ITEM = 7
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_SHOW_INFO = 11
ACTION_NEXT_ITEM = 14
ACTION_PREV_ITEM = 15

ACTION_MOUSE_WHEEL_UP = 104
ACTION_MOUSE_WHEEL_DOWN = 105
ACTION_MOUSE_MOVE = 107

KEY_NAV_BACK = 92
KEY_CONTEXT_MENU = 117
KEY_HOME = 159


def create_players_dict(title, year, tmdb_id, imdb_id, tvdb_id, mediatype, elementum_type, season, episode):
	return [
		{
			'label1':'Elementum',
			'label2':utils.localStr(32006),
			'title': title,
			'icon': 'elementum_icon.png',
			'imdb':imdb_id, 'tmdb':tmdb_id, 'tvdb':tvdb_id,
			'url': utils.elementum_url(elementum_type, title, year, tmdb_id),
			'url_type': 'player'
		},
		{
			'label1':'Jacktook',
			'label2':utils.localStr(32007),
			'title': title,
			'icon': 'jacktook_icon.png',
			'imdb':imdb_id, 'tmdb':tmdb_id, 'tvdb':tvdb_id,
			'url': utils.jacktook_url(mediatype, title, tmdb_id, imdb_id, tvdb_id, season, episode),
			'url_type': 'container'
		},
		{
			'label1':'Torrest',
			'label2':utils.localStr(32008),
			'title': title,
			'icon': 'torrest_icon.png',
			'imdb':imdb_id, 'tmdb':tmdb_id, 'tvdb':tvdb_id,
			'url': utils.torrest_url(title, year),
			'url_type': 'player'
		}
	]

class DialogSelect(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self)
        self.items = kwargs['items']
        self.title = kwargs['title']
        #self.plugin = kwargs['plugin']
        self.item_info = kwargs['item_info']
        self.count = 0
        self.retval = -1

    def onInit(self):
        self.getControl(32501).setLabel(self.title) # dialog title
        self.getControl(32505).setLabel(self.item_info) # item IDs
        for item in self.items:
            self.addItem(item)
        self.setFocusId(32503)

    def onClick(self, controlId):
        if controlId == 32500: # Close Button
            self.close()
        elif controlId == 32503: # Panel
            listControl = self.getControl(32503)
            selected = listControl.getSelectedItem()
            self.retval = int(selected.getProperty('index'))
			# play url
            if self.items[self.retval]['url_type'] == 'player':
                utils.play(selected.getPath(), 'player', selected)
            elif self.items[self.retval]['url_type'] == 'container':
                utils.update(selected.getPath())
            self.close()

    def onAction(self, action):
        if action.getId() in [ACTION_PARENT_DIR, KEY_NAV_BACK, ACTION_PREVIOUS_MENU]:  # NOQA
            self.close()

    def addItem(self, itemdata):
        listControl = self.getControl(32503)
        imdb = itemdata['imdb']
        tmdb = itemdata['tmdb']
        tvdb = itemdata['tvdb']
        item = xbmcgui.ListItem(itemdata['label1'], itemdata['label2'], path=itemdata['url'])
        item.setProperty('index', str(self.count))
        item.setProperty('IsPlayable', 'true')
        item.setProperty('IMDBNumber', imdb)
		#item.setContentLookup(False)
        #item.setProperty('ForceResolvePlugin', 'true')
        item.setArt({ 'icon': os.path.join(ADDON_PATH, "resources", "media", itemdata['icon']) })
        info_tag = item.getVideoInfoTag()
        info_tag.setTitle(itemdata['title'])
        info_tag.setFilenameAndPath(itemdata['url'])
        info_tag.setMediaType("video")
        info_tag.setIMDBNumber(imdb)
        info_tag.setUniqueIDs({"imdb": str(imdb), "tmdb": str(tmdb), "tvdb": str(tvdb)}, 'imdb')
        listControl.addItem(item)
        self.count += 1

