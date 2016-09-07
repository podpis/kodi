# -*- coding: utf-8 -*-
"""

@author: ramicspa
"""

import urllib2,urllib
import re
import json as json
import htmlentitydefs

BASEURL='http://freedisc.pl'
TIMEOUT = 30

def getUrl(url,data=None,headers={},cookies=None):
    if headers:
        my_header=headers
    else:
        my_header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'}
    req = urllib2.Request(url,data,my_header)
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link =  response.read()
        response.close()
    except:
        link=''
    return link
 
def _get_userranking(userranking):
    out=[]
    for item in userranking:
        href = re.compile(' href="(.*?)">').findall(item)
        img = re.compile('<img src=["\'](.*?)["\'] alt=["\'](.*?)["\']').findall(item)
        if href and img:
            one = {'href'   : BASEURL+href[0],
                   'title' : unicodePLchar(img[0][1]).strip(),
                   'img' : img[0][0],
                   'folder': True,
                }
            out.append(one)
    return out            


def _get_overflowtype(overflow):
    out=[]
    for item in overflow:
        href = re.compile('href=["\'](.*?)["\']').findall(item)
        img = re.compile('<img src=["\'](.*?)["\']').findall(item)
        title = re.compile('<a title=["\'](.*?)["\']').findall(item)

        if href and title:
            one = {'href'   : BASEURL+href[0],
                   'title' : unicodePLchar(title[0]).strip(),
                   'img' : img[0],
                   'folder': False,
                   }
            out.append(one)
    return out
            
def _get_dir_item(dir_item):
    out=[]
    item=dir_item[0]
    for item in dir_item:
        href = re.compile('<a href=["\'](.*?)["\']').findall(item)
        title = re.compile('<a href=[^>]+>(.*?)<').findall(item)
        id = re.compile('<div class=["\']data["\'] id=["\'](.*?)["\']>').findall(item)
        img = re.compile('src=["\'](.*?)["\']').findall(item)
        info = re.compile('<div class=["\']info["\'][^>]*>(.*?)<').findall(item)

        
        if href and title:
            if id:
                url='http://freedisc.pl/embed/video/'+id[0].split('-')[-1]
                folder = False
            else:
                url = BASEURL + '/' if not href[0].startswith('/') else BASEURL
                url = url + href[0]
                folder = True if re.search(',d-\d+',url) else False
            
            title = unicodePLchar(title[0])
            if info:
                title +=' [COLOR lightblue]%s[/COLOR]'%(info[0])
            img = img[0] if img else ''
            if img.startswith('/'):
                img = BASEURL + img
           
            one = {'href'   : url,
                   'title' : unicodePLchar(title.strip()),
                   'img' : img,
                   'folder': folder,
                   }
            out.append(one)
    return out
                        

def _get_content_element(content_element):
    out=[]   
    #item=content_element[0]
    for item in content_element:
       
        img = re.compile('src=["\'](.*?)["\']').findall(item)
        href = re.compile('href=["\'](.*?)["\']').findall(item)
        title = re.compile('title=["\'](.*?)["\']').findall(item)
        info = re.compile('<div class=["\']size["\'][^>]*>(.*?)<').findall(item)
        
        if href and title:
            id = re.search(',f-(\d+)',href[0])
            if id:
                url='http://freedisc.pl/embed/video/'+id.group(1)
                folder = False
            else:
                url = BASEURL + '/' if not href[0].startswith('/') else BASEURL
                url = url + href[0]
                folder = True if re.search(',d-\d+',url) else False
            
            title = unicodePLchar(title[0])
            if info:
                title +=' [COLOR lightblue]%s[/COLOR]'%(info[0])
            img = img[0] if img else ''
            if img.startswith('/'):
                img = BASEURL + img
           
            one = {'href'   : url,
                   'title' : unicodePLchar(title.strip()),
                   'img' : img,
                   'folder': folder,
                   }
            out.append(one)
    return out            
            
            
