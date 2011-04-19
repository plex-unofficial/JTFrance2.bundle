# -*- coding: Latin-1 -*-

"""
Author: Pierre Della Nave 
Date: May 2009
Revision: 0.1

Acknowledgements and Credits:
SesameStreet Plugin
France2 Plugin by Erwan Loisant

 Copyright (c) 2008 Erwan Loisant <eloisant@gmail.com>

 This file may be used under the terms of the
 GNU General Public License Version 2 (the "GPL"),
 http://www.gnu.org/licenses/gpl.html

 Software distributed under the License is distributed on an "AS IS" basis,
 WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 for the specific language governing rights and limitations under the
 License.
"""
import PMS
from PMS import Plugin, Log, XML, HTTP
from PMS.Objects import *
from PMS.Shortcuts import *
import re
import unicodedata

PLUGIN_PREFIX           = "/video/JTFrance2"
PLUGIN_ID               = "com.plexapp.plugins.JTFrance2"
PLUGIN_REVISION         = 0.3
PLUGIN_UPDATES_ENABLED  = True

WEB_ROOT = 'http://jt.france2.fr'

CACHE_INTERVAL = 3600 * 2

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, 'JT France2', 'icon-default.jpg', 'art-default.jpg')
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("ShowList", viewMode="List", mediaType="items")
  MediaContainer.title1 = 'Journal de France2'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################
def MainMenu():
  dir = MediaContainer(title1="Journal de France2", content = 'Items', art = R('art-default.jpg'))
  dir.viewGroup = 'ShowList'

  dir.Append(Function(DirectoryItem(sub_category, title="Journal de 8h" , thumb=R("logo_8h.jpg")), jt_category='8', title='Journal de 8h'))
  dir.Append(Function(DirectoryItem(sub_category, title="Journal de 13h" , thumb=R("logo_13h.jpg")), jt_category='13', title='Journal de 13h'))
  dir.Append(Function(DirectoryItem(sub_category, title="Journal de 20h" , thumb=R("logo_20h.jpg")), jt_category='20', title='Journal de 20h'))
  return dir

####################################################################################################

def get_jt_stream(html):
    stream_pattern = re.compile('"(mms://[^"]+)"')
    match = stream_pattern.search(html)
    if match != None:
      stream_url = match.group(1)
    return stream_url

####################################################################################################

def get_jt_name(html):
    html = html.encode("Latin-1")
    name_pattern = re.compile('<h3 class="itemTitle">([^<>]+)</h3>')
    match_name = name_pattern.search(html)
    if match_name != None:
      name = unicode(match_name.group(1),"utf-8")
    return name

####################################################################################################

from htmlentitydefs import name2codepoint 
def replace_entities(match):
    try:
        ent = match.group(1)
        if ent[0] == "#":
            if ent[1] == 'x' or ent[1] == 'X':
                return unichr(int(ent[2:], 16))
            else:
                return unichr(int(ent[1:], 10))
        return unichr(name2codepoint[ent])
    except:
        return match.group()

entity_re = re.compile(r'&(#?[A-Za-z0-9]+?);')
def html_unescape(data):
    return entity_re.sub(replace_entities, data)

####################################################################################################

def get_jt_summary(html):
    html = html.encode("utf-8")
    html = html_unescape(html)
    summary_pattern = re.compile('class="subjecttimer.*>(.*)</a>')
    try:
    	match_summary = summary_pattern.findall(html.replace('</li>','\n'))
        summary = ''
    	if match_summary != None:
    		for str in match_summary:
			Log(str)
			summary = summary + str +'\n'
    except:
    	summary = "Sommaire non disponible"
    if summary == '':
	summary = "Sommaire non disponible"
    return summary

####################################################################################################

def sub_category (sender, jt_category, title = None, replaceParent=False, values=None):

  dir = MediaContainer(title1="", title2=title, replaceParent=replaceParent)
  dir.viewGroup = 'Details'
  base_address = 'http://info.francetelevisions.fr/video-info/player_html/blochtml.php?id-categorie=JOURNAUX_LES_EDITIONS_NATIONALES_'+jt_category+'H'
  logo_string = 'logo_'+jt_category+'h.jpg'

  html = HTTP.Request(base_address+"&bloc=categorie",encoding="Latin-1")
  archives_pattern = re.compile('"itemTitle".*id-video=(.*)&autres')

  videolist = archives_pattern.findall(html) 
  for video in videolist:
    html = HTTP.Request(base_address+"&bloc=player"+"&id-video="+video,encoding='Latin-1')
    dir.Append(VideoItem(get_jt_stream(html),get_jt_name(html),'',get_jt_summary(html),'',R(logo_string)))
    
  return dir

####################################################################################################

