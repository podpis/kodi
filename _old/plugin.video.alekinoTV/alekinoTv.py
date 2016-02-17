# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 10:09:33 2015

@author: rakowski
"""

import urllib,urllib2
import re

#from time import localtime, strftime

BASEUrl = 'http://alekino.tv'

def getUrl(url,post_data=None):
    if post_data:
        dataPost = urllib.urlencode(post_data)
        req = urllib2.Request(url,dataPost)
    else:
        req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def listItemsFilmy(subpage="/filmy",filtr='',page=1):
    tmp_url=BASEUrl+ subpage  +'?' + filtr +'&p='+ str(page)
    link = getUrl(tmp_url)
    LIST=[]
    match = re.compile('<div class="row-fluid span12 movie-item">(.*?)<div class="clearfix">', re.DOTALL).findall(link)
    for i in range(len(match)):
        one={}
        match1 = re.compile('<a class="title" href="(.*?)">(.*?)</a>', re.DOTALL).findall(match[i])
        one['Title'] = match1[0][1].replace('<small>','').replace('</small>','')
        one['href'] = match1[0][0].decode('utf8')   
        match2 = re.compile('<p class="cats">.* <a href="(.*?)">(.*?)</a>.*</p>', re.DOTALL).findall(match[i])
        if match2:
            one['Genre']=match2[0][1].decode('utf8')  
        match3 = re.compile('<p class="desc">(.*?)</p>', re.DOTALL).findall(match[i])
        if match3:
            one['Plot']=match3[0].strip(' \r\t\n').decode('utf8')   
        match4 = re.compile('<div class="pull-left thumb" style="background-image:url\((.*?)\);">', re.DOTALL).findall(match[i])
        if len(match4) > 0:
            one['img'] = match4[0].decode('utf8')[:-5]+'l.jpg'
        LIST.append(one)
    return LIST

def filmyKategorie(subpage="/filmy"):
    tmp_url=BASEUrl+ subpage
    link = getUrl(tmp_url)
    LIST=[]
    
    match = re.compile('<!-- blok z kategoriami -->(.*?)<!-- /blok z kategoriami -->', re.DOTALL).findall(link)
    match1 = re.compile('<li class="filterParent"><a href="#" data-type="filter" data-value="(.*?)" data-filter="(.*?)\[\]">(.*?)</a> <span class="w">(.*?)</span></li>', re.DOTALL).findall(match[0])
    
    for i in range(len(match1)):
        one={}
        one['Title'] = ' '.join(match1[i][-2:])
        one['Filtr'] = '%s[0]=%s' % (match1[i][1],match1[i][0])
        LIST.append(one)
    return LIST

#L=listItemsFilmy(filtr='sorting=movie.rate',page=1)

def maxuploadtv(url='http://maxupload.tv/e/Nb7a'):
    link = getUrl(url)
    postdata = {'ok': 'yes', 'Close Ad and Watch as Free User': 'confirm', 'true': 'submited'}
    link = getUrl(url, postdata)
    match = re.compile("url: \'(.*?)\'\r\n").findall(link)
    #print("Link",match,link)
    if len(match) > 0:
        return match[0]
    else:
        return ''

def getVidoLink(href='/film/gabriel-1'):
    link = getUrl(BASEUrl + href)
    match1 = re.compile('<a href="#" data-type="player" data-version="standard" data-id="(.*?)">', re.DOTALL).findall(link)
    url1 = "http://alekino.tv/players/init/" + match1[0] + "?mobile=false"
    link = getUrl(url1)
    match15 = re.compile('"data":"(.*?)"', re.DOTALL).findall(link)
    hash = match15[0].replace('\\','')
    post_data = {'hash': hash}
    data = getUrl('http://alekino.tv/players/get',post_data)
    match16 = re.compile('<iframe src="(.*?)" (.*?)', re.DOTALL).findall(data)
    linkVideo = ''
    if len(match16) > 0:
        if match16[0][0].startswith('http://maxupload'):
            linkVideo = maxuploadtv( match16[0][0].decode('utf8'))
            linkVideo = linkVideo + '|Referer=http://alekino.tv/assets/alekino.tv/swf/player.swf'
    return linkVideo


def alekinoSzukaj(query='bolek'):
    LIST = []
    if not query:
        return LIST;
    url=BASEUrl + '/szukaj?query='+ query.replace(' ','%20') + '&x=0&y=0'
    link = getUrl(url)
    match = re.compile('<!-- Znalezione filmy -->(.*?)<!-- Znalezione seriale -->', re.DOTALL).findall(link)
   
    match1 = re.compile('<div class="result box pl-round" style="margin-bottom:10px;">\n(.*?)<a href="(.*?)"><img src="(.*?)" alt="" title="" height="133" width="100"></a>\n(.*?)<a href="(.*?)"(.*?)>(.*?)</a>', re.DOTALL).findall(match[0])
    
    h_i_t = [(x[1],x[2],x[6]) for x in match1]  
    descs = re.compile('<p>(.*?)</p>', re.DOTALL).findall(match[0])
    descs = [x.strip(' \n\t') for x in descs]
    ocena = re.compile('Ocena to:(.*?)<strong>(.*?)</strong>', re.DOTALL).findall(match[0])
    ocena = [''.join(x).strip(' \t\n') for x in ocena]
    gatun = re.compile('<span class="small-bread">(.*?)</span>', re.DOTALL).findall(match[0])
    gatun = [' '.join(x.replace('<br>','').split()) for x in gatun]
    
    len(h_i_t)
    len(gatun) 
    len(ocena)
    len(descs)

    for i in range(len(h_i_t)):
        one={}
        one['Title'] = h_i_t[i][2] + ' ('+ ocena[i] +')'
        one['href'] = h_i_t[i][0]
        one['Genre'] = gatun[i]
        one['Plot'] =descs[i]    
        one['img'] = h_i_t[i][1]
        LIST.append(one)
    return LIST
        

#alekinoSzukaj('home')


