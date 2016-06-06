# -*- coding: utf-8 -*-

import re
import urllib2,urllib
import base64
import urlparse
try:
    import execjs
except:
    import js2py


UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

def getUrl(url,data=None,header={},cookies=None):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=15)
        if cookies=='':
            cookies=response.info()['Set-Cookie']
        link = response.read()
        response.close()
    except:
        link=''
    return link
    

def decode(url,data):
    #query=re.search('src=["\'](http.*?)["\']',data)
    # if query:
    #     query=query.group(1)
    #     
    srcs=re.compile('src=["\'](http.*?)["\']').findall(data)
    #query = srcs[1]
    ## MAIN CASE
    for query in srcs:
        if 'livecounter' in query:
            pass
        
        elif 'myfreshinfo' in query:
            print '@@myfreshinfo'
            return _myfreshinfo(query,data,url)
        elif 'cinema-tv.xyz' in query:
            print '@@cinema-tv.xyz'
            return _cinematvxyz(query,data,url) 
        elif 'flowplayer' in query:
            print '@@flowplayer'
            return _flowplayer(query,data,url)            
        elif 'shidurlive' in query:   #TODO
            print '@@shidurlive'
            return _shidurlive(query,data,url) 
        elif 'freedocast' in query:
            print '@@freedocast'
            return _freedocast(query,data,url) 
        elif 'tvope' in query:
            print '@@tvope'
            return _tvope(query,data,url) 
        elif 'dotstream.tv' in query:
            print '@@dotstream'
            return _dotstream(query,data,url)  
        elif 'static.bro.adca.st' in query:
            print '@@jstatic.bro.adca.st'
            return _static_bro_adca_st(url,data)
        elif 'jwpsrv.com' in query:
            print '@@jwpsrv'
            return _jwpsrv(query,data)
        elif 'jwpcdn.com' in query:
            print '@@jwpcdn'
            return _jwpcdn(query,data,url)
        elif 'aliez.me' in query:
            print '@@aliez'
            return _aliez(query,data)
        elif 'ustream' in query:
            print '@@ustream'
            return _ustream(query,data)
        elif 'castto.me' in query:
            print '@@castto'
            return _static_castto_me(url,data)
        elif 'privatestream' in query:
            print '@@privatestream'
            return _privatestream(query,data)
    print srcs
    return None

##
def _myfreshinfo(query,data,url):
    vido_url=''
    data2=getUrl(query)
    s_hex = re.compile('unescape\(["\'](.*?)["\']\)').findall(data2)
    s_hex0 = s_hex[0].replace('%','').decode('hex')
    f_name = re.compile('function (.*?)\(').findall(s_hex0)[0]
    s_hex1 = s_hex[1].replace('%','').decode('hex')
    encrypted = re.compile('<SCRIPT LANGUAGE="JavaScript">%s\("(.*?)"\);</SCRIPT>'%f_name,re.DOTALL).findall(data2)
    if encrypted:
        code = encrypted[0]
        #code = code.encode('utf-8')
        code =''+code.strip('\\n')+''
        try:
            fun = s_hex0.replace('document.write(tttmmm)','return tttmmm')
            ctx = execjs.compile(fun)
            decoded = ctx.call(f_name, code)
        except:
            context = js2py.EvalJs() 
            context.execute(fun)
            decoded = getattr(context,f_name)(code)
    return vido_url    
##
def _flowplayer(query,data,url):
    vido_url=''
    rtmp = re.compile('\'(rtmp://.*?)\'').findall(data)
    swfUrl = re.compile('src:\'(http://.*?swf)\'').findall(data)
    if rtmp and swfUrl:
        vido_url = rtmp[0] + ' swfUrl='+swfUrl[0] + ' swfVfy=1 live=1 timeout=13  pageUrl='+url
    return vido_url    

def _cinematvxyz(query,data,url):
    #rtmp://stream.smcloud.net/live/<playpath>polotv <swfUrl>http://cinema-tv.xyz/floplayer/flowplayer-3.2.18.swf <pageUrl>http://cinema-tv.xyz/streams/muzyczne/polotv.php
    vido_url=''
    file = re.compile('url: \'(.*?)\'').findall(data)
    rtmp = re.compile('\'(rtmp://.*?)\'').findall(data)
    swfUrl = re.search('"player", "(.*?.swf)"',data)
    if file and rtmp and swfUrl:
        vido_url = rtmp[0] + ' playpath='+file[0].strip() +' swfUrl='+swfUrl.group(1) + ' swfVfy=1 live=1 timeout=13  pageUrl='+url
    return vido_url
##
def _shidurlive(query,data,url):
    #TODO need working example
    vido_url='TODO'
    return vido_url
    
