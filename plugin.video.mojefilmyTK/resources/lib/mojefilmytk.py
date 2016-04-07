# -*- coding: utf-8 -*-
"""
Created on Thu Apr -6 2016

@author: ramicspa
"""

import urllib2,urllib
import re


BASEURL='http://moje-filmy.tk'
TIMEOUT = 5

def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link =  response.read()
        response.close()
    except:
        link=''
    return link

# url='http://moje-filmy.tk/filmy/all'
# url='http://moje-filmy.tk/filmy/strona/2'
# (out, (prevPage,nextPage)) = scanMainpage(url)
def scanMainpage(url):
    content = getUrl(url)
    out=[]
    items = re.compile('<li class="ajax_block_product bordercolor">(.*?)</li>',re.DOTALL).findall(content)
    for item in items:

        href = re.compile('<a href="(.*?)" class="product_img_link" title="(.*?)">',re.DOTALL).findall(item)
        img = re.compile('<img .* src="(.*?)"',re.DOTALL).findall(item)
        title = re.compile('<span class="availability bordercolor">(.*?)</span>',re.DOTALL).findall(item)
        plot = re.compile('<a class="product_descr" href="(.*?)" title="(.*?)</a>',re.DOTALL).findall(item)
        quality = re.compile('<font color="black"><b>(.*?)</b></font></span>',re.DOTALL).findall(item)
    
        genre =  re.compile('<span class="discount">(.*?)</span>',re.DOTALL).findall(item)
        audio = re.compile('<b style="color:#FFF">(.*?)</b>').findall(item)
        
        if href and title:
            href_tmp =  href[0][0]
            if href_tmp.startswith('/'):
                href_tmp = BASEURL + href_tmp
            img = img[0] if img else ''
            if img.startswith('//'):
                img = 'http:'+img
            one = {'href'   : href_tmp,
                'title2'  : unicodePLchar(href[0][1]).strip(),
                'title' : unicodePLchar(title[0]).strip() if title else '',
                'plot'   : unicodePLchar(plot[0][1]) if plot else '',
                'img'    : img,
                'audio' : audio[-1] if audio else '',
                'code'  : quality[-1] if quality else '',
                    }
            if one.get('title2'):
                one['title'] += '/%s' % one.get('title2')
            if one.get('audio'):
                one['title'] +=' [COLOR green]%s[/COLOR]' % one.get('audio')            
            out.append(one)

    # pagination
    prevPage = re.compile('<a class="ajax_add_to_cart_button exclusive" href="(.*?)">Poprzednia</a>').findall(content)
    nextPage = re.compile('</a><a class="ajax_add_to_cart_button exclusive" href="(.*?)">Następna</a></div>').findall(content)
    if prevPage:
        prevPage = BASEURL + prevPage[0]
    if nextPage:
        nextPage = BASEURL + nextPage[0]
    return (out, (prevPage,nextPage))


def getGatunekRok():
    content = getUrl(BASEURL)
    type = re.compile('<h4>(.*?)</div>',re.DOTALL).findall(content)
    for i,one in enumerate(type):
        if i == 0:#type
            jezyk = re.compile('<a href="(.*?)" title="">(.*?)</a>').findall(one)
        if i == 1:
            rok = re.compile('<a href="(.*?)" title="">(.*?)</a>').findall(one)
        if i == 2:
            gatunek = re.compile('<a href="(.*?)" title="">(.*?)</a>').findall(one)
    return (jezyk,rok,gatunek)
    
    


def search(s='marsja'):
    """TODO"""
    url = 'http://moje-filmy.tk/filmy/szukaj?' + 'search_query=marsj&orderby=position&orderway=desc'
    out, (prevPage,nextPage) = scanMainpage(url)
    url= 'http://moje-filmy.tk/filmy/szukaj-ajax'
    params = {'szukaj':'mars'}
    data = urllib.urlencode(  params)
    content = getUrl(url,data)
    
    

#url = 'http://moje-filmy.tk/film/projektatka-ccd5035fa1b8ca0ecff4f080a381f14d'
def getVideoUrls(url):
    """    
    returns 
        - ulr http://....
        - or list of [('720p', 'http://...'),...]
    """        
    #print url
    Cookie='|Cookie="PHPSESSID=1'
    if '/embed/' in url:
        url=url.replace('/embed/','/?v=')
    content = getUrl(url)
    src=[]
    sources = re.compile('file: "(.*?)"',re.DOTALL).findall(content)
    label = re.compile('label: "(.*?)"',re.DOTALL).findall(content)

    return zip(label,sources)
    

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