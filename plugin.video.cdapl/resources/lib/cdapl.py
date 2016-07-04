# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 18:47:43 2016

@author: ramic
"""
import cookielib
import urllib2,urllib
import re,os
import json as json

#from collections import OrderedDict

import jsunpack as jsunpack

BASEURL='http://www.cda.pl'
TIMEOUT = 10
COOKIEFILE = ''


def getUrl(url,data=None,cookies=None,Refer=False):
    if COOKIEFILE:
        cj = cookielib.LWPCookieJar()
        cj.load(COOKIEFILE)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    if Refer:
        req.add_header("Referer", url)
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link =  response.read()
        response.close()
    except:
        link=''
    return link
    
def CDA_login(USER,PASS,COOKIEFILE):
    loginData = { 'username': USER, 'password': PASS, "submit_login": "" }
    url='http://www.cda.pl/login'
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    params=urllib.urlencode(loginData)  
    status=False
    try:
        req = urllib2.Request(url, params)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
        response = urllib2.urlopen(req)
        contents = response.read()
        if 'wyloguj' in contents:   #check if logged in
            cj.save(COOKIEFILE, ignore_discard = True)    
            status=True
            #print 'Zalogowany cookie : %s' %COOKIEFILE
    except:
        pass
    return status

##  JSONUNPACK

#        result = getUrl(url)
#        result = re.compile('(eval.*?)\n').findall(result)[-1]
#        result = unpack(result)

def _get_encoded_unpaker(content):
    src =''
    #packed = re.compile('(eval.function.*?\)\))\n',re.DOTALL).findall(content)
    packedMulti = re.compile("eval(.*?)\{\}\)\)",re.DOTALL).findall(content)
    for packed in packedMulti:
        packed=re.sub('  ',' ',packed)
        packed=re.sub('\n','',packed)
        try:
            unpacked = jsunpack.unpack(packed)
        except:
            unpacked=''
        if unpacked:
            unpacked=re.sub(r'\\',r'',unpacked)
            src1 = re.compile('file:\s*[\'"](.+?)[\'"],',  re.DOTALL).search(unpacked)
            src2 = re.compile('url:\s*[\'"](.+?)[\'"],',  re.DOTALL).search(unpacked)
            if src1:
                src = src1.group(1)
            elif src2:
                src = src2.group(1)
            if src:
                break
    return src

def _get_encoded(content):
    src=''
    idx1 = content.find('|||http')
    if idx1>0:
        idx2 = content.find('.split',idx1)
        encoded =content[idx1:idx2]
        if encoded:
            #print encoded
            tmp = encoded.split('player')[0]
            tmp=re.sub(r'[|]+\w{2,3}[|]+','|',tmp,re.DOTALL)
            tmp=re.sub(r'[|]+\w{2,3}[|]+','|',tmp,re.DOTALL)
            
            
            remwords=['http','cda','pl','logo','width','height','true','static','st','mp4','false','video','static',
                    'type','swf','player','file','controlbar','ads','czas','position','duration','bottom','userAgent',
                    'match','png','navigator','id', '37', 'regions', '09', 'enabled', 'src', 'media']
            remwords=['http', 'logo', 'width', 'height', 'true', 'static', 'false', 'video', 'player', 
                'file', 'type', 'regions', 'none', 'czas', 'enabled', 'duration', 'controlbar', 'match', 'bottom',
                'center', 'position', 'userAgent', 'navigator', 'config', 'html', 'html5', 'provider', 'black',
                'horizontalAlign', 'canFireEventAPICalls', 'useV2APICalls', 'verticalAlign', 'timeslidertooltipplugin', 
                'overlays', 'backgroundColor', 'marginbottom', 'plugins', 'link', 'stretching', 'uniform', 'static1', 
                'setup', 'jwplayer', 'checkFlash', 'SmartTV', 'v001', 'creme', 'dock', 'autostart', 'idlehide', 'modes',
               'flash', 'over', 'left', 'hide', 'player5', 'image', 'KLIKNIJ', 'companions', 'restore', 'clickSign',
                'schedule', '_countdown_', 'countdown', 'region', 'else', 'controls', 'preload', 'oryginalne', 'style', 
                '620px', '387px', 'poster', 'zniknie', 'sekund', 'showAfterSeconds', 'images', 'Reklama', 'skipAd',
                 'levels', 'padding', 'opacity', 'debug', 'video3', 'close', 'smalltext', 'message', 'class', 'align',
                  'notice', 'media']

            for one in remwords:
                tmp=tmp.replace(one,'')
            
            cleanup=tmp.replace('|',' ').split()
            
            out={'server': '', 'e': '', 'file': '', 'st': ''}
            if len(cleanup)==4:
                #print 'Length OK'
                for one in cleanup:
                    if one.isdigit():
                        out['e']=one
                    elif re.match('[a-z]{2,}\d{3}',one) and len(one)<10:  
                        out['server'] = one
                    elif len(one)==22:
                        out['st'] = one
                    else:
                        out['file'] = one
                src='http://%s.cda.pl/%s.mp4?st=%s&e=%s'%(out.get('server'),out.get('file'),out.get('st'),out.get('e'))
    return src

# url='http://www.cda.pl/video/49982323'
# url='http://www.cda.pl/video/941368e'
# content = getUrl(url)

def scanforVideoLink(content):
    """
    Scans for video link included encoded one
    """
    video_link=''
    src1 = re.compile('file: [\'"](.+?)[\'"],',  re.DOTALL).search(content)
    src2 = re.compile('url: [\'"](.+?)[\'"],',  re.DOTALL).search(content)
    if src1:
        #print 'found RE [file:]'
        video_link = src1.group(1)
    elif src2:
        #print 'found RE [url:]'
        video_link = src2.group(1)
    else:
        #print 'encoded : unpacker'
        video_link = _get_encoded_unpaker(content)
        if not video_link:
            #print 'encoded : force '
            video_link = _get_encoded(content)
    return video_link

#url='http://www.cda.pl/video/5393794a'
#stream_url =getVideoUrls(url)
def getVideoUrls(url,tryIT=4):
    """
    returns 
        - ulr http://....
        - or list of [('720p', 'http://www.cda.pl/video/1946991f?wersja=720p'),...]
         
    """  
    # check if version is selecte
    playerSWF1='|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/player5.9/player.swf'
    playerSWF='|Referer=http://static.cda.pl/player5.9/player.swf'
    #print url
    content = getUrl(url)
    src=[]
    
    if content=='':
        src.append(('Materiał został usunięty',''))
    lic1 = content.find('To wideo jest niedostępne ')
    if lic1>0:
        src.append(('To wideo jest niedostępne w Twoim kraju','')) 
    elif not '?wersja' in url:
        quality_options = re.compile('<a data-quality="(.*?)" (?P<H>.*?)>(?P<Q>.*?)</a>', re.DOTALL).findall(content)
        for quality in quality_options:
             link = re.search('href="(.*?)"',quality[1])
             hd = quality[2]
             src.insert(0,(hd,BASEURL+link.group(1)))
    if not src:     # no qualities availabe ... get whaterer is there
        src = scanforVideoLink(content)
        if src:
            src+=playerSWF1+playerSWF
        else:
            for i in range(tryIT):
                #print 'Trying get link %d' %i
                #print url
                content = getUrl(url)
                src = scanforVideoLink(content)
                if src: 
                    src+=playerSWF1+playerSWF
                    break
    return src    


def getVideoUrlsQuality(url,quality=0):
    """
    returns url to video
    """
    src = getVideoUrls(url)
    if type(src)==list:
        selected=src[quality]
        #print 'Quality :',selected[0]
        src = getVideoUrls(selected[1])
    return src
    
#url='http://www.cda.pl/Witold_Prochnicki/folder/805805/'
def _scan_UserFolder(url,recursive=True,items=[],folders=[]):
    content = getUrl(url)
    items = items
    folders = folders
    
    #match   = re.compile('<a href="(.*?)">(.*?)</a> <span class="hidden-viewTiles">(.*?)</span>').findall(content)
    match   = re.compile('class="link-title-visit" href="(.*?)">(.*?)</a>').findall(content)
    matchT  = re.compile('class="time-thumb-fold">(.*?)</span>').findall(content)
    matchHD = re.compile('class="thumbnail-hd-ico">(.*?)</span>').findall(content)
    matchHD = [a.replace('<span class="hd-ico-elem">','') for a in matchHD]
    # matchIM = re.compile('<img[ \t\n]+class="thumb thumb-bg thumb-size"[ \t\n]+alt="(.*?)"[ \t\n]+src="(.*?)">',re.DOTALL).findall(content)
    matchIM = re.compile('<img[ \t\n]+class="thumb thumb-bg thumb-size"[ \t\n]+alt="(.*?)"[ \t\n]+src="(.*?)">',re.DOTALL).findall(content)
    
    #print 'Video #%d' %(len(match))

    for i in range(len(match)):
        url = BASEURL+ match[i][0]
        title = unicodePLchar(match[i][1])
        duration_str = matchT[i] if matchT[i] else '0'
        duration =  sum([a*b for a,b in zip([3600,60,1], map(int,duration_str.split(':')))])
        code = matchHD[i]
        plot = unicodePLchar(matchIM[i][0])
        img = matchIM[i][1]
        items.append({'url':url,'title':unicode(title,'utf-8'),'code':code.encode('utf-8'),'plot':unicode(plot,'utf-8'),'img':img,'duration':duration})
    
    # Folders
    folders_links = re.compile('class="folder-area">[ \t\n]+<a[ \t\n]+href="(.*?)"',re.DOTALL).findall(content)
    folders_names = re.compile('<span[ \t\n]+class="name-folder">(.*?)</span>',re.DOTALL).findall(content)
    if folders_links:
        if len(folders_names) > len(folders_links): folders_names = folders_names[1:]   # remove parent folder is exists
        for i in range(len(folders_links)):
            folders.append( {'url':folders_links[i],'title': html_entity_decode(folders_names[i]) })
    # print 'Folder #%d ' %(len(folders_links))
    
    nextpage = re.compile('<div class="paginationControl">[ \t\n]+<a class="btn btn-primary block" href="(.*?)"',re.DOTALL).findall(content)
    
    if recursive and len(nextpage):
        # print 'Entering next page: ', nextpage[0]
        _scan_UserFolder(nextpage[0],recursive,items)
    
    return items,folders

#url='http://www.cda.pl/ramicspa/obserwowani'
def get_UserFolder_obserwowani(url):
    content = getUrl(url)
    items = []
    folders = []
    match=re.compile('@użytkownicy(.*?)<div class="panel-footer"></div>', re.DOTALL).findall(content)
    if len(match) > 0:
        data = re.compile('data-user="(.*?)" href="(.*?)"(.*?)src="(.*?)"', re.DOTALL).findall(match[0])
        for one in data:
            folders.append( {'url':one[1]+'/folder-glowny','title': html_entity_decode(one[0]),'img':one[3] })
    return items,folders
              
# urlF='http://www.cda.pl/ramicspa/folder-glowny?type=pliki'
# urlF='http://www.cda.pl/ramicspa/ulubione/folder-glowny'
def get_UserFolder_content( urlF,recursive=True,filtr_items={}):
    items=[]
    folders=[]
    items,folders=_scan_UserFolder(urlF,recursive,items,folders)
    _items=[]
    if filtr_items:
        cnt=0
        key = filtr_items.keys()[0]
        value = filtr_items[key].encode("utf-8")
        for item in items:
            if value in item.get(key):
                cnt +=1
                _items.append(item)
        items = _items
        print 'Filted %d items by [%s in %s]' %(cnt, value, key)
    return items,folders


    
def l2d(l):
    """
    converts list to dictionary for safe data picup
    """
    return dict(zip(range(len(l)),l))

# url='http://www.cda.pl/video/show/3d_dubbing/p1?duration=dlugie&section=&quality=720p&section=&s=best&section='
# url='http://www.cda.pl/video/show/film_lektor_pl_dubbing/p1?duration=dlugie&section=&quality=720p&section=&s=date&section='

# items=searchCDA(url)
# print_toJson(items)
def searchCDA(url):
    content = getUrl(url)
    labels=re.compile('<label(.*?)</label>', re.DOTALL).findall(content)
    nextpage =re.compile(' class="sbmBigNext btn-my btn-large fiximg" href="(.*?)">').findall(content)
    
    items=[]
    #label=labels[0]
    for label in labels:
        if label.find('premium')>0: 
            continue
        plot = re.compile('title="(.*)"').findall(label)
        image = re.compile('src="(.*)" ').findall(label)
        hd = re.compile('<span class="hd-ico-elem hd-elem-pos">(.*?)</span>').findall(label)
        duration = re.compile('<span class="timeElem">\s+(.*?)\s+</span>').findall(label)
        title=re.compile('<a class=".*?" href="(/video/.*?)">(.*?)</a>').findall(label)
        nowosc = 'Nowość' if label.find('Nowość')>0 else ''
        if title:
            if len(title[0])==2:
                url = BASEURL+ title[0][0]
                title = unicodePLchar(title[0][1])
                duration =  sum([a*b for a,b in zip([3600,60,1], map(int,duration[0].split(':')))]) if duration else ''
                code = hd[0] if hd else ''
                plot = unicodePLchar(plot[0]) if plot else ''
                img = image[0] if image else ''
                items.append({'url':url,'title':unicode(title,'utf-8'),'code':code,'plot':unicode(plot,'utf-8'),'img':img,'duration':duration,'new':nowosc})
    if items and nextpage:
        nextpage = BASEURL+ nextpage[0]
    return items,nextpage

def print_toJson(items):
    for i in items:
        print i.get('title')
        #print 'title':i.get('title'),'url':i.get('url'),'code':i.get('code')}
        print '{"title":"%s","url":"%s","code":"%s"}' % (i.get('title'),i.get('url'),i.get('code'))

#title='Straight Outta Compton 2015 Lektor PL 1080p x265 by LexusFR'
#title='Pan Hoppy i Żółwie / Roald Dahl’s Esio Trot (2015) Lektor PL'
def cleanTitle(title):
    #title=unicodePLchar(title)
    pattern = re.compile(r"[(\[{;,/]")
    year=''
    label=''
    reyear = re.search('\d{4}',title)
    relabel = re.compile('(?:lektor|pl|dubbing|napis[y]*)', flags=re.I | re.X).findall(title.lower())
    if relabel:
        label = ' [COLOR green] %s [/COLOR]' % ' '.join(relabel)
    if reyear:
        title = re.sub('\d{4}','',title)
        year = reyear.group()
    title = pattern.split(title)[0]
    
    title=title.lower()
    rmList=['lektor','dubbing',' pl ','full','hd','*','720p','180p','"']
    for rm in rmList:
        title = title.replace(rm,'')
    return title.strip(), year, label.strip()

# url='http://www.cda.pl/video/6080383d'
# out=grabInforFromLink(url)
def grabInforFromLink(url):
    out={}
    if not 'www.cda.pl/video/' in url:
        return out
    content = getUrl(url)
    plot=re.compile('<meta property="og:description" content="(.*?)"/>').findall(content)    
    title=re.compile('<meta property="og:title" content="(.*?)"/>').findall(content)   
    image=re.compile('<meta property="og:image" content="(.*?)"/>').findall(content)   
    video_id = url.split('?')[0].split('/')[-1]
    quality=re.compile('href="/video/'+video_id+'\?wersja=(.*?)"').findall(content)
    durationf = re.compile('<meta itemprop=[\'\"]duration[\'\"] content=[\'\"](.*?)[\'\"]/').findall(content)
    if title:
        title = unicodePLchar(title[0])
        duration=''
        if durationf:
            tmp=re.compile('(\d)').findall(durationf[0])
            while len(tmp)<3:
                tmp.insert(0,'0')
            duration =  sum([a*b for a,b in zip([3600,60,1], map(int,tmp))]) if tmp else ''
        
        code = quality[-1] if quality else ''
        plot = unicodePLchar(plot[0]) if plot else ''
        img = image[0] if image else ''
        out={'url':url,'title':unicode(title,'utf-8'),'code':code,'plot':unicode(plot,'utf-8'),'img':img,'duration':duration}
    return out
    
## JSON TASK

import htmlentitydefs

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
    

def ReadJsonFile(jfilename):
    content = '[]'
    if jfilename.startswith('http'):
        content = getUrl(jfilename)
    elif os.path.exists(jfilename):    # local content
        with open(jfilename,'r') as f:
            content = f.read()
            if not content:
                content ='[]'
    data=json.loads(html_entity_decode(content))
    #data=json.loads(html_entity_decode(content), object_pairs_hook=OrderedDict)
    return data

# jfilename=r'C:\Users\ramic\OneDrive\Public\Kodi\cdapl\bajki.json'
# jfilename=r'C:\Users\ramic\OneDrive\Public\Kodi\cdapl\filmy3D.json'
# mydict=ReadJsonFile(jfilename)
# a=xpath(mydict,'')
def xpath(mydict, path=''):
    elem = mydict
    if path:
        try:
            for x in path.strip("/").split("/"):
                elem = elem.get( x.decode('utf-8') )
        except:
            pass
    return elem
    
def jsconWalk(data,path):
    lista_katalogow = []
    lista_pozycji=[]
    
    elems = xpath(data,path) 
    if type(elems) is dict: # or type(elems) is OrderedDict:
        # created directory
        for e in elems.keys():
            one=elems.get(e)
            if type(one) is str or type(one) is unicode:    # another json file
                lista_katalogow.append( {'img':'','title':e,'url':"", "jsonfile" :one} )
            elif type(one) is dict and one.has_key('jsonfile'): # another json file v2
                one['title']=e  # dodaj tytul
                one['url']='' 
                lista_katalogow.append( one )
            else:
                if isinstance(e, unicode):
                    e = e.encode('utf8')
                elif isinstance(e, str):
                    # Must be encoded in UTF-8
                    e.decode('utf8')
                lista_katalogow.append( {'img':'','title':e,'url':path+'/'+e,'fanart':''} )
        if lista_katalogow:
             lista_katalogow= sorted(lista_katalogow, key=lambda k: (k.get('idx',''),k.get('title','')))
    if type(elems) is list:
        print 'List items'
        for one in elems:
            # check if direct link or User folder:
            if one.has_key('url'):
                lista_pozycji.append( one )
            elif one.has_key('folder'):        #This is folder in cds.pl get content:
                filtr_items = one.get('flter_item',{})
                show_subfolders = one.get('subfoders',True)
                show_items = one.get('items',True)
                is_recursive = one.get('recursive',True)
                
                items,folders = get_UserFolder_content( 
                                        urlF        = one.get('folder',''),
                                        recursive   = is_recursive,
                                        filtr_items = filtr_items )
                if show_subfolders:
                    lista_katalogow.extend(folders)
                if show_items:
                    lista_pozycji.extend(items)
                
    return (lista_pozycji,lista_katalogow)
    


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


## Permium

     
def premium_Katagorie():
    url='http://www.cda.pl/premium'
    content = getUrl(url)
    genre = re.compile('<li><a href="(http://www.cda.pl/premium/.*?)">(.*?)</a></li>', re.DOTALL).findall(content)
    out=[]
    for one in genre:
        out.append({'title':unicodePLchar(one[1]),'url':one[0]})
    if out:
        out.insert(0,{'title':'[B]Wszystkie filmy[/B]','url':'http://www.cda.pl/premium'})
    return out

#content=jtmp.get('html')
def premium_readContent(content):
    ids = [(a.start(), a.end()) for a in re.finditer('<span class="cover-area">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        item = content[ ids[i][1]:ids[i+1][0] ]
        #href_title = re.compile('<a href="(.*?)\?from=catalog" class="kino-title">(.*?)</a>').findall(item)[0]
        
        href = re.compile('<a href="(.*?)"').findall(item)
        title= re.compile('class="kino-title">(.*?)<').findall(item)
        img = re.compile('src="(http.*?)"').findall(item)
        quality = re.compile('"cloud-gray">(.*?p)<').findall(item)
        rate = re.compile('<span class="marker">(.*?)<').findall(item)

        if title and href:
            try:
                rating = float(rate[0]) if rate else ''
            except:
                rating = ''

            out.append({
                'title':unicodePLchar(title[0]),
                'url':BASEURL+href[0],
                'img':img[0] if img else '',
                'code':quality[-1] if quality else '',
                'rating':rating
                })
    return out

# def premium_readContent(content):
#     items = re.compile('<span class="cover-area">(.*?[\n\t ]*</span>)[\n\t ]*</span>\n</span>',re.DOTALL).findall(content)
#     out=[]
#     #print len(items)
#     #item=items[0]
#     for i,item in enumerate(items):
#         #print item
# 
#         href_title = re.compile('<a href="(.*?)\?from=catalog" class="kino-title">(.*?)</a>').findall(item)[0]
#         img = re.compile('src="(http.*?)"').findall(item)[0]
#         quality = re.compile('"cloud-gray">(.*?p)<').findall(item)[-1]
#         out.append({
#             'title':unicodePLchar(href_title[1]),
#             'url':BASEURL+href_title[0],
#             'img':img,'code':quality
#             })
#     return out

def premium_Sort():
    return {'nowo dodane':'new',
    'alfabetycznie':'alpha',
    'najlepiej oceniane na Filmweb':'best',
    'najczęściej oceniane na Filmweb':'popular',
    'data premiery kinowej':'release',
    'popularne w ciągu ostatnich 60 dni':'views',
    'popularne w ciągu ostatnich 30 dni':'views30'}
    

#url='http://www.cda.pl/premium/akcji?sort=alpha&d=2'
#params='3_all_alpha'
def premium_Content(url,params=''):
    if len(params)==0:
        content = getUrl(url)
        out = premium_readContent(content)
        match = re.compile('katalogLoadMore\(page,"(.*?)","(.*?)",').findall(content)
        if match:
            #params = [2,match[0][0],match[0][1],{}]
            params = '%d_%s_%s' %(2,match[0][0],match[0][1])
    else:
        sp = params.split('_')
        myparams = [int(sp[0]),sp[1],sp[2],{}]
        payload = {"jsonrpc":"2.0","method":"katalogLoadMore","params":myparams,"id":2}
        content = getUrl(url.split('?')[0]+'?d=2',data=json.dumps(payload),Refer=True)
        jtmp=json.loads(content).get('result')
        if jtmp.get('status') =='continue':
            params = '%d_%s_%s' % (int(sp[0])+1,sp[1],sp[2])
        else:
            params = ''
        out = premium_readContent(jtmp.get('html'))
    return out,params

# url='http://www.cda.pl/premium/muzyczne?sort=new&d=2'        
# out,params=premium_Content(url)
# print out[0].get('title')
# print params
# out,params=premium_Content('http://www.cda.pl/premium/horror?sort=new&d=2',params)

# payload = {"jsonrpc":"2.0","method":"katalogLoadMore","params":[1,"10","new",{}],"id":2}
# payload = {"jsonrpc":"2.0","method":"katalogLoadMore","params":[1,"all","best",{}],"id":2}
# 
# content = getUrl(url,data=json.dumps(payload))
# a=json.loads(content)
# r=a['result']
# r['status']
# content=r['html']