##
def _freedocast(query,data,url):
    vido_url=''
    #rtmp://live.looknij.in/live/<playpath>FILMBOX <swfUrl>http://cdn.freedocast.com/hdflvplayer/hdplayer.swf <pageUrl>http://cinema-tv.xyz/streams/filmowe/filmboxextra.php
    link = re.compile('"streamer=(.*?)"').findall(data)
    if link:
        data2=link[0].split('&amp;')
        vido_url = data2[0] +' playpath='+data2[1].split('=')[-1] +' swfUrl='+query+ ' swfVfy=1 live=1 timeout=13  pageUrl='+url
    return vido_url  
##
def _tvope(query,data,url):
    vido_url=''
    #rtmp://play5.tvope.com/tvope<playpath>stream_tvn24 <swfUrl>http://i.tvope.com/swf/player5.4.swf <pageUrl>http://tvope.com/emb/player.php?c=tvn24&w=640&h=480&jw&d=match-sport.com
    feed = re.compile('c="(.*?)"; w=(.*?); h=(.*?);').findall(data)
    query = 'http://tvope.com/emb/player.php?c=%s&w=%s&h=%s&jw&d='%feed[0]
    query +=query+urlparse.urlparse(url).hostname
    header = {'User-Agent':UA,
                'Referer': url,
                'Host':'tvope.com'}
    decoded = getUrl(query,header=header)
    swfUrl = re.compile('SWFObject\(\'(.*?)\'').findall(decoded)
    stream = re.compile('\'streamer\',\'(.*?)\'\);').findall(decoded)
    file   = re.compile('\'file\',\'(.*?)\'\);').findall(decoded)
    if swfUrl and stream and file:
        vido_url = stream[0] +' playpath='+file[0] + ' swfUrl='+swfUrl[0] + ' swfVfy=1 live=1 timeout=13  pageUrl='+query
    return vido_url  
    
##
def _dotstream(query,data,urlref):
    vido_url=''
    query = query.replace('/pl?','/player.php?')
    header = {'User-Agent':UA,
            'Referer': urlref}
    decoded = getUrl(query,header=header)
    if decode:
        swfUrl='http://dotstream.tv/jwp/jwplayer.flash.swf'
        if re.search('a = ([0-9]+)',decoded):
            a=int(re.search('a = ([0-9]+)',decoded).group(1))
            b=int(re.search('b = ([0-9]+)',decoded).group(1))
            c=int(re.search('c = ([0-9]+)',decoded).group(1))
            d=int(re.search('d = ([0-9]+)',decoded).group(1))
            f=int(re.search('f = ([0-9]+)',decoded).group(1))
            v_part = re.search('v_part = \'(.*?)\';',decoded).group(1)
            link = 'rtmp://%d.%d.%d.%d/'%(a/f,b/f,c/f,d/f) + v_part.split('/')[1]+'/'+' playpath='+v_part.split('/')[-1]
        
            vido_url = link + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+query
    return vido_url

##
#query=url.strip()     
def get_Cookies(url,params=None,header={}):
    req = urllib2.Request(url,params,headers=header)
    sock=urllib2.urlopen(req)
    cookies=sock.info()['Set-Cookie']
    sock.close()
    return cookies
def get_cookie_value(cookies='',value='sesssid'):
    idx1=cookies.find(value+'=')
    if idx1==-1:
        return''
    else:
        idx2=cookies.find(';',idx1+1)
    return cookies[idx1:idx2]    
## Sub routines

def _static_bro_adca_st(query,data):
    vido_url=''
    #http://jar2.musicterritory.xyz/swf/2682.m3u8?sf=NTczZGY3NzMxNjVjZA==&token=uqEYnMwC2ydIRr5v4_mzqw
    print 'DATA'
    print data
    feed = re.compile('id=[\'"](.*?)[\'"]; width=[\'"](.*?)[\'"]; height=[\'"](.*?)[\'"];').findall(data)
    print 'FEED'
    print feed
    if feed:
        src2='http://ebookterritory.pw/stream.php?id=%s&width=%s&height=%s&stretching=uniform'%feed[0]
        header = {'User-Agent':UA,
                'Referer': query,
                'Host':'ebookterritory.pw',
                 }
        
        cookies=''
        decoded = getUrl(src2,header=header,cookies=cookies)  # grab Cookies asd well  
        curl = re.search('curl = "(.*?)"',decoded)
        
        header = {'User-Agent':UA,
                'Referer': src2,
                'Host':'ebookterritory.pw',
                'X-Requested-With':'XMLHttpRequest'}
        url_t='http://ebookterritory.pw/getToken.php'
        decoded2 = getUrl(url_t,header=header)   
        token = re.search('"token":"(.*?)"',decoded2)

        if curl and token:
            cookies= get_Cookies(src2,header=header) 
            h = "|Cookie=%s" % urllib.quote('PHPSESSID=1')
            #h = "|Cookie=%s" % get_cookie_value(cookies,'PHPSESSID')#PHPSESSID
            print h
            # req = urllib2.Request('http://jar3.gamersenclave.pw/swf/2682.m3u8')
            # sock=urllib2.urlopen(req)
            # a=getUrl('http://static.bro.adca.st/broadcast/drawplayer.js')

            link = base64.b64decode(curl.group(1))
            vido_url = link + token.group(1) + h+'&User-Agent='+UA+'&Referer=http://cdn.ebookterritory.pw/jwplayer.flash.swf'

    return vido_url

