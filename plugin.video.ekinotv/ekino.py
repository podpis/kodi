# -*- coding: utf-8 -*-

import sys,os,re
import urllib,urllib2
import urlparse


BASEURL='http://ekino-tv.pl'
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
    

def skanuj_filmy(kat='',wer='', page='1', url='http://ekino-tv.pl/movie/cat/kategoria[35]+'):
    if kat or wer:
        my_url = 'http://ekino-tv.pl/movie/cat/kategoria[%s]+wersja[%s]+strona[%s]+' %(kat,wer,page)
    else:
        my_url = url
    print '#'*10
    print my_url
    content  = getUrl(my_url)
    return _getData(content)
    
def _getData(content):
    img = re.compile('<img src="(/static/thumb/.*.jpg)" alt=').findall(content)
    title = re.compile('<div class="title">[\s]*<a href="(.*?)">(.*?)</a><br>').findall(content)
    des = re.compile('<div class="movieDesc">[\s\n]*(.*?)</div>').findall(content)
    rok = re.compile('<p class="cates">(.*) \|').findall(content)
    categorie = re.compile('<p class="cates">(.*) \| (<a href="/movie/cat/kategoria\[\d+\]">.*</a>[,]*)*</p>').findall(content)

    foundItems=min(len(img),len(title),len(des),len(categorie))
    res=[]
    for i in range(foundItems):
        out={}
        #cat = dict(zip(range(len(_Links)),_Links))
        out['href'] = title[i][0]
        out['title'] = unicodePLchar(title[i][1].strip('\n '))
        out['year'] = categorie[i][0]
        out['genre'] = ''.join(re.compile('>(.*?)<').findall(categorie[i][1]))
        out['code'] = 'HD' if 'HD' in out['genre'] else ''
        out['plot'] = unicodePLchar(des[i].strip('\n '))
        out['img'] = BASEURL+img[i].replace('/thumb/','/normal/')
        res.append(out)
    return res
    

# url='/movie/show/piraci-z-karaiboacutew-na-nieznanych-wodach-pirates-of-the-caribbean-on-stranger-tides-2011-lektor/3132'
# url='/movie/show/igrzyska-smierci-kosoglos-czesc-2-lektor-pl-the-hunger-games-mockingjay-part-2-2015-lektor/13000'
def get_sources(url='/movie/show/partyzant-napisy-pl-partisan-2015-napisy/7909'):
    content  = getUrl(BASEURL+url)
    iframes = re.compile('ShowPlayer\(\'(.*?)\',\'.*?\'\)').findall(content)
    _Lables=[]
    _Links=[]
    one=iframes[0]
    for one in iframes:
        print one
        if 'hosting=vshare' in one:
            one='http://vshare.io/v/%s/width-640/height-400/'  % (one.split('=')[-1])
        if one.startswith('http'):
            _Links.append(one)
            _Lables.append(one.split('/')[2])
    return (_Lables,_Links)



def _old_get_sources(url='/movie/show/partyzant-napisy-pl-partisan-2015-napisy/7909'):
    content  = getUrl(BASEURL+url)
    iframes = re.compile('<iframe(.*)></iframe>\n', re.DOTALL).findall(content)
    _Lables=[]
    _Links=[]
    for f in iframes:
        links = re.compile('src="(.*?)"', re.DOTALL).findall(content)
        for one in links:
            if 'hosting=vshare' in one:
                one='http://vshare.io/v/%s/width-640/height-400/'  % (one.split('=')[-1])
            # if 'openload.co/embed' in one:
            #     content=getUrl(one)
            #     kod = re.compile('var suburl = "(.*?)"', re.DOTALL).findall(content)
            #     one = one.replace('/embed/','/stream/')+'~'+kod[0].split('/')[-1][:-1]+'?mime=true'
            #     print one
            if one.startswith('http'):
                _Links.append(one)
                _Lables.append(one.split('/')[2])
    return (_Lables,_Links)
       
def getCategories(url='http://ekino-tv.pl/movie/cat/'):
    content  = getUrl(url)   
    cats = re.compile('<li data-id="(\d+)">[\s\n]+<a href="/movie/cat/kategoria\[\d+\]">(.*?)</a>[\s\n]*</li>').findall(content)
    number = [x[0] for x in cats]
    opis = [x[1] for x in cats]
    return (opis,number)
    
def szukaj(what='Piraci'):
    postdata = {'search_field': what}
    content = getUrl('http://ekino-tv.pl/search/', postdata)
    return _getData(content)

# cat=getCategories()
# s=szukaj('dom')
#s=szukaj('Piraci z Karaibów')
# len(s)
#f=skanuj_filmy(kat='35',wer='',url='')
# (_Lables,_Links)=get_sources(f[0]['href'])

