# -*- coding: utf-8 -*-

import urllib2,urllib
import os,re
import urlparse
import cfcookie,cookielib

BASEURL='https://www.iwatchonline.lol'
TIMEOUT = 10
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

COOKIEFILE=r''

# def _getUrl(url,data=None,header={},useCookies=True,saveCookie=False):
#     if COOKIEFILE and os.path.isfile(COOKIEFILE) and useCookies:
#         cj = cookielib.LWPCookieJar()
#         cj.load(COOKIEFILE)
#         opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#         urllib2.install_opener(opener)
#     
#     req = urllib2.Request(url,data)
#     if not header:
#         header = {'User-Agent':UA}
#     req = urllib2.Request(url,data,headers=header)
#     try:
#         response = urllib2.urlopen(req,timeout=TIMEOUT)
#         link =  response.read()
#         response.close()
#         if COOKIEFILE and os.path.isfile(COOKIEFILE) and saveCookie and useCookies:
#              cj.save(COOKIEFILE, ignore_discard = True) 
#     except urllib2.HTTPError as e:
#         #link = e.read()
#         link = ''
#     return link

def _getUrl(url,data=None,cookies=None):
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
    return content

def cf_setCookies(link,cfile=COOKIEFILE):
    cj = cookielib.LWPCookieJar()
    cookieJar = cfcookie.createCookie(BASEURL,cj,UA)
    dataPath=os.path.dirname(cfile)
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)
    else:
        print 'PATH OK'
    if cookieJar:
        cookieJar.save(cfile, ignore_discard = True) 
    return cj

def getLanguages():
    content = getUrl(BASEURL+'/movies')
    langs=re.compile('<a class="spf-link" href="\?language=(.*)">').findall(content)
    lang = langs.remove('Polish')
    langs.insert(0,'Polish')
    langs.insert(0,'[B]All[/B]')
    return langs

def getGenre():
    content = getUrl(BASEURL+'/movies')
    genre=re.compile('<a class="spf-link" href="\?gener=(.*?)">(.*?)</a>',re.DOTALL).findall(content)
    return genre

#url='https://www.iwatchonline.lol/movies?'
#url='https://www.iwatchonline.lol/movies?&amp;p=25'
#url='https://www.iwatchonline.lol/movies?sort=metacritc'
def scanMainpage(url):
    out=[]
    content = getUrl(url.replace('&amp;','&'))
    
    idx = content.find('<ul class="thumbnails">')
    subsets = re.compile('<li class="">(.*?)</li>',re.DOTALL).findall(content[idx:-1])
    #subset= subsets[0]
    for subset in subsets:
        
        href = re.compile('<a href="(.*?)"').findall(subset)
        img = re.compile('<img class="thumbimg" src="(.*?)"').findall(subset)
        title = re.compile('<div class="title hide">(.*?)<',re.DOTALL).findall(subset)
        year = None
        if title:
            year = re.compile('(\d{4})').findall(title[0].strip())
        
        rating = re.compile('<div class="star" data-rating="(.*?)">').findall(subset)
        plot = re.compile('<div class="shortdescription description hide">(.*?)<',re.DOTALL).findall(subset)
        
        
        if href and title and img:
            one = {'url'   : href[0],
                'title'  : unicodePLchar(title[0].strip()),
                'plot'   : unicodePLchar(plot[0].strip()) if plot else '',
                'img'    : img[0],
                'rating' : rating[0] if rating else '',
                'year'   : year[-1] if year else '',
                'code'  : '',
                    }
            out.append(one)
    
    nextPage = re.compile('<li class="next pagea"><a href="(.*?)">').findall(content)
    nextPage = nextPage[0] if nextPage and out else False
    
    prevPage = re.compile('<li class="prev pagea"><a href="(.*?)">').findall(content)
    prevPage = prevPage[0] if prevPage and out else False
            
    return (out, (prevPage,nextPage))     

