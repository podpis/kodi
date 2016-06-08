# -*- coding: utf-8 -*-

import urllib2,urllib
import os
import re
import base64,json
import cookielib
import cfcookie
import random
try:
    import captcha
except:
    pass

BASEURL='http://www.efilmy.net/'
TIMEOUT = 10

UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
header={
    'User-Agent':UA,
    'Host':'www.efilmy.tv',
    'Upgrade-Insecure-Requests':'1',
    'Connection': 'keep-alive',
    'Accept':'text/html,application/xhtml+xml,application/',
    }

# COOKIEFILE = r'C:\Users\ramic\AppData\Roaming\Kodi\addons\plugin.video.efilmy\resources\lib\1efimly.cookie'
COOKIEFILE=''

def getUrl(url,data=None,header={},useCookies=True,saveCookie=False):
    if COOKIEFILE and os.path.isfile(COOKIEFILE) and useCookies:
        cj = cookielib.LWPCookieJar()
        cj.load(COOKIEFILE)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    
    req = urllib2.Request(url,data)
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link =  response.read()
        response.close()
        if COOKIEFILE and os.path.isfile(COOKIEFILE) and saveCookie and useCookies:
             cj.save(COOKIEFILE, ignore_discard = True) 
    except urllib2.HTTPError as e:
        #link = e.read()
        link = ''
    return link

#url='http://www.efilmy.tv/filmy.html'
#url='http://www.efilmy.tv/filmy,p1.html'
#filmy,pagination =get_content(url)
def get_content(url):
    out=[]
    prevPage=''
    nextPage=''
    header['Referer']=url,
    url=url.replace('efilmy.tv/','efilmy.net/')
    content = getUrl(url,header=header)
    items = re.compile('<div class="list-item">(.*?)</div>',re.DOTALL).findall(content)
    #item=items[3]
    len(items)
    for item in items:
        # href = re.compile('href="(.*?)"').findall(item)
        # title = re.compile('title="(.*?)"').findall(item)
        title_pl = re.compile('<a title=".*?" href="(.*?)" class="title_pl">(.*?)</a>').findall(item)
        print title_pl
        title_en = re.compile('class="title_en">(.*?)</a>').findall(item)
        genre = re.compile('<span class="dst">Kategoria: <a title=".*?" href=".*?">(.*?)</a>').findall(item)
        opis = re.compile('<p>(.*?)</p>').findall(item)
        img = re.compile('<img class="poster" src="(.*?)"').findall(item)
        if title_pl and img:
            h= BASEURL+title_pl[0][0]
            t= title_pl[0][1]
            i= 'http://www.efilmy.tv/'+img[0].replace('/small/','/big/')
            d= genre[0] if genre else ''
            o= opis[0] if opis else ''
            year=''
            audio=''
            t_en=''
            if title_en:
                year,audio = title_en[0].split('|')[-1].split(',')
                t_en=title_en[0].split('|')[0].strip()
                year = year.strip()
                audio = '[COLOR green] %s [/COLOR]'%audio.strip()
            out.append({'title':unicodePLchar(t),'title_en':unicodePLchar(t_en),'audio':audio,'url':h,'img':i,'year':year,'plot':o})

    # pagination
    pagination = re.compile('<div class="pagin">(.*?)</div>',re.DOTALL).findall(content)
    if pagination:
        prevPage=re.compile('<a href="(.*?)".*?>\&laquo;</a>').findall(pagination[0])
        nextPage=re.compile('<a href="(.*?)"').findall(pagination[0])
        if prevPage:
            prevPage = BASEURL + prevPage[0]
        if nextPage:
            nextPage = BASEURL + nextPage[-1]
        
    return (out, (prevPage,nextPage))

#get_movie_cat_year(what='cat')
#get_movie_cat_year(what='year')
def get_movie_cat_year(what='year'):
    #what='cat' or 'year'
    out=[]
    url='http://www.efilmy.net/filmy.html'
    header['Referer']=url
    content = getUrl(url,header=header)
    movie_cat = re.compile('<ul class="movie-%s">(.*?)</ul>'%what,re.DOTALL).findall(content)
    if movie_cat:
        if what=='cat':
            kats = re.compile('<a title=".*?" href="(.*?)">(.*?)</a><span>(.*?)</span>').findall(movie_cat[0])
            for k in kats:
                out.append( (' '.join(k[1:]),BASEURL+k[0]) )
        else:
            kats = re.compile('<a title="(.*?)" href="(.*?)">').findall(movie_cat[0])
            for k in kats:
                out.append((k[0],BASEURL+k[1]))
    return out

def get_Serial_list(page=0):
    out=[]
    url='http://www.efilmy.net//seriale.php?cmd=slist&page=%d'%page
    content = getUrl(url,header=header)
    items= re.compile('<a title=".*?" href="(.*?)">(.*?)</a>').findall(content)
    for item in items:
        out.append({'title':unicodePLchar(item[1]),'url':BASEURL+item[0]})
    return out

