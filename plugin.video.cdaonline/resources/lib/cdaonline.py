# -*- coding: utf-8 -*-

import urllib2
import re
 
BASEURL=''
TIMEOUT = 5
 
def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link = response.read()
        response.close()
    except:
        link=''
    return link

def scanMainpage(url,page=1):
    url += '/' if url[-1] != '/' else ''
    content = getUrl(url + 'page/%d/' %page)
    nextpage=False
    if content.find(url + 'page/%d/' %(page+1))>0:
        nextpage = page+1
        
    ids = [(a.start(), a.end()) for a in re.finditer('<div id=\"mt.*\" class=\"item\">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<div class="boxinfo">[\s\n]+<a href="(.*?)">',re.DOTALL).search(subset)
        title = re.compile('<span class="tt">(.*?)</span>',re.DOTALL).search(subset)
        plot = re.compile('<span class="ttx">\n(.*?)(?:<div class="degradado"></div>){0,1}[\s\n]*</span>[\s\n]*',re.DOTALL).search(subset)
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
                'plot'   : unicodePLchar(plot.group(1)) if plot else '',
                'img'    : img,
                'rating' : imdb.group(1) if imdb else '?',
                'year'   : year.group(1) if year else '?',
                'code'  : quality.group(1) if quality else '?',
                    }
            out.append(one)
    nextPage=False
    if content.find(url + 'page/%d/' %(page+1))>0:
        nextPage = page+1
    prevPage = page-1 if page>1 else False
    return (out, (prevPage,nextPage))
 
def _getOrginalURL(url,host=''):
    orginal_link=''
    if url.startswith('http'):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
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
    return orginal_link

def getVideoLinks(url):
    content = getUrl(url)
        
    ids = [(a.start(), a.end()) for a in re.finditer('<li class="elemento">', content)]
    ids.append( (-1,-1) )
    out=[]
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
            href_go = 'http'+ href.group(1).split('http')[-1]
            link = _getOrginalURL(href_go.replace('http://cda-online.pl?',''),host)
            
            if link:
                if 'openload' in host:
                    continue
                one = {'url' : link,
                    'title': "[%s] %s, %s" %(host,j,q),
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


def getGatunekRok(rodzaj='film',typ='gatunek'):
    content = getUrl('http://cda-online.pl/')
    selected = []
    if rodzaj=='film':
        if typ=='gatunek':
            selected = re.compile('<a href="(http://cda-online.pl/kategoria/.*?/)" >(.*?)</a> <span>(\d+)</span>').findall(content)
        else:
            selected = re.compile('<a href="(http://cda-online.pl/rok/\d{4}/)">(\d{4})</a>').findall(content)
    elif rodzaj=='serial':
        if typ=='gatunek':
            selected = re.compile('<a href="(http://cda-online.pl/seriale-gatunek/.*?/)" >(.*?)</a> <span>(\d+)</span>').findall(content)
        else:
            selected = re.compile('<a href="(http://cda-online.pl/seriale-rok/\d{4}/)">(\d{4})</a>').findall(content)
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
    

if __name__=="dupa":
    url='http://cda-online.pl/filmy-online/'
    url='http://cda-online.pl/seriale-rok/2016'
    url='http://cda-online.pl/rok/2015/'
    url='http://cda-online.pl/seriale/'
    url='http://cda-online.pl/rok/2016/'
    out,pagination = scanMainpage(url,1)
    out[0].get('img')
    ## get vidoe sources
    url = out[0].get('href')
    links = getVideoLinks(url)

    ## get tv show episodes
    url='http://cda-online.pl/seriale/breaking-bad/'
    out = scanTVshow(url)
    url = out[0].get('href')
    links = getVideoLinks(url)
    
    url='http://cda-online.pl/igrzyska-smierci-kosoglos-czesc-2/'
    links = getVideoLinks(url)
    _getOrginalURL('http://go.cda-online.pl/Juv6D')
    data=getGatunekRok(rodzaj='film',typ='gatunek')
 
    