# url='http://freedisc.pl/ranking/month'
# url='http://freedisc.pl/Viola_up'
# url='http://freedisc.pl/Viola_up,d-318621,Viola_ups'
# url='http://freedisc.pl/Viola_up,d-1419318,r'
# url='http://freedisc.pl/Viola_up/favourites'
# url ='http://freedisc.pl/seriale-online/najnowsze'
def scanUser(url):
    # url='http://vider.pl/Queen-1/'
    # url='http://vider.pl/'
    #url='http://vider.pl/Queen-1/queen-1+dvn5m'
    out=[]
    print '******************scanUser', url
    content=getUrl(url)
    
    #nextPage = re.compile('<span class="link2 pointer search-next-page-click" data-href="(.*?)">').findall(content)
    #prevPage = re.compile('<span class="link2 pointer search-previous-page-click" data-href="(.*?)">').findall(content)
    
    userranking = re.compile('<div class="friends-item hover padding-5 overflow-a">(.*?)</div></div></div>',re.DOTALL).findall(content)
    overflow = re.compile('<div class="w-100-p overflow-a hover margin-t-minus-1" style="border-bottom: 1px solid #dfe0df;border-top: 1px solid #dfe0df;">(.*?)</div></div>',re.DOTALL).findall(content)
    dir_item = re.compile('<div class="dir-item">(.*?</div>)</div>',re.DOTALL).findall(content)
    content_element = re.compile('<div class=["\']content-element padding-5[^"\']+["\']>(.*?</div>)</div>',re.DOTALL).findall(content)
    
    
    if userranking:
        out = _get_userranking(userranking)
    elif overflow:
        out = _get_overflowtype(overflow)    
    
        fileTreeLink = re.compile('<a class=["\']menu-system["\'] href=["\'](.*?)["\']>').findall(content)
        if fileTreeLink:
            my = {'href':BASEURL+fileTreeLink[0],'title':'[COLOR blue][System Plików][/COLOR]','img':'','folder':True}
            out.insert(0,my)
        fav = re.compile('<a class=["\']menu-fav["\'] href=["\'](.*?)["\']>').findall(content)
        if fav:            
            my = {'href':BASEURL+fav[0],'title':'[COLOR blue][Ulubione][/COLOR]','img':'','folder':True}
            out.insert(1,my)

    elif dir_item:
        out = _get_dir_item(dir_item)
    elif content_element:
        out = _get_content_element(content_element)
        
    return out
    
def search(txt='tangled ever after'):
    out=[]
    url='http://freedisc.pl/search/get'
    payload = {"search_phrase":txt,"search_type":"all","search_saved":0,"pages":1,"limit":150}

    headers= {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest'}

    content=getUrl(url,data=json.dumps(payload),headers=headers)
    if content:
        data=json.loads(content)
        print data.keys()
        resp_data_data = data.get('response',{}).get('data_files',{}).get('data',[])
        for item in resp_data_data:
            #item = resp_data_data[0]
            one = {'href'  : 'http://freedisc.pl/embed/video/'+item.get('id',''),
                   'title' : unicodePLchar(item.get('name','').encode('utf-8')).replace('',''),
                   'img' : '',
                   'folder': '',
                   'duration': item.get('duration',''),
                   'plot' : '',
                   }
            if one.get('folder'):
                one['title'] = '[COLOR blue]%s[/COLOR] - [COLOR green]%s[/COLOR]' %(one['title'], one.get('folder'))
            out.append(one)
    return out
                   
    
#url = 'http://freedisc.pl/Viola_up,f-486419,rango-2011-pldubb-dvdrip-xvid-firma-avi'
#url = 'http://freedisc.pl/embed/video/486419'
#url = 'http://freedisc.pl/embed/video/517258'
BRAMKA = 'http://www.bramka.proxy.net.pl/index.php?q='
def getVideoUrls(url):
    """    
    returns 
        - ulr http://....
    """        
    #print url
    video_link=''
    if not '/embed/' in url:
        content = getUrl(url)
        embed = re.compile('<div class="video-frame "><iframe src="(/embed/video/.*?)"').findall(content)
        if embed:
            url = BASEURL+embed[0]

    content = getUrl(BRAMKA+urllib.quote_plus(url)+'&hl=2e7')
    data = re.compile('<link rel="video_src" type="" href="(.*)" />').findall(content)

    if data:
        data = urllib.unquote(data[0].replace(BRAMKA,''))
        file = re.search('file=(http://.*)',data)
        if file:
            video_link=file.group(1)+'|Referer='+url +' swfUrl=http://http://freedisc.pl/static/player/v58/player.swf'
    return video_link
    
def html_entity_decode_char(m):
    ent = m.group(1)
    if ent.startswith('x'):
        return unichr(int(ent[1:],16))
    try:
        return unichr(int(ent))
    except Exception, exception:
        if ent in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[ent])
        else:
            return ent

def html_entity_decode(string):
    string = string.decode('UTF-8')
    s = re.compile("&#?(\w+?);").sub(html_entity_decode_char, string)
    return s.encode('UTF-8')    

def unicodePLchar(txt):
    txt = html_entity_decode(txt)
    #txt = txt.decode("utf-8").replace(u"\u2654", "").encode("utf-8")
    txt = txt.replace('#038;','')
    txt = txt.replace('&lt;br/&gt;',' ')
    txt = txt.replace('&#34;','"')
    txt = txt.replace('&#39;','\'').replace('&#039;','\'')
    txt = txt.replace('&#8221;','"')
    txt = txt.replace('&#8222;','"')
    txt = txt.replace('&#8217;','\'')
    txt = txt.replace('&#8211;','-').replace('&ndash;','-')
    txt = txt.replace('&quot;','"').replace('&amp;quot;','"')
    #txt = txt.replace('&oacute;','ó').replace('&Oacute;','Ó')
    #txt = txt.replace('&amp;oacute;','ó').replace('&amp;Oacute;','Ó')
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