#url='http://www.efilmy.tv/serial,19,Agenci-NCIS-Los-Angeles-NCIS-Los-Angeles-2009-2011.html'
def get_Episode_list(url):
    out=[]
    header['Referer']=url,
    url=url.replace('efilmy.tv/','efilmy.net/')
    content = getUrl(url,header=header)
    idx = content.find('<div class="holder">')
    episodes = re.compile('<li>(.*?)</li>',re.DOTALL).findall(content[idx:])
    len(episodes)
    for e in episodes:
        href=re.compile('href="(.*?)"').findall(e)
        title=re.compile('>(.*?)<').findall(e)
        if href and title:
            h= BASEURL+href[0]
            t=''.join(title).replace('-->','').strip()
            out.append({'title':unicodePLchar(t),'url':h})
    return out

#    url='http://www.efilmy.net/filmy.php?cmd=popularne&dni=7'
#    url='http://www.efilmy.net/seriale.php?cmd=popularne&dni=7'
#http://www.efilmy.tv/filmy.php?cmd=watched #Teraz Oglądane
#http://www.efilmy.net/filmy.php?cmd=added   # Ostatnio Dodane
url='http://www.efilmy.net/filmy.php?cmd=added'
def get_top(url):
    #filmy,seriale
    out=[]
    # url='http://www.efilmy.net/filmy.php?cmd=popularne&dni=7'
    # url='http://www.efilmy.net/seriale.php?cmd=popularne&dni=7'
    header['Referer']=url,

    content = getUrl(url,header=header)

    divs= re.compile('(<div class=.*?</div>)',re.DOTALL).findall(content)
    #item = divs[3]
    for item in divs:
        title_pl = re.compile('href="(.*?)" class="pl">(.*?)</a>').findall(item)
        title_en = re.compile('class="en">(.*?)</a>').findall(item)
        genre = re.compile('<span class="(cat|dsc)">.*?<a title=".*?" href=".*?">(.*?)</a>(.*?)<').findall(item)
        opis = re.compile('<p>(.*?)</p>').findall(item)
        img = re.compile('src="(.*?)"').findall(item)
        #title_pl = re.compile('>(.*?)<').findall(item)
        one={}
        if title_pl :
            one['url']= BASEURL+title_pl[0][0]
            one['title']= unicodePLchar(title_pl[0][1])
            one['img']= 'http://www.efilmy.net/'+img[0].replace('/small/','/big/') if img else ''
            one['year']=''
            if genre:
                if len(genre[0])==3:
                    one['genre']= genre[0][1] if genre else ''
                    try:
                        audio,year = genre[0][-1].split('|')[-1].split(',')
                        one['year'] = year.strip()
                        one['audio'] = ' [COLOR green] %s [/COLOR]'%audio.strip()
                    except:
                        pass
                    
            one['plot']= opis[0] if opis else ''
            if len(title_en)==2: # Episodes
                one['title'] += ' [COLOR lightblue]%s[/COLOR]' %(' '.join(title_en))
            out.append(one)
    return out
#m,s=search(txt='futurama')
def search(txt='futurama'):
    url='http://www.efilmy.net/autocomm.php?query=%s'%(txt.replace(' ','+'))
    out_m=[]
    out_s=[]
    # url='http://www.efilmy.net/filmy.php?cmd=popularne&dni=7'
    # url='http://www.efilmy.net/seriale.php?cmd=popularne&dni=7'
    header['Referer']=url

    content = getUrl(url,header=header)
    if content:
        try:
            jdata = json.loads(content)
        except:
            jdata={}
        
        suggestions=jdata.get('suggestions',[])
        for s in suggestions:
            one={}
            one['title']=unicodePLchar(s.get('value',''))
            one['url'] = BASEURL + s.get('data','')
            one['img'] = BASEURL + s.get('img','')
            if 'm' in s['t']:   #Movie
                out_m.append(one)
            else:
                out_s.append(one)
    return out_m,out_s
        
        
