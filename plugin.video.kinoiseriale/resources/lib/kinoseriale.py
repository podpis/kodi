# -*- coding: utf-8 -*-

import urllib2,urllib
import os
import re
import base64,json
import cookielib


BASEURL='http://www.kinoiseriale.tv'
TIMEOUT = 10

UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'


# COOKIEFILE = r'C:\Users\ramic\AppData\Roaming\Kodi\addons\plugin.video.efilmy\resources\lib\1efimly.cookie'
COOKIEFILE=''
BRAMKA = 'http://www.bramka.proxy.net.pl/index.php?q='

def getUrl(url,data=None,header={},useCookies=True,saveCookie=False):
    if COOKIEFILE and os.path.isfile(COOKIEFILE) and useCookies:
        cj = cookielib.LWPCookieJar()
        cj.load(COOKIEFILE)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    
    req = urllib2.Request(url,data)
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link =  response.read()
        response.close()
        if COOKIEFILE and os.path.isfile(COOKIEFILE) and saveCookie and useCookies:
             cj.save(COOKIEFILE, ignore_discard = True) 
    except urllib2.HTTPError as e:
        #link = e.read()
        link = ''
    return link

url='http://www.kinoiseriale.tv/filmy/szukaj.html?ask=Wyszukaj+Film&mode=2&type=0&qual=0&gat=1&rok=0&stype=1&site=1'
url='http://www.kinoiseriale.tv/rankingi.html?typ=rating'
url='http://www.kinoiseriale.tv/filmy/szukaj.html?ask=Wyszukaj+Film&stype=2&site=1'
def scanMainpage(url,page=1):
    if 'site=' in url:
        url = re.sub('site=\d+','site=%d'%page,url)
    else:
        url = url + '&site=%d' %page
    content = getUrl(url)
    
    nextPage=False
    next_url=url.replace('http://www.kinoiseriale.tv','').replace('site=%d'%page,'site=%d' %(page+1))
    if content.find(next_url.split('//')[-1])>-1:
        nextPage = page+1
   
        
    ids = [(a.start(), a.end()) for a in re.finditer('<div (class|id)="movielisting">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        img = re.compile('<img src="(.*?)"').search(subset)
        title  = re.compile('class="movie-maintitle">(.*?)</a>').search(subset)
        title2 = re.compile('class="movie-subtitle">(.*?)</a>').search(subset)
        plot = re.compile('<div class="moviedesc">(.*?)</div>',re.DOTALL).search(subset)
        year =  re.compile('<span class="movieyear">(.*?)</span>').search(subset)
        quality = re.compile('<div class="moviemodes">(.*?)</div>').search(subset)
        
        language = re.compile('<div class="movietypes">(.*?)</div>',re.DOTALL).search(subset)
        if language:
            lang = re.compile('title="(.*?)"').findall(language.group(1))
            print lang
        
        href = re.compile('<a href="(.*?)">').search(subset)
        vote = re.compile('<div class="voting-box"><p>Ocena:</p><h1>(.*?)</h1><p>(.*?)</p></div>').search(subset)
        
        if href and title:
            img = img.group(1).replace('/small/filmy','/filmy') if img else ''

            one = {'href'   : BASEURL+href.group(1),
                'title'  : unicodePLchar(title.group(1)),
                'plot'   : unicodePLchar(plot.group(1)) if plot else '',
                'img'    : img,
                'rating' : vote.group(1).replace(',','.') if vote else '?',
                'year'   : year.group(1) if year else '?',
                'code'  : quality.group(1) if quality else '?',
                    }
            if one['title'] and one['href']:
                out.append(one)
    prevPage = page-1 if page>1 else False
    return (out, (prevPage,nextPage))    

url='http://www.kinoiseriale.tv/serial/ally-mcbeal.html'
url='http://www.kinoiseriale.tv/serial/allo-allo.html'
#out=scanTVshow(url)
def scanTVshow(url):
    content = getUrl(url)
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="sezon"', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        seasonNumber = re.compile('<meta content="(.*?)" itemprop="seasonNumber">').search(subset)
        seasonNumber = seasonNumber.group(1) if seasonNumber else '0'
        
        jds = [(a.start(), a.end()) for a in re.finditer('<div class="epizod"', subset)]
        jds.append( (-1,-1) )
        for j in range(len(jds[:-1])):
            epizod = subset[ jds[j][1]:jds[j+1][0] ] 
            episodeNumber = re.compile('itemprop="episodeNumber">(.*?)<').search(epizod)
            episodeNumber = episodeNumber.group(1) if episodeNumber else '0'
            
            href = re.compile('<a href="(.*?)"').search(epizod)
            href.group(1)
            titlee = re.compile('<span itemprop="name">(.*?)</span>').search(epizod)
            
            language = re.compile('<div class="odctypes">(.*?)</div>',re.DOTALL).search(epizod)
            if language:
                lang = re.compile('title="(.*?)"').findall(language.group(1))
                print lang
                
            if href and titlee:
                title = 'S%02dE%02d %s' %(int(seasonNumber),int(episodeNumber), titlee.group(1))
                one = {'href'  : BASEURL+href.group(1),
                    'title' : unicodePLchar(title)}
                out.append(one)
    return out
        
def getGatunekRok(rodzaj='film',typ='gat'):
    content = getUrl('http://www.kinoiseriale.tv/filmy/szukaj.html')
    if BRAMKA:
        content=content.replace(BRAMKA,'')
        content=re.sub(r'href=[\'"]?([^\'" >]+)',my_replace,content)
        #re.findall(r'href=[\'"]?([^\'" >]+)', content)
    selected = []
    if rodzaj=='film':
        if typ=='gat': #gatunek
            #selected = re.compile('<a href="(http://cda-online.pl/kategoria/.*?/)" >(.*?)</a> <span>(\d+)</span>').findall(content)
            selected = re.compile('onclick="fsURL\(\'gat\',\'(.*?)\'\)">(.*?)</a>').findall(content)
        elif typ=='rok':
            selected = re.compile('<option value="(\d{4})">(\d{4})</option>').findall(content)
        elif typ=='mode': #jakosc
            selected = re.compile('onclick="fsURL\(\'mode\',\'(.*?)\'\)">(.*?)</a>').findall(content)
        elif typ=='type': #jezyk
            selected = re.compile('onclick="fsURL\(\'type\',\'(.*?)\'\)">[ \n\t]*<img src=".*?" alt="(.*?)"').findall(content)    
      
    elif rodzaj=='serial':
        if typ=='gat':
            selected = re.compile('onclick="fsURL\(\'gat\',\'(.*?)\'\)">(.*?)</a>').findall(content)
    if selected:
        url_list = [x[0] for x in selected]
        display = [unicodePLchar(' '.join(x[1:])) for x in selected]
        return (display,url_list)
    return False        

def Rankingi(url='http://www.kinoiseriale.tv/rankingi.html'):
    content = getUrl(url)
    out=[]
    items = re.compile('<li><a href="(.*?)" title="(.*?)">.*?</a></li>').findall(content)
    for item in items:
        if 'rankingi' in item[0] or 'top' in item[0]:
            out.append({'title':unicodePLchar(item[1]),'url':BASEURL+item[0]})
    return out

#url='http://www.kinoiseriale.tv/filmonline/7557/za-murami-derriE3A8re-les-murs.html'
#url='http://www.kinoiseriale.tv/odcinek/45376/the-best-of-allo-allo-allo-allo-wspomnien-czar.html'
def getVideoLinks(url):
    outL=[]
    print url
    content = getUrl(url,useCookies=False)
    players = re.compile('<a href="#" onclick="pswitch\(\'(\d+)\'\)">(.*?)</a>').findall(content)
    link = re.compile('<iframe src="(.*?)" class="joyframe"').findall(content)
    if link:
        link = link[0].split('=')[0]+'='
        
        for id,player in players:
            # Here get only retular
            data = getUrl(link+id,useCookies=False)
            href = re.compile('href = "(.*?)"').findall(data)
            if href:
                video_link=href[0]
                if 'offcard.net' in video_link:
                    data = getUrl(video_link,useCookies=True,header={'User-Agent':UA,'Referer':link+id})
                    href = re.compile('{url: "(.*?)"}').findall(data)
                    if href:
                        p='|SwfUrl=http://offcard.net/static/player/flowplayer-3.2.8.swf'
                        video_link = href[0]# +'|SwfUrl=http://offcard.net/static/player/flowplayer-3.2.8.swf'
                        player = 'offcard.net'
                        print video_link
                        
                    else:
                        continue
                outL.append({'url':video_link,'host':player,'title': '%s' %player})
    return outL
  

def unicodePLchar(txt):
    txt = txt.replace('&infin;','Wszstkie')
    txt = txt.replace('#038;','')
    txt = txt.replace('&lt;br/&gt;',' ')
    txt = txt.replace('&#34;','"')
    txt = txt.replace('&#39;','\'').replace('&#039;','\'')
    txt = txt.replace('&#8221;','"')
    txt = txt.replace('&#8222;','"')
    txt = txt.replace('&#8217;','\'')
    txt = txt.replace('&#8211;','-').replace('&ndash;','-')
    txt = txt.replace('&quot;','"').replace('&amp;quot;','"')
    txt = txt.replace('&oacute;','ó').replace('&Oacute;','Ó')
    txt = txt.replace('&amp;oacute;','ó').replace('&amp;Oacute;','Ó')
    #txt = txt.replace('&amp;','&')
    txt = txt.replace('\u0105','ą').replace('\u0104','Ą')
    txt = txt.replace('\u0107','ć').replace('\u0106','Ć')
    txt = txt.replace('\u0119','ę').replace('\u0118','Ę')
    txt = txt.replace('\u0142','ł').replace('\u0141','Ł')
    txt = txt.replace('\u0144','ń').replace('\u0144','Ń')
    txt = txt.replace('\u00f3','ó').replace('\u00d3','Ó')
    txt = txt.replace('\u015b','ś').replace('\u015a','Ś')
    txt = txt.replace('\u017a','ź').replace('\u0179','Ź')
    txt = txt.replace('\u017c','ż').replace('\u017b','Ż')
    return txt    