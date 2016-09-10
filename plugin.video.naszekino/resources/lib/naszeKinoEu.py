# -*- coding: utf-8 -*-

import sys,os,re
import urllib,urllib2
import urlparse


BASEURL='http://nasze-kino.eu'
#http://nasze-kino.eu/film/mission-impossible-rogue-nation-mission-impossible-5-2015-lektor-pl/3476

def unicodePLchar(txt):
    txt = txt.replace('#038;','')
    txt = txt.replace('&nbsp;','')
    txt = txt.replace('&lt;br/&gt;',' ')
    txt = txt.replace('&#34;','"')
    txt = txt.replace('&#39;','\'').replace('&#039;','\'')
    txt = txt.replace('&#8221;','"')
    txt = txt.replace('&#8222;','"')
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

#url='http://nasze-kino.eu/gatunek/18/-bajki-/6'
#url='http://nasze-kino.eu/gatunek/46/-filmy-/'
def get_movie_relative(url,page='1'):
    url_split=url.split('/')
    if url_split[-1] == '': # current page
        myurl=url+'%s'%page
    else:
        url_split[-1]='%s'%page
        myurl = '/'.join(url_split)
    content=getUrl(myurl)
    out=[]
    items = re.compile('<div class="movie relative">(.*?</span></div>)',re.DOTALL).findall(content)
    pages = re.compile('<div class="pages">(.*?)<div class="clear">',re.DOTALL).findall(content)
    len(items)
    #item=items[0]
    for item in items:
        title=re.compile('<a href="(.*?)" title="(.*?)">').findall(item)
        img = re.compile('<img src="(/upload/.*?)"').findall(item)
        gatunek=re.compile('<span class="span">GATUNEK: <a href=".*?" title="(.*?)">(.*?)</a>').findall(item)
        jakosc =re.compile('<span class="span">JAKOŚĆ: <a href=".*?" title="(.*?)">(.*?)</a>').findall(item)
        wersja =re.compile('<span class="span">WERSJA: <a href=".*?" title="(.*?)">(.*?)</a>').findall(item)
        if title:
            gatunek = gatunek[0][0] if gatunek else ''
            jakosc = jakosc[0][0].split(' ')[0] if jakosc else ''
            wersja = wersja[0][0] if wersja else ''
            
            one = {'url':BASEURL+title[0][0],
                   'title':unicodePLchar(title[0][1]).decode('utf-8'),
                   'img':BASEURL+img[0],
                   'genre':unicodePLchar(gatunek).decode('utf-8'),
                   'code':unicodePLchar(jakosc).decode('utf-8'),
                   'label':unicodePLchar(wersja).decode('utf-8')
                   }
            out.append(one)
    return out

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]
    

# url='http://nasze-kino.eu/film/limitless-2015-sezon-1-napisy-pl/2589'
# url='http://nasze-kino.eu/film/w-samym-sercu-morza-in-the-heart-of-the-sea-2015-lektor-pl/5062'
#url='http://nasze-kino.eu/film/msciciel-z-wall-street-assault-on-wall-street-2013-lektor-pl/5091'
url='http://nasze-kino.eu/film/dzieciaki-mojej-siostry-na-tropie-zlota-my-canadian-adventure-quest-for-the-lost-gold-2015-lektor-pl/6719'
url='http://nasze-kino.eu/film/zielona-latarnia-green-lantern-2011-lektor-pl/6732'
url='http://nasze-kino.eu/film/godzilla-milleniumpowrot-godzilli-1999-lektor-pl/6718'
url='http://nasze-kino.eu/film/sekretne-zycie-zwierzakow-domowych-the-secret-life-of-pets-2016-lektor-ivo/8002'
def get_movie_links(url):
    content=getUrl(url)
    out={}
    #items = re.compile('<a href="(.*?)" target="\s*_blank">(.*?)</a>').findall(content)
    items = re.compile('<a href="([^"]*)" target="\s*_blank">(.*?)</a>').findall(content)
    for href,title in items:
        #print title
        if 'FORUM' in title:
            continue
        if not 'http://nasze-kino' in href:
            title = title.decode('utf-8')
            if not out.has_key(title):
                out[title]=[]
            out[title].append(href)
    if not out and items:
        print 'check forum'
        forum=getUrl(items[0][0])
        pre=re.compile('<pre class="bbcode_code" style="[^"]*">(.*?)</pre>',re.DOTALL).findall(forum)
        if pre:
            items = re.compile('<a href="([^"]*)" target="\s*_blank">').findall(pre[0])
            if items:
               out['OGLADAJ']=items
     
    #print sorted(out.keys(),key=natural_keys)
    return out

#linklist = ['http://videomega.tv/?ref=GqxDr09yL00Ly90rDxqG', 'http://streamin.to/39poh03bpa1h', 'http://vidto.me/phs8u1cezeoz.html', 'https://openload.co/f/UBNf7D2-nC8/M%C5%9Bciciel_z_Wall_Street_Assault_on_Wall_Street_%282013%29_PL.720p.BLURAY.x264.AC3-MX.mkv', 'http://www.cda.pl/video/61788937', 'http://videomega.tv/?ref=50Ki8ltOSttSOtl8iK05']
def host_link(linklist):
    hosts=[]
    links=[]
    for one in linklist:
        if one.startswith('http'):
            hosts.append(one.split('/')[2])
            links.append(one)
    return hosts,links
    

def header():
    content=getUrl(BASEURL)
    out={'gatunek':[],'jakosc':[],'wersja':[]}
    header = re.compile('<header>(.*?)</header>',re.DOTALL).findall(content)
    if header:
        header=header[0]
        items=re.compile('<li><a href="(.*?)" title="(.*?)" class=".*">(.*?)</a></li>').findall(header)
        for i in items:
            one = {'url':BASEURL+i[0],'title':unicodePLchar(i[1]).decode('utf-8')}
            if i[0].startswith('/gatunek/'):
                if '-' not in one['title']:
                    out['gatunek'].append(one)
            elif i[0].startswith('/wersja/'):
                out['wersja'].append(one)
            elif i[0].startswith('/jakosc/'):
                out['jakosc'].append(one)
    return out    

def polecane_filmy():
    content=getUrl(BASEURL)
    out=[]
    section = re.compile('<section>(.*?)</section>',re.DOTALL).findall(content)
    if section:
        section=section[0]
        items=re.compile('<a href="(.*?)" title="(.*?)"><img src="(.*?)" alt="(.*?)"[ \t]*/></a>').findall(section)
        for i in items:
            one = {'url':BASEURL+i[0],
                   'title':unicodePLchar(i[1]).decode('utf-8'),
                   'img':BASEURL+i[2]}
            out.append(one)
    return out 
    
def ostatnio_dodane_seriale():
    content=getUrl(BASEURL)
    out=[]
    section = re.compile('<center>(.*?)</center>',re.DOTALL).findall(content)
    if section:
        section=section[0]
        items=re.compile('<a href="(.*?)"><img src="(.*?)" alt="(.*?)" title="(.*?)" />').findall(section)
        for i in items:
            one = {'url':i[0],
                   'title':unicodePLchar(i[-1]).decode('utf-8'),
                   'img':i[1]}
            out.append(one)
    return out     

