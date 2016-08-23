# -*- coding: utf-8 -*-

import re
import urllib2,urllib
import base64
import urlparse
import jsunpack
try:
    import execjs
except:
    pass
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
    
#url=pageUrl[0]
def decode(url,data):
    #query=re.search('src=["\'](http.*?)["\']',data)
    # if query:
    #     query=query.group(1)
    #     
    srcs=re.compile('src=["\'](http.*?)["\']').findall(data)
    #query = srcs[0]
    ## MAIN CASE
    for query in srcs:
        if 'livecounter' in query:
            pass
        elif 'widestream.io' in query:
            print '@@widestream.io'    #D
            return _widestream(query,data,url)  
        elif 'static.nowlive.xyz' in query:
            print '@@static.nowlive.xyz'    #D
            return _staticnowlive(query,data,url)  
        elif 'delta-live.pro' in query:
            print '@@delta-live.pro'    #DONE
            return _deltalivepro(query,data,url)  
        elif 'openlive.org' in query:
            print '@@openlive.org'    #DONE
            return _openlive(query,data,url)  
        elif 'sawlive.tv' in query:
            print '@@sawlive.tv'    #DONE
            return _sawlivetv(query,data,url)    
        elif 'pxstream.tv' in query:
            print '@@pxstream'
            return _pxstream(query,data,url)
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
            print '@@static.bro.adca.st'
            return _static_bro_adca_st(query,data,url)
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


def _widestream(query,data,url):
    vido_url=''
    header = {'User-Agent':UA,
             'Referer': url,}
    decoded = getUrl(query,header=header)
    file = re.compile('file: "(.*?)"').search(decoded)
    if file:
        vido_url=file.group(1)
    return vido_url 
    
def _staticnowlive(query,data,url):
    #http://163.172.216.164/swf/6459.m3u8?sf=NTdiOThlZTEyMmY4Ng==&token=D9YZNC8NIQnSnIzkR-pf0g
    vido_url=''
    feed = re.compile('id=[\'"](.*?)[\'"]; width=[\'"](.*?)[\'"]; height=[\'"](.*?)[\'"];').findall(data)
    if feed:
        src2='http://nowlive.pw/stream.php?id=%s&width=%s&height=%s&stretching=uniform&p=1'%feed[0]
        header = {'User-Agent':UA,
                 'Referer': url,}
        decoded = getUrl(src2,header=header)
        stream = re.compile('curl = "(.*?)"').findall(decoded)
        h = "|Cookie=%s" % urllib.quote('PHPSESSID=1')
        header={'User-Agent':UA,'Referer': src2,'Host':'nowlive.pw',
        'X-Requested-With':'XMLHttpRequest',
        'Cookie':'_ga=GA1.2.971820973.1471970062; _gat=1'}
        
        token_data = getUrl('http://nowlive.pw/getToken.php',header=header)
        token = re.compile('"token":"(.*?)"').findall(token_data)
        if token and stream:
            vido_url = base64.b64decode(stream[0]) + token[0] +'|Referer==http://nowlive.pw/jwplayer.flash.swf'
    return vido_url    
    
def _deltalivepro(query,data,url):
    #rtmp://demo.fms.visionip.tv/live/<playpath>demo-sub-polsat2-hsslive-25f-16x9-SD <swfUrl>http://delta-live.pro/floplayer/flowplayer-3.2.18.swf <pageUrl>http://delta-live.pro/streams/ogolne/polsat1.html
    vido_url=''
    file = re.compile('url: \'(.*?)\'').search(data)
    rtmp = re.compile('netConnectionUrl: \'(.*?)\'').search(data)
    swfUrl = re.search('"player", "(.*?.swf)"',data)
    if file and rtmp and swfUrl:
        vido_url = rtmp.group(1) + ' playpath='+file.group(1).strip() +' swfUrl='+swfUrl.group(1) + ' swfVfy=1 live=1 timeout=13  pageUrl='+url
    return vido_url   
    
def _openlive(query,data,url):
    #rtmp://94.176.148.234/live?token=IX5KIjKObbvIjTyK3x3bQAExpired=1471982518<playpath>ver27987b5ad39232b2a109471e62c0ac81 <swfUrl>http://p.jwpcdn.com/6/12/jwplayer.flash.swf <pageUrl>http://openlive.org/embed.php?file=deltajedynka&width=620&height=420

    vido_url=''
    feed = re.compile('file=[\'"](.*?)[\'"]; width=[\'"](.*?)[\'"]; height=[\'"](.*?)[\'"];').findall(data)
    if feed:
        src2='http://openlive.org/embed.php?file=%s&width=%s&height=%s'%feed[0]
        
        header = {'User-Agent':UA,
                    'Referer': url,}
        decoded = getUrl(src2,header=header)
        swfUrl = ['http://p.jwpcdn.com/6/12/jwplayer.flash.swf']
        stream = re.compile('\'streamer\'[:, ]+\'(.*?)\'').findall(decoded)
        file   = re.compile('\'file\'[:, ]+\'(.*?)\'').findall(decoded)
        if swfUrl and stream and file:
            u_p=urlparse.urlparse(stream[0])
            request = urllib2.Request('http://'+u_p.netloc+u_p.path, None, header)
            data =  urllib2.urlopen(request)
            ip,port=data.fp._sock.fp._sock.getpeername()
            rtmp = 'rtmp://94.176.148.234/live?'+u_p.query
            vido_url = rtmp +' playpath='+file[0] + ' swfUrl='+swfUrl[0] + ' swfVfy=1 live=1  timeout=10 pageUrl='+src2 #swfVfy=1 live=1 
    return vido_url
    
