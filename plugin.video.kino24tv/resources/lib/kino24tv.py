# -*- coding: utf-8 -*-

import urllib2,urllib
import re,os
import cfcookie,cookielib
from urlparse import urlparse

BASEURL='http://kino24-tv.pl'
TIMEOUT = 10
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'

COOKIEFILE=r'D:\cookie.cda'
BRAMKA = 'http://www.bramka.proxy.net.pl/index.php?q='
 
def _getUrl(url,data=None,cookies=None):
    #url = 'http://www.bramka.proxy.net.pl/index.php?q='+urllib.quote(url)
    #url = 'http://www.bramka.proxy.net.pl/index.php?q='+url
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', UA)
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link = response.read()
        response.close()
    except:
        link=''
    return link

def getUrl(url,data=None):
    cookies=cfcookie.cookieString(COOKIEFILE)
    content=_getUrl(url,data,cookies)
    if not content:
        cj=cf_setCookies(url,COOKIEFILE)
        cookies=cfcookie.cookieString(COOKIEFILE)
        content=_getUrl(url,data,cookies)
        if not content:
            content=_getUrl(BRAMKA+url,data,cookies)
    return content

def cf_setCookies(link,cfile):
    cj = cookielib.LWPCookieJar()
    cookieJar = cfcookie.createCookie(BASEURL,cj,UA)
    dataPath=os.path.dirname(cfile)
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)
    if cookieJar:
        cookieJar.save(cfile, ignore_discard = True) 
    return cj
    
# url='http://kino24-tv.pl/kategoria/filmy-online/'
# url=''
url='http://kino24-tv.pl/'
def scanMainpage(url,type=''):
  
    content = getUrl(url)
    
    nextPage=False
    next_url=re.compile('<div class="pag_b">(.*?)</div>').search(content)
    if next_url:
        next_url=re.compile('<a href="(.*?)"').search(next_url.group(1))
        nextPage = next_url.group(1) if next_url else False
    
    prevPage=False
    next_url=re.compile('<div class="pag_a">(.*?)</div>').search(content)
    if next_url:
        next_url=re.compile('<a href="(.*?)"').search(next_url.group(1))
        prevPage = next_url.group(1) if next_url else False
    
    out = []
    if type=='polecane':
        out = scan_polecane(content)
    elif 'kategoria' in url:
        out = scan_kategoria(content)
    else:
        out = scan_ostatnioDodane(content)

    return (out, (prevPage,nextPage))

def scan_kategoria(content):
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="fit item">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<a href="(.*?)">',re.DOTALL).search(subset)
        title = re.compile('<h1>(.*?)</h1>',re.DOTALL).search(subset)
        plot = re.compile('<div class="contenido"><p>(.*?)</p>',re.DOTALL).search(subset)
        img = re.compile('<img src="(.*?)"',re.DOTALL).search(subset)
        imdb = re.compile('<div class="a">.*<span>(.*?)</span>',re.DOTALL).search(subset)
       
        year =  re.compile('<a href="http://kino24-tv.pl/release-year/.*?" rel="tag">(.*?)</a>').search(subset)
        duration = re.compile('<b class="icon-time"></b>(.*?)</span> ').search(subset)
        quality = re.compile('<span class="calidad2">(.*?)</span>',re.DOTALL).search(subset)
        
        if href and title:
            img = img.group(1) if img else ''
            if img.startswith('//'):
                img = 'http:'+img
            one = {'href'   : href.group(1),
                'title'  : unicodePLchar(title.group(1)),
                'plot'   : unicodePLchar(plot.group(1).strip()) if plot else '',
                'img'    : img,
                'rating' : imdb.group(1) if imdb else '',
                'year'   : year.group(1) if year else '',
                'code'  : quality.group(1) if quality else '',
                    }
            out.append(one)
    return out
    

