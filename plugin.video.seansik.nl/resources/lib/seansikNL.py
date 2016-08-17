# -*- coding: utf-8 -*-

import urllib2,urllib
import re,os
import base64,json

TIMEOUT = 10
UA='Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'

def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', UA)
    response = urllib2.urlopen(req,timeout=TIMEOUT)
    link = response.read()
    response.close()
    return link
    
# url='http://www.seansik.nl/filmy-online/kategoria[1,2]+'
# filmy,pagination=scanMainpage(url,page=1)

def scanMainpage(url,page=1,data=None):
   
    if 'strona' in url:
        url = re.sub(r'strona\[\d+\]','strona[%d]'%page,url)
    else:
        url = url + 'strona[%d]+'%page
    
    content = getUrl(url,data)
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="pattern clearfix movie">', content)]
    if not ids:
        ids = [(a.start(), a.end()) for a in re.finditer('<div class="cartoon">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<a href="(.*?)"',re.DOTALL).findall(subset)
        title = re.compile('<h2 class="headline">(.*?)</h2>',re.DOTALL).findall(subset)
        title = title[0] if title else ''
        plot = re.compile('<p class="description">(.*?)</p>',re.DOTALL).findall(subset)
        img = re.compile('<img src="(.*?)"',re.DOTALL).findall(subset)
        year = ''
        lang = ''
        if title:
            year =  re.compile('(\d{4})',re.DOTALL).findall(title)
            title = re.sub('\(\d{4}\)','',title) if year else title   
            lang = re.compile('\[(.*?)\]',re.DOTALL).findall(title)
            title = re.sub('\[(.*?)\]','',title) if lang else title

        if href and title:
            one = {'href'   : href[0],
                'title'  : unicodePLchar(title.strip()),
                'plot'   : unicodePLchar(plot[0]) if plot else '',
                'img'    : img[0] if img else '',
                'year'   : year[0] if year else '',
                'code'   : lang[0] if lang else '',
                    }
            out.append(one)

    nextPage=False
    if content.find('strona[%d]'%(page+1))>-1:
        nextPage = page+1
        
    prevPage = page-1 if page>1 else False
    return (out, (prevPage,nextPage))


def scanTVshows():
    url='http://www.seansik.nl/seriale-online/'
    out=[]
    content = getUrl(url)
    ul=re.compile('<ul class="default-list">(.*?)</ul>',re.DOTALL).findall(content)
    if ul:
        shows = re.compile('<a href="(.*?)">(.*?)</a>').findall(ul[0])
        for href,title in shows:
           out.append({'href': href,'title':unicodePLchar(title.strip())})
    return out

#url='http://www.seansik.nl/serial/allo-allo/42'
def scanEpisodes(url):
    content = getUrl(url)
    episodes = re.compile('<li class="episode"><a href="(.*?)">(.*?)</a></li>').findall(content)
    out=[]    
    for href,title in episodes:
        out.append({'href': href,'title':unicodePLchar(title.strip())})
    return out

#url='http://www.seansik.nl/film/excentrycy-czyli-po-sonecznej-stronie-ulicy-2015-pl/16249'
#url='http://www.seansik.nl/allo-allo/the-british-are-coming-anglicy-nadchodz-cz-1/odcinek-1-sezon-1/1937'
def getVideoLinks(url):
    content = getUrl(url)
    out=[]
    ul = re.compile('<ul id="source">(.*?)</ul>',re.DOTALL).findall(content)
    if ul:
        sources = re.compile('data-iframe="(.*?)">(.*?)</a>',re.DOTALL).findall(ul[0])
        for href,host in sources:
            if host and href:
                h = base64.b64decode(href)
                if 'seansik' in h:
                    data = getUrl(h)
                    h=re.compile('src="(.*?)"',re.DOTALL).findall(data)
                    h= h[0] if h else ''
                if h:
                    out.append({'url' : h,'host': host,})
    return out
 

def Search(txt='dom'):
    url='http://www.seansik.nl/index.php?url=search/get/&search=%s'%urllib.quote(txt)
    content= getUrl(url)
    content = content.replace('\\','')
    try:
        content = content.replace('/thumb/','/normal/')
        out = eval(unicodePLchar(content))
    except:
        out=[]
    return out

    
#filter('gatunek')
#filter('rok')
def filter(what):
    content = getUrl('http://www.seansik.nl/filmy-online/')
    if   what == 'gatunek':
        filter = re.compile('<ul id="filter-category" class="filter">(.*?)</ul>',re.DOTALL).findall(content)
        pattern = 'kategoria[%s]+'
    elif what =='rok':
        filter = re.compile('<ul id="filter-year" class="filter">(.*?)</ul>',re.DOTALL).findall(content)
        pattern = 'rok[%s]+'
    else:
        filter = []
    if filter:
        items = re.compile('<li data-id="(.*?)"[^>]*>(.*?)</li>',re.DOTALL).findall(filter[0])
        kat = [pattern%x[0] for x in items]
        display = [x[1] for x in items]
        return (display,kat)
    return (None,None)

##
def unicodePLchar(txt):
    txt = txt.replace('&nbsp;','')
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
    txt = txt.replace('&amp;','&')
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