#query='http://sawlive.tv/embed/tvp22'
#query='http://sawlive.tv/embed/canalsport'
def _sawlivetv(query,data,url):
    vido_url=''
    source = getUrl(query)
    try:
        decoded = jsunpack.unpack(source.decode('string_escape'))
    except:
        decoded =''
    src=re.compile('src=["\'](http:.*?)["\']').findall(decoded)
    if src:
        header = {'Referer':  src[0], 'User-Agent': UA}
        decoded = getUrl(src[0].replace('/view/','/watch/'),header=header)
        
        swfUrl = re.compile('SWFObject\(\'(.*?)\'').findall(decoded)
        match = re.compile('(eval\(function\(p,a,c,k,e,d\).*?)\n').findall(decoded)
        if match:
            decoded = jsunpack.unpack(match[0].decode('string_escape'))
        
            unscape = lambda x: x.group(0).replace('%','').decode('hex')
            decoded = re.sub('%.{2}',unscape,decoded)
            
            code = decoded.replace("so.addVariable('file',","file=")
            code = code.replace("so.addVariable('streamer',","streamer=")
            code = code.replace("));",");")
            code = code.replace("unescape","")
            
            context = js2py.EvalJs() 
            context.execute(code)
            streamer= getattr(context,'streamer')
            file= getattr(context,'file')
        
        
            if swfUrl and streamer and file:
                vido_url = streamer +' playpath='+file + ' swfUrl='+swfUrl[0] + ' swfVfy=1 live=1 timeout=13   pageUrl='+src[0]
        # 
        # match22 = re.compile("SWFObject\('(.*?)','mpl','100%','100%','9'\);").findall(data)
        # match23 = re.compile("so.addVariable\('file', '(.*?)'\);").findall(data)
        # match24 = re.compile("so.addVariable\('streamer', '(.*?)'\);").findall(data)
        # print ("Match", match22, match23, match24, link22)
        # videolink = match24[0] + ' playpath=' + match23[0] + ' swfUrl=' + match22[
        #     0] + ' pageUrl=http://sawlive.tv/embed/' + channel + ' live=true swfVfy=true'
        # vido_url = src[0]#+'|Referer='+query+'&User-Agent=' + UA 
    return vido_url
##
def _pxstream(query,data,url):
    vido_url=''
    feed = re.compile('file=[\'"](.*?)[\'"]; width=[\'"](.*?)[\'"]; height=[\'"](.*?)[\'"];').findall(data)
    if feed:
        #link=getUrl(query)
        myfeed=list(feed[0])
        myfeed.insert(1,url)
        src2='http://pxstream.tv/embed.php?file=%s&referrer=%s&width=%s&height=%s&jwplayer=flash'%tuple(myfeed)
        
        header = {'User-Agent':UA,
                    'Referer': url,
                    'Host':'pxstream.tv'}
        decoded = getUrl(src2,header=header)
        file = re.compile('file:\s*[\'"](.*?)[\'"]').findall(decoded)
        provider = re.compile('provider:\s*[\'"](.*?)[\'"]').findall(decoded)
        if provider:
            provider = provider[0]
            provider = 'http:' + provider if provider.startswith('//') else provider
        else:
            provider = 'http://api.peer5.com/jwplayer6/assets/flashls.provider.swf'
        if file:
            vido_url = file[0]+'|Referer='+src2+'&User-Agent=' + UA #+ '&X-Requested-With=' + '1' #constants.get_shockwave()

    return vido_url
  
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


def _static_bro_adca_st(query,data,url):
    vido_url=''
    #http://jar2.musicterritory.xyz/swf/2682.m3u8?sf=NTczZGY3NzMxNjVjZA==&token=uqEYnMwC2ydIRr5v4_mzqw
    #print 'DATA'
    #print data
    feed = re.compile('id=[\'"](.*?)[\'"]; width=[\'"](.*?)[\'"]; height=[\'"](.*?)[\'"];').findall(data)
    #print 'FEED'
    #print feed
    if feed:
        qlink=getUrl(query)
        src2=re.compile('src="(.*?)"').findall(qlink)
        src2=src2[0] if src2 else 'brocast.tech'
        host = urlparse.urlparse(src2).netloc
        #src2='http://ebookterritory.pw/stream.php?id=%s&width=%s&height=%s&stretching=uniform'%feed[0]
        src2='http://'+host+'/stream.php?id=%s&width=%s&height=%s&stretching=uniform'%feed[0]
        
        header = {'User-Agent':UA,
                'Referer': url,
                'Host':host,#'ebookterritory.pw',
                 }
        
        cookies=''
        decoded = getUrl(src2,header=header,cookies=cookies)  # grab Cookies asd well  
        curl = re.search('curl = "(.*?)"',decoded)
        
        header = {'User-Agent':UA,
                'Referer': src2,
                'Host':host,#'ebookterritory.pw',
                'X-Requested-With':'XMLHttpRequest'}
        #url_t='http://ebookterritory.pw/getToken.php'
        url_t='http://'+host+'/getToken.php'
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