#url='https://www.iwatchonline.lol/tv-shows/28131-house-of-cards'
def scanTVShows(url):
    out=[]
    content = getUrl(url.replace('&amp;','&'))
    
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="accordion-group">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]  
        
        seasonNumber = re.compile('data-toggle="collapse" data-parent="#accordion2" href="#season(\d+)">').findall(subset)
        seasonNumber = seasonNumber[0] if seasonNumber else '0'
        
        episodes = re.compile('<tr class="unwatched ">(.*?)</tr>',re.DOTALL).findall(subset)
        episode = episodes[0]
        for episode in episodes:
            TD = re.compile('<td[>]*(.*?)</td>',re.DOTALL).findall(episode)
            if len(TD)==5:
                href = re.compile('href="(.*?)"').findall(TD[0])
                episodeNumber = re.compile('</i>.*?(\d)[ ]*</a>').findall(TD[0])
                episodeNumber = episodeNumber[0] if episodeNumber else '0'
                title = TD[1].strip()
                rating = re.compile('data-rating="(\d+)"').findall(TD[2])
                times = TD[3].strip()
                linksNo = re.compile('href="#">(.*?)<').findall(TD[4])
                if href and title :
                    one = {'url'   : href[0],
                        'title'  : unicodePLchar('S%02dE%02d [B]%s[/B] %s' %(int(seasonNumber),int(episodeNumber), title, times)),
                        'plot'   : '',
                        'img'    : '',
                        'rating' : rating[0] if rating else '',
                        'year'   : '',
                        'code'  : linksNo[0] if linksNo else '',
                            }
                    out.append(one)
    return out

def search(data='searchquery=india&searchin=m'):
    out=[]
    url=BASEURL+'/search'
    #data='searchquery=%s&searchin=%s'%(urllib.quote_plus(searchquery),searchin)
    content= getUrl(url,data=data)
    
    firstTable = re.compile('<table class="table table-striped table-hover">(.*?)</table>',re.DOTALL).findall(content)
    firstTable = firstTable[0] if firstTable else ''
    
    imgs = re.compile('<img src="(.*?)" alt="">').findall(firstTable)
    titles =re.compile('<a href="(.*?)">(.*?)</a>').findall(firstTable)
    
    for img,title in zip(imgs,titles):
        one = {'url'   : title[0],
            'title'  : unicodePLchar(title[1]),
            'plot'   : '',
            'img'    : img,
            'rating' : '',
            'year'   : '',
            'code'  : '',
                }
        out.append(one)
    return out
    
# url='https://www.iwatchonline.lol/movie/57667-kindergarten-cop-2-2016'
url='https://www.iwatchonline.lol/movie/55880-the-huntsman-winter-s-war-2016'
url='https://www.iwatchonline.lol/episode/62514-totally-spies-totally-dunzo-2--s05e26'
def getVideoLinks(url):
    outL=[]
    content = getUrl(url)
    ids = [(a.start(), a.end()) for a in re.finditer('<a class="spf-link KAKA"', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        
        host = re.compile('alt="" />(.*?)<',re.DOTALL).findall(subset)
        href = re.compile('href="(.*?)" target="_blank"').findall(subset)
        TD  = [x.strip() for x in re.compile('<td>(.*?)</td>',re.DOTALL).findall(subset) if x.strip()]
        lang = re.compile('rel="tooltip" data-original-title="(.*?)">').findall(TD[0]) if len(TD)>1 else ''
        lang = lang[0] if lang else ''
        age =  TD[1] if len(TD)>2 else ''
        if '>' in age and '<' in age:
            age = re.compile('>(.*?)<').findall(age)[0]
        quality  =  TD[2] if len(TD)>3 else ''
        
        if host and href:
            host = host[0].strip()
            href = href[0]
            msg = '%s [%s]: %s, %s'%(lang,host,age,quality)
            
            one = {'href':href,'host':host,'lang':lang,'age':age,'quality':quality,'msg':msg}
            outL.append(one)
    return outL        
# outL=getVideoLinks(url)    

# url='http://www.iwatchonline.lol/stream/6500872'
# url='http://www.iwatchonline.lol/stream/6455764'
def getLinkUrl(url):
    link=''
    content = getUrl(url)
    iframes = re.compile('<iframe(.*?)</iframe>',re.DOTALL).findall(content)
    #iframe = iframes[0]
    for iframe in iframes:
        href = re.compile('src="(.*?)"').findall(iframe)
        if href:
            link = href[0]
            if 'greevid.com' in link:
                link = get_greevid(link)
            if link:
                return link
    return link
    
def get_greevid(url):
    content = getUrl(url)
    iframes = re.compile('<iframe(.*?)</iframe>',re.DOTALL).findall(content)
    if iframes:
        href = re.compile('src="(.*?)"').findall(iframes[0])
        if href:
            href = 'http'+href[0].split('http')[-1]
            return href
    return ''                
    
def unicodePLchar(txt):
    if type(txt) is not str:
        txt=txt.encode('utf-8')
        
    txt = txt.replace('#038;','')
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