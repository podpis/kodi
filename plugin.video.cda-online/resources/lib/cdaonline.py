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
                'title'  : title.group(1),
                'plot'   : plot.group(1) if plot else '',
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
            link = _getOrginalURL(href.group(1).replace('http://cda-online.pl?',''),host)
            
            if link:
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
                'title' : t.strip()}
            out.append(one)
    return out

if __name__=="main":
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
    url='http://go.cda-online.pl/Juv6D'
    links = getVideoLinks(url)
    _getOrginalURL('http://go.cda-online.pl/Juv6D')