def scan_ostatnioDodane(content):    
    ids = [(a.start(), a.end()) for a in re.finditer('<div id=\"mt.*\" class=\"item\">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<div class="boxinfo">[\s\n]+<a href="(.*?)">',re.DOTALL).search(subset)
        title = re.compile('<span class="tt">(.*?)<',re.DOTALL).search(subset)
        #title = re.compile('<span class="tt">(.*?)</span>',re.DOTALL).search(subset)
        plot = re.compile('<span class="ttx">(.*?)<',re.DOTALL).search(subset)
        img = re.compile('<div class="image">[\s\n]+<img src="(.*?)"',re.DOTALL).search(subset)
        imdb = re.compile('<span class="imdbs">(.*?)</span>',re.DOTALL).search(subset)
        year =  re.compile('<span class="year">(.*?)</span>',re.DOTALL).search(subset)
        quality = re.compile('<span class="calidad2">(.*?)</span>',re.DOTALL).search(subset)
        
        if href and title:
            img = img.group(1) if img else ''
            if img.startswith('//'):
                img = 'http:'+img
            one = {'href'   : href.group(1),
                'title'  : unicodePLchar(title.group(1)),
                'plot'   : unicodePLchar(plot.group(1).strip()) if plot else '',
                'img'    : img,
                'rating' : imdb.group(1) if imdb else '',
                'year'   : year.group(1) if year else '',
                'code'  : quality.group(1) if quality else '',
                    }
            out.append(one)
    return out

url='http://kino24-tv.pl/'
def scan_polecane(content):
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="item">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<a href="(.*?)">',re.DOTALL).search(subset)
        title = re.compile('<span class="ttps">(.*?)<',re.DOTALL).search(subset)
        plot = re.compile('<div class="contenido"><p>(.*?)</p>',re.DOTALL).search(subset)
        img = re.compile('<img src="(.*?)"',re.DOTALL).search(subset)
        imdb = re.compile('<b class="icon-star"></b></b>(.*?)</span>',re.DOTALL).search(subset)
       
        year =  re.compile('<span class="ytps">(.*?)</').search(subset)
        quality = re.compile('<span class="calidad2">(.*?)</span>',re.DOTALL).search(subset)
        
        if href and title:
            img = img.group(1) if img else ''
            if img.startswith('//'):
                img = 'http:'+img
            one = {'href'   : href.group(1),
                'title'  : unicodePLchar(title.group(1).strip()),
                'plot'   : unicodePLchar(plot.group(1).strip()) if plot else '',
                'img'    : img,
                'rating' : imdb.group(1) if imdb else '',
                'year'   : year.group(1) if year else '',
                'code'  : quality.group(1) if quality else '',
                    }
            out.append(one)  
    return out
    
def Gatunki(url='http://kino24-tv.pl/'):
    content = getUrl(url)  
    out=[]
    categorias = re.compile('<div class="categorias">(.*?)</div>',re.DOTALL).findall(content)
    if categorias:
        cats = re.compile('<a href="(.*?)"[ ]*>(.*?)</a> <span>(.*?)</span>').findall(categorias[0])
        for href,title,amount in cats:
            one = {'href'   : href,
                'title'  : unicodePLchar('%s (%s)' %(title.strip(),amount)),
                    }
            out.append(one) 
    return out

    
def _getOrginalURL(url,host=''):
    orginal_link=''
    if url.startswith('http'):
        
        if 'linki.online' in url:
            content = getUrl(url)
            links = re.compile('top.location = [\'"](.*?)[\'"];').search(content)
            if links:
                orginal_link = links.group(1)
        if 'ouo.io' in url:
            orginal_link = url
        else:
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
            try:
                response = urllib2.urlopen(req)
                if response:
                    orginal_link=response.url
                    if orginal_link==url:
                        content=response.read()
                        links = re.compile('<a href="(.*)" class').findall(content)
                        for l in links:
                            if host in l:
                                orginal_link = l
                                break
                    response.close()
            except:
                pass
    return orginal_link

#url='http://kino24-tv.pl/kapitan-ameryka-wojna-bohaterow-captain-america-civil-war-2016-napisy-pl-dubbing-pl/'
def getVideoLinks_iframes(url,content=None):
    if not content:
        content = getUrl(url)
    
    out  =[]
    iframe = re.compile('<iframe (.*?)</iframe>',re.DOTALL).findall(content)
    #names = re.compile('<li>[\n\t ]*<a href="#div.*?".*?>(.*?)</a',re.DOTALL).findall(content)
    names = re.compile('<ul class="idTabs">(.*?)</ul>',re.DOTALL).findall(content)
    if names:
        names = [x.strip() for x in re.compile('>(.*?)<',re.DOTALL).findall(names[0]) if len(x.strip())]
    else:
        names=[]
    #frame = iframe[0]
    for frame in iframe:
        href = re.compile('src="(.*?)"',re.DOTALL).search(frame)
        if href:
            href_go = 'http'+ urllib.unquote(href.group(1)).split('http')[-1]
             
            if href_go.startswith('http') and not 'youtube' in href_go and not 'facebook' in href_go:
                #host = href_go.split('/')[2]
                host = urlparse(href_go).netloc
                one = {'url' : href_go,
                    'title': "[%s]" %(host),
                    'host': host    }
                out.append(one)
    if len(names)==len(out): # merge with names
        for one,name in zip(out,names):
            one['title'] += ' %s'%name
    return out

# out=getVideoLinks(url)
def getVideoLinks(url):
    content = getUrl(url)
        
    ids = [(a.start(), a.end()) for a in re.finditer('<li class="elemento">', content)]
    ids.append( (-1,-1) )
    
    out=getVideoLinks_iframes(url,content)
    
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<a href="(.*?)"',re.DOTALL).search(subset)
        host = re.compile('<img src="(?:.*?)" alt="(.*?)">[\s\n]+(.*?)</span>').search(subset)
        jezyk = re.compile('<span class="c">(.*?)</span>',re.DOTALL).search(subset)
        jakosc =re.compile('<span class="d">(.*?)</span>',re.DOTALL).search(subset)
        
        if href and host:
            j= jezyk.group(1) if jezyk else ''
            q= jakosc.group(1) if jakosc else ''
            host = host.groups()[-1]
            href_go = 'http'+ urllib.unquote(href.group(1)).split('http')[-1]
            
            print i,host,href_go,'\n'
            
            link = _getOrginalURL(href_go.replace('http://cda-online.pl?',''),host)
            
            if link:
                msg =''
                if 'ouo.io' in link:
                    msg = '[COLOR red] ouo.io not supported[/COLOR]'
                one = {'url' : urllib.unquote(link),
                    'title': "[%s] %s, %s %s" %(host,j,q,msg),
                    'host': host    }
                out.append(one)
    return out

def scanTVshow(url):
    content = getUrl(url)
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="numerando">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        hreftitle = re.compile('<a href="(.*?)">[\s\n]+(.*?)</a>',re.DOTALL).search(subset)
        date = re.compile('<span class="date">(.*?)</span>').search(subset)
    
        
        if hreftitle:
            d= date.group(1) if date else ''
            t= hreftitle.group(2) + ' ' + d
            one = {'href'  : hreftitle.group(1),
                'title' : unicodePLchar(t.strip())}
            out.append(one)
    return out

#rodzaj='serial'
#rodzaj='film'
# typ='gatunek'
# typ='rok'

def my_replace(m):
    return 'href="'+urllib.unquote(m.group(1))

def getGatunekRok(rodzaj='film',typ='gatunek'):
    content = getUrl(BASEURL)
    if BRAMKA:
        content=content.replace(BRAMKA,'')
        content=re.sub(r'href=[\'"]?([^\'" >]+)',my_replace,content)
        #re.findall(r'href=[\'"]?([^\'" >]+)', content)
    selected = []
    if rodzaj=='film':
        if typ=='gatunek':
            selected = re.compile('<a href="(http://kino24-tv.pl/kategoria/.*?/)" >(.*?)</a> <span>(.*?)</span>').findall(content)
        elif typ=='rok':
            selected = re.compile('<a href="(http://kino24-tv.pl/release-year/.*?/)">(.*?)</a>').findall(content)
        elif typ=='jakosc':
            selected = re.compile('<a href="(http://kino24-tv.pl/quality/.*?)">(.*?)</a>').findall(content)
    elif rodzaj=='serial':
        if typ=='gatunek':
            selected = re.compile('<a href="(http[s]://cda-online.pl/seriale-gatunek/.*?)"[\t\n ]*>(.*?)</a>').findall(content)
        elif typ=='rok':
            selected = re.compile('<a href="(http[s]://cda-online.pl/seriale-rok/\d{4}/)">(\d{4})</a>').findall(content)
    if selected:
        url_list = [x[0] for x in selected]
        display = [' '.join(x[1:]) for x in selected]
        return (display,url_list)
    return False

def unicodePLchar(txt):
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
    
