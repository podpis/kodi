# -*- coding: utf-8 -*-

import sys,os,re
import urllib,urllib2
import urlparse
import json

UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36'
BASEURL='http://on-anime.pl/'
TIMEOUT=10

def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', UA)

    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link = response.read()
        response.close()
    except:
        link=''
    return link

def get_anime(url='http://on-anime.pl/anime/'):
    content = getUrl(url)

    ids = [(a.start(), a.end()) for a in re.finditer('<a class="tl centruj"', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.search('href="(.*?)"',subset)
        img = re.search('<img src="(.*?)"',subset)
        title = re.compile('overflow:hidden;">(.*?)</div>',re.DOTALL).findall(subset)
        plot = re.compile('<div class="margin:5px;">(.*?)</div>',re.DOTALL).findall(subset)
        
        typ = re.compile('<span class="b">Typ: </span>(.*?)</div>',re.DOTALL).findall(subset)
        genre = re.compile('<span class="b">Gatunek: </span>(.*?)</div>',re.DOTALL).findall(subset)
        czas_trwania =re.compile('<span class="b">Czas trwania: </span>(.*?)</div>',re.DOTALL).findall(subset)
        rating = re.compile('<div style="background:url\(\'/grafika/ikonki/ulubione.png\'\); height:16px; width:(\d+.\d+)%;">').findall(subset)

        if href and title:
            title = title[0].strip()
            if czas_trwania:
                title = title + ' [COLOR lightblue]'+czas_trwania[0].strip()+'[/COLOR]'
            href = urlparse.urljoin(BASEURL,href.group(1))
            genre = [x.strip() for x in genre if x.strip()] if genre else []
            one = {'url'   : href,
                'title'  : unicodePLchar(title),
                'plot'   : unicodePLchar(plot[0].strip()) if plot else '',
                'img'    : urlparse.urljoin(BASEURL,img.group(1)) if img else '',
                'rating' : rating[0] if rating else '',
                'genre' : unicodePLchar(','.join(genre)) if genre else '',
                    }
            out.append(one)
    return out            

#url='http://on-anime.pl/anime/Akame-ga-Kill!'
def get_episodes(url):
    content = getUrl(url+'/odcinki')
    if not content:
        content = getUrl(url)
        
    ids = [(a.start(), a.end()) for a in re.finditer(' <div class="tab" style=', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        count   = re.compile('<div class="tp tbl tit centruj" style="width:8%;">(.*?)</div>').findall(subset)
        release = re.compile('<div class="tp tbl tit centruj" style="width:20%;">(.*?)</div>').findall(subset)
        rating  = re.compile('<div class="tp tbl tit centruj" style="width:12%;">(.*?)</div>',re.DOTALL).findall(subset)


        href_title =re.compile('<a href="(.*?)">([^<].*?)</a>').findall(subset)
        title2 = re.compile('<div class="h6">(.*?)</div>').findall(subset)
        if href_title:
            title = href_title[0][1].strip()
            if count:
                title = '%s.%s'%(count[0].strip(),title)
            if title2:
                title += ' [COLOR lightblue]%s[/COLOR]'%title2[0].strip()
            if release:
                title += ' %s'%(release[0].strip())
                
            href = urlparse.urljoin(BASEURL,href_title[0][0])
            one = {'url'   : href,
                'title'  : unicodePLchar(title),
                'img'    :  '',
                'rating' : rating[0].strip() if rating else '',
                }
            out.append(one)
    return out    

url='http://on-anime.pl/anime/Akame-ga-Kill!/odcinki-24'
url='http://on-anime.pl/anime/Berserk-(2016)/odcinki-1'
def getLinks(url):
    content = getUrl(url)

    ids = [(a.start(), a.end()) for a in re.finditer('<div class="tw">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        href_title = re.search('<a href="(.*?)">(.*?)</a>',subset)
        quality = re.compile('<span style="color:#.*;">(.*?)</span> ').findall(subset)
    
        dodany = re.compile('<div class="tp tbl tit centruj">([^<].*?)</div>',re.DOTALL).findall(subset)
        dodany = dodany[-1].strip() if dodany else ''
        
        if href_title:
            href = urlparse.urljoin(BASEURL,href_title.group(1))
            title = href_title.group(2)
            if quality:
                title += ' [COLOR blue]%s[/COLOR]'%(quality[0].strip()) 
            if dodany and '<' not in dodany:
                title += ' | %s'%(dodany) 
            one = {'url'   : href,
                  'title'  : unicodePLchar(title),
                }
            out.append(one)
    return out     

# url='http://on-anime.pl/anime/Akame-ga-Kill!/online-24#5234'
# url='http://on-anime.pl/anime/Berserk-(2016)/online-1#10848'
def getVideoUrl(url):
    id =re.search('#(\d+)',url)
    if id:
        content = getUrl('http://ani.center/moduly/anime/ajax.online.php?id=%s'%id.group(1))
        src = re.compile('src="(.*?)"').findall(content)
        if src:
            href = src[0].replace('rutube.ru/embed/','rutube.ru/play/embed/')
            if 'video.sibnet.ru' in href:
                ur = 'http:' + href if href.startswith('//') else href
                content = getUrl(ur)
                file = re.search('\'file\' : \'(.*?)\',',content)
                if file:
                    href='http://video.sibnet.ru'+file.group(1)
            return href
    return ''
    
            
def get_katalog_anime(dane='',strona='1',sortuj='9'):
    url='http://on-anime.pl/moduly/anime/ajax.szukaj.php'
    data='dane=%s&strona=%s&sortuj=%s&widok=0&strony=0'%(dane,strona,sortuj)
    content = getUrl(url,data)

    ids = [(a.start(), a.end()) for a in re.finditer('<div class="tab">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        obrazek = re.search('obrazek\([\'"](.*?)[\'"]\)',subset)
        background = re.search('background:url\([\'"](.*?)[\'"]\)',subset)
        href_title = re.search('<a href="(.*?)">(.*?)</a>',subset)
        year = re.search('<h5 class="tl" style="vertical-align:top;">(.*?)</h5>',subset)
        genre = re.compile('class="przycisk">(.*?)</a>').findall(subset)
        plot = re.compile('<h6 style="height:26px; overflow:hidden;">(.*?)</h6>').findall(subset)
        rating = re.search('<h5>Ocena:</h5> <h3 class="b">(.*?)</h3>',subset)
        
        if href_title:
            title = href_title.group(2).strip()
            href = urlparse.urljoin(BASEURL,href_title.group(1))
            one = {'url'   : href,
                'title'  : unicodePLchar(title),
                'plot'   : unicodePLchar(plot[0]) if plot else '',
                'img'    : urlparse.urljoin(BASEURL,obrazek.group(1)) if obrazek else '',
                'background' : urlparse.urljoin(BASEURL,background.group(1)) if background else '',
                'rating' : rating.group(1) if rating else '',
                'genre' : unicodePLchar(','.join(genre)) if genre else '',
                'year'   : year.group(1) if year else '',
                    }
            out.append(one)
            
    nextPage='%d'%(int(strona)+1) if out else False
    prevPage='%d'%(int(strona)+1) if int(strona)>1 else False
    
    return out,(prevPage,nextPage)

# url='http://on-anime.pl/sezon'
# items,pagination = get_seasons(url)
# items,pagination = get_seasons(pagination[0].get('url'))
def get_seasons(url='http://on-anime.pl/sezon/'):
    content = getUrl(url)
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="tl obrazek" style=', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        
        img = re.search('background:url\([\'"](.*?)[\'"]\)',subset)
        href_title = re.search('<a href="(.*?)">([^<].*?)</a>',subset)
        plot = re.compile('<br />([^<].*?)</div>',re.DOTALL).findall(subset)
        premiera = re.compile('<span class="b">Premiera:</span>(.*?)</div>',re.DOTALL).findall(subset)
        
        genre = re.compile('style="font-weight:normal;">(.*?)</a>').findall(subset)

        if href_title:
            title = href_title.group(2).strip()
            if premiera:
               title += ' [COLOR blue]%s[/COLOR]'%(premiera[0].strip())
            href = urlparse.urljoin(BASEURL,href_title.group(1))
            one = {'url'   : href,
                'title'  : unicodePLchar(title),
                'plot'   : unicodePLchar(plot[0]) if plot else '',
                'img' : urlparse.urljoin(BASEURL,img.group(1)) if img else '',
                'genre' : unicodePLchar(','.join(genre)) if genre else '',
            }
            out.append(one)

    pagination=[]
    prev=re.compile('<div class="tp tit" style="width:250px;">&laquo; <a href="(.*?)">(.*?)</a></div>').findall(content)
    if prev:
        pagination.append({'url':urlparse.urljoin(BASEURL,prev[0][0]),'title'  : unicodePLchar(prev[0][1].strip())})
    next=re.compile('<div class="tp tit prawo" style="width:250px;"><a href="(.*?)">(.*?)&raquo;</a></div>').findall(content)
    if next:
        pagination.append({'url':urlparse.urljoin(BASEURL,next[0][0]),'title'  : unicodePLchar(next[0][1].strip())})
    
    return out,pagination
    
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