# url='http://www.efilmy.tv/filmy,rok-2014.html'    
# url='http://www.efilmy.net/film,28550,Koszmarna-opowiesc-wigilijna-A-Christmas-Horror-Story-2015-Lektor-PL.html'
# url='http://www.efilmy.tv/film,6000,Opowiesc-wigilijna-Muppetow-The-Muppet-Christmas-Carol-1992-Lektor-PL.html'
# url='http://www.efilmy.tv/film,28547,Sprawiedliwy-2015-PL.html'
url='http://www.efilmy.tv/serial,6,13-Posterunek-1997-2000,sezon-1,odcinek-1.html'
url='http://www.efilmy.tv/serial,107,Chirurdzy-Grey-s-Anatomy-2005-2011,sezon-12,odcinek-1.html'
url='http://www.efilmy.tv/filmy.php?id=13577&title=Futurama-Potwor-o-miliardzie-grzbietow-Futurama-The-Beast-with-a-Billion-Backs-2008-Lektor-PL'
url='http://www.efilmy.tv/film,14972,Szybki-cash-Snabba-Cash-2010-Lektor-PL.html'
url='http://www.efilmy.tv/serial,9,24-godziny-2002,sezon-9,odcinek-1.html'
url='http://www.efilmy.tv/film,28633,Brama-piekiel-Hellgate-1989-Lektor-PL.html'
def getVideoLinks(url):
    outL=[]
    header['Referer']=url

    url=url.replace('efilmy.tv/','efilmy.net/')
    content = getUrl(url,header=header)
    
    players = re.compile('Odtwarzacz <em>(.*?)</em>').findall(content)
    
    typ = re.compile('name="ur_k" value="(.*?)"').findall(content)
    typfs='filmy.php'
    if typ:
        typfs = base64.b64decode(typ[0])
        typfs = typfs.split('?')[0]
    ids = re.compile('<div id="(.*?)" alt="n" class="embedbg">').findall(content)
    #id,player = zip(ids,players)[0]
    
    for id,player in zip(ids,players):
        # Here get only retular
        link = 'http://www.efilmy.net/%s?cmd=show_regular&id=%s'%(typfs,id)
        data = getUrl(link,header=header)
        if 'vidzer' in player:
            href =re.compile('<a href="(.*?)".*?id="player">').search(data).group(1)
            if href:
                video_link = href +'|Referer=http://www.vidzer.net/media/flowplayer/flowplayer.commercial-3.2.18.swf'
                outL.append({'href':video_link,'player':player,'cmd':'regular','msg': '%s (regular)' %player})
        else:
            if 'streamin.to' in player:
                href = re.compile('<a href="(.*?)" target="_blank">(.*?)</a>').findall(data)
                if href:
                    href = href[0]
                    if 'www.vidzer.net' in href[0] and  href[1].islower():
                        video_link='http://%s/embed-%s.html'%(player,href[1])
                        outL.append({'href':video_link,'player':player,'cmd':'regular','msg': '%s (regular)' %player})
            outL.append({'href':'','player':player,'cmd':'show','id':id,'typfs':typfs,'msg': '%s ([COLOR red]captcha to solve[/COLOR])' %player})
    return outL

# outL=getVideoLinks(url)
# outL[1]
# getLink_show_player(**outL[1])

def efilmy_setCookies(link,cfile):
    cj = cookielib.LWPCookieJar()
    cookieJar = cfcookie.createCookie(link.replace('efilmy.net/','efilmy.tv/'),cj,UA)
    dataPath=os.path.dirname(cfile)
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)
    if cookieJar:
        cookieJar.save(cfile, ignore_discard = True) 
    return cj
    
def getLink_show_player(typfs,id,player,**args):
    print typfs,id,player
    typfs,id,player
    video_link=''
    # Try get with existing cookies
    bs=[]
    link = 'http://www.efilmy.tv//%s?cmd=show_player&id=%s'%(typfs,id)
    cookie_string = cfcookie.cookieString(COOKIEFILE)
    if cookie_string:
        header['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        header['Cookie']=cookie_string
        header['Referer']=link
        data = getUrl(link,header=header)
        bs= re.compile('document.write\(Base64.decode\("(.*?)"\)').findall(data)
    print bs
    if bs:
        src = base64.b64decode(bs[0])
        href = re.compile('["\'](http.*?)["\']').findall(src)
        if href:
            video_link=href[0]
    else:
        cj=efilmy_setCookies(link,COOKIEFILE)
        header['Accept']='image/webp,image/*,*/*;q=0.8'
        header['Cookie']=cfcookie.cookieString(COOKIEFILE)
        url='http://www.efilmy.net/mirrory.php?cmd=generate_captcha&time=%f'%random.random()
        data = getUrl(url,header=header)
        # f=open(r'C:\Users\ramic\AppData\Roaming\Kodi\addons\plugin.video.efilmy\resources\lib\1img.png','wb')
        # f.write(data)
        # f.close()
        # print 'CAPTCHA'
        r=captcha.UserCaptcha(data)
        print r
        #r='monopody'
        header['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        header['Cookie']=cfcookie.cookieString(COOKIEFILE)
        link = 'http://www.efilmy.tv//mirrory.php?cmd=check_captcha'
        myid=id.split('_')[0]
        mode = 's' if '_s' in id else 'f'
        formdata = 'captcha=%s&id=%s&mode=%s'%(r,myid,mode)
        data = getUrl(link,formdata,header=header)
        bs= re.compile('document.write\(Base64.decode\("(.*?)"\)').findall(data)
        print bs
        if bs:
            src = base64.b64decode(bs[0])
            href = re.compile('["\'](http.*?)["\']').findall(src)
            if href:
                video_link=href[0]
    return video_link
    

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
    