def _jwpcdn(query,data,url):
    vido_url=''
    file   = re.compile('[\']*file[\']*[:, ]*[\'"](.*?)[\'"]').findall(data)
    if file:
        file = file[0]
        if file.endswith('m3u8'):
            vido_url = file
        else:
            swfUrl='http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            vido_url = file + ' swfUrl='+swfUrl + ' live=1 timeout=13  pageUrl='+url  
    return vido_url
        
def _jwpsrv(query,data):
    vido_url=''
    file   = re.compile('[\']*file[\']*[:, ]*[\'"](.*?)[\'"]').findall(data)
    if file:
        file = file[0]
        if file.endswith('m3u8'):
            vido_url = file
        else:
            swfUrl='http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            vido_url = file + ' swfUrl='+swfUrl + ' live=1 timeout=13  pageUrl='+query  
    return vido_url
    
def _aliez(query,data):
    #rtmp://a2.aliez.me/live/<playpath>streama45795?token=b9afc78968817e7542aac23309d3ec51 <swfUrl>http://i.aliez.me/swf/playernew.swf?0 <pageUrl>http://emb.aliez.me/player/live.php?id=45795&w=560&h=430
    vido_url=''
    decoded=getUrl(query)
    file   = re.compile('[\'"]file[\'"][:,][\t ]*[\'"](.*?)[\'"]').findall(decoded)
    swfUrl = re.compile('embedSWF\("(.*?)"').findall(decoded)
    if file and swfUrl:
        swfUrl = swfUrl[0]
        file = urllib.unquote(file[0])
        vido_url = file + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+query
    return vido_url
    
def _ustream(query,data):
    vido_url=''
    cid = re.search('cid=(.*?)"',data)
    HLS_PLAYLIST_URL = (
        "http://iphone-streaming.ustream.tv"
        "/uhls/%s/streams/live/iphone/playlist.m3u8"
    ) 
    if cid:
        cid=cid.group(1)
        data = getUrl(HLS_PLAYLIST_URL%cid)
        if data:
            links = re.compile('\n(http.*?)\n').findall(data)
            if links:
                vido_url = links[0]
    return vido_url
    
def _privatestream(query,data):
    vido_url=''
    decoded = getUrl(query)
    src2=re.compile('"(http://privatestream.tv/.*?)"').findall(decoded)
    if src2:
        decoded = getUrl(src2[0])   
        swfUrl='http://privatestream.tv/js/jwplayer.flash.swf'
 
        a=int(re.search('a = ([0-9]+)',decoded).group(1))
        b=int(re.search('b = ([0-9]+)',decoded).group(1))
        c=int(re.search('c = ([0-9]+)',decoded).group(1))
        d=int(re.search('d = ([0-9]+)',decoded).group(1))
        f=int(re.search('f = ([0-9]+)',decoded).group(1))
        v_part = re.search('v_part = \'(.*?)\';',decoded).group(1)
        link = 'rtmp://%d.%d.%d.%d/'%(a/f,b/f,c/f,d/f) + v_part.split('/')[1]+'/'+' playpath='+v_part.split('/')[-1]
    
        vido_url = link + ' swfUrl='+swfUrl + ' live=1 timeout=13 pageUrl='+query
    return vido_url
    
def _static_castto_me(url,data):
    vido_url =''
    #http://cdn.castto.me/live/ytFxxJz6QsclKSqoYuUX/playlist.m3u8
    feed = re.compile('fid="(.*?)"; v_width=(.*?); v_height=(.*?);').findall(data)
    if feed:
        src2='http://static.castto.me/embedlivepeer5.php?channel=%s&vw=%s&vh=%s'%feed[0]
        header = {'User-Agent':UA,
                'Referer': url,
                'Host':'static.castto.me',
                }
        decoded = getUrl(src2,header=header)
        file   = re.compile('file[: ]*["\'](.*?)[\'"]').findall(decoded)
        if file:
            vido_url = file[0]
    return vido_url