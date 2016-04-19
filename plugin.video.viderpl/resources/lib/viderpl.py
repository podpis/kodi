# -*- coding: utf-8 -*-
"""
Created on Thu Apr -18 2016

@author: ramicspa
"""

import urllib2,urllib
import re
import json as json


BASEURL='http://vider.pl'
TIMEOUT = 5

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


def _get_overflowtype(overflow):
    out=[]
    for item in overflow:
        href = re.compile('<a href="(.*?)"><span').findall(item)
        img = re.compile('<img src="(.*?)">').findall(item)
        title = re.compile('<span class="txt_md">(.*?)</span>').findall(item)
        duration = re.compile('<i class="fa fa-clock-o"></i>(.*?)</span>',).findall(item)
        if href and title:
            one = {'href'   : BASEURL+href[0],
                   'title' : unicodePLchar(title[0]).strip() if title else '',
                   'img' : img[0],
                   'duration': duration[0] if duration else ''
                   }
            out.append(one)
    return out
                
def _get_clearfixtype(clearfix):
    out=[]   
    #item=clearfix[0]
    for item in clearfix:
        href_title = re.compile('<p class="title"><a href="(.*?)" class=".*?">(.*?)<').findall(item)
        img = re.compile('<img src="(.*?)" ').findall(item)
        meta = re.compile('<p class="meta">(.*?)</p>').findall(item)
        duration = re.compile('<div class="duration">(.*?)</div>').findall(item)
        plot = re.compile('<p class="description">(.*?)</p>').findall(item)
        if href_title:
            folder =''
            if meta:
                txt = ' '.join(re.compile('>(.*?)<').findall(meta[0])).strip()
               
                match1 = re.compile('Katalogów: \d+ / Plików: \d+').findall(txt)
                match2 = True if 'Filmy:' in txt and 'Rozmiar:' in txt else False
                if match1:
                    folder = match1[0]
                elif match2:
                    folder = txt.replace('  ',' ')
            
            image=''
            if img:
                image = img[0]
                if not 'http' in image:
                   image =  BASEURL + image

            one = {'href'  : BASEURL+href_title[0][0],
                   'title' : unicodePLchar(href_title[0][1]).strip() if href_title else '',
                   'img' : image,
                   'folder': folder,
                   'duration': duration[0] if duration else '',
                   'plot' :unicodePLchar(plot[0]).strip() if plot else '',
                   }
            if one.get('folder'):
                one['title'] = '[COLOR blue]%s[/COLOR] - [COLOR green]%s[/COLOR]' %(one['title'], one.get('folder'))
            out.append(one)
    return out
            
url='http://vider.pl/ranking/month'
url='http://vider.pl/ziomek72'
url='http://vider.pl/Queen-1/poczekalnia+dn5mvs'
url='http://vider.pl/search/all/2015/1'
url='http://vider.pl/search/all/tangled%20ever%20after'
def scanUser(url):
    # url='http://vider.pl/Queen-1/'
    # url='http://vider.pl/'
    #url='http://vider.pl/Queen-1/queen-1+dvn5m'
    out=[]
    my={}
    print '******************scanUser', url
    content=getUrl(url)
    
    
    #nextPage = re.compile('<span class="link2 pointer search-next-page-click" data-href="(.*?)">').findall(content)
    #prevPage = re.compile('<span class="link2 pointer search-previous-page-click" data-href="(.*?)">').findall(content)
    
    overflow = re.compile('<div class="overflow">(.*?)</div>',re.DOTALL).findall(content)
    clearfix = re.compile('<li class="clearfix w-100-p">(.*?)</li>',re.DOTALL).findall(content)

    if overflow:
        out = _get_overflowtype(overflow)    
    
        fileTreeLink = re.compile('<div class="CssTreeValue CssTreeValueMain"><a href="(.*?)" title="(.*?)" class="fileTreeLink">').findall(content)
        if fileTreeLink:
            my = {'href':BASEURL+fileTreeLink[0][0],'title':'[COLOR blue][Kolekcje video][/COLOR]','img':'','folder':'yes'}
            out.insert(0,my)

    elif clearfix:
        out = _get_clearfixtype(clearfix)
        
    return out
    
def search(txt='tangled ever after'):
    out=[]
    url='http://vider.pl/search/get'
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
            one = {'href'  : 'http://vider.pl/embed/video/'+item.get('id_url',''),
                   'title' : item.get('name',''),
                   'img' : '',
                   'folder': '',
                   'duration': item.get('duration',''),
                   'plot' : '',
                   }
            if one.get('folder'):
                one['title'] = '[COLOR blue]%s[/COLOR] - [COLOR green]%s[/COLOR]' %(one['title'], one.get('folder'))
            out.append(one)
    return out
                   
    
# def scanMainpage(url):
#     content = getUrl(url)
#     out=[]
#     items = re.compile('<li class="ajax_block_product bordercolor">(.*?)</li>',re.DOTALL).findall(content)
#     for item in items:
# 
#         href = re.compile('<a href="(.*?)" class="product_img_link" title="(.*?)">',re.DOTALL).findall(item)
#         img = re.compile('<img .* src="(.*?)"',re.DOTALL).findall(item)
#         title = re.compile('<span class="availability bordercolor">(.*?)</span>',re.DOTALL).findall(item)
#         plot = re.compile('<a class="product_descr" href="(.*?)" title="(.*?)</a>',re.DOTALL).findall(item)
#         quality = re.compile('<font color="black"><b>(.*?)</b></font></span>',re.DOTALL).findall(item)
#     
#         genre =  re.compile('<span class="discount">(.*?)</span>',re.DOTALL).findall(item)
#         audio = re.compile('<b style="color:#FFF">(.*?)</b>').findall(item)
#         
#         if href and title:
#             href_tmp =  href[0][0]
#             if href_tmp.startswith('/'):
#                 href_tmp = BASEURL + href_tmp
#             img = img[0] if img else ''
#             if img.startswith('//'):
#                 img = 'http:'+img
#             one = {'href'   : href_tmp,
#                 'title2'  : unicodePLchar(href[0][1]).strip(),
#                 'title' : unicodePLchar(title[0]).strip() if title else '',
#                 'plot'   : unicodePLchar(plot[0][1]) if plot else '',
#                 'img'    : img,
#                 'audio' : audio[-1] if audio else '',
#                 'code'  : quality[-1] if quality else '',
#                     }
#             if one.get('title2'):
#                 one['title'] += '/%s' % one.get('title2')
#             if one.get('audio'):
#                 one['title'] +=' [COLOR green]%s[/COLOR]' % one.get('audio')            
#             out.append(one)
# 
#     # pagination
#     prevPage = re.compile('<a class="ajax_add_to_cart_button exclusive" href="(.*?)">Poprzednia</a>').findall(content)
#     nextPage = re.compile('</a><a class="ajax_add_to_cart_button exclusive" href="(.*?)">Następna</a></div>').findall(content)
#     if prevPage:
#         prevPage = BASEURL + prevPage[0]
#     if nextPage:
#         nextPage = BASEURL + nextPage[0]
#     return (out, (prevPage,nextPage))


    

#url = 'http://vider.pl/Queen-1/barbie_-super-ksiezniczki-2015-dubbing-pl+fnxxens'
#url = 'http://vider.pl/embed/video/nxxens'
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
    content = getUrl(url)
    data = re.compile('data-video-url="(.*?)"').findall(content)
    if data:
        video_link=data[0]+'|Referer:%s'%url + ' swfUrl=http://vider.pl/static/player/v58/player.swf'
    return video_link
    

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