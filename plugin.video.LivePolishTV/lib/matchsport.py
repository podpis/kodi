# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import execjs

UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

def fixForEPG(one):
    return one
    
def getUrl(url,data=None,header={}):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=15)
        link = response.read()
        response.close()
    except:
        link=''
    return link
    
def get_root(addheader=False):
    url='http://match-sport.com/'
    content = getUrl(url)
    match=re.compile('<li><a href="(.*?)">(.*?)</a></li>').findall(content)

    out=[]
    if addheader:
        t='[COLOR yellow]Updated: %s (iklub)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://iklub.net','group':'','urlepg':''})
    #one=match[0]
    for item in match:
        t=item[1].strip()
        out.append(fixForEPG({'title':t,'tvid':t,'img':'','url':url+item[0],'group':'','urlepg':''}))
    #return sorted(out, key=lambda k: k['title'],reverse=True)    
    return out
    
# url='http://match-sport.com/index.php'
# url='http://match-sport.com/tvn1.php'
# url='http://match-sport.com/polsatnews.php'
# url='http://match-sport.com/axn1.php'
# url='http://match-sport.com/stream16.php'
# url='http://match-sport.com/axn1.php'
# url='http://match-sport.com/stream1.php'
# url='http://match-sport.com/stream17.php' #http://static.castto.me/js/embedlivest.js
# url='http://match-sport.com/stream12.php' #http://static.bro.adca.st/broadcast/player.js
# url='http://match-sport.com/stream9.php' #
# url ='http://match-sport.com/stream23.php' #http://www.soccerjumbotv.me/ch-1.html
# url='http://match-sport.com/tvnstyle1.php'
# url='http://match-sport.com/stream3.php'
url = 'http://cinema-tv.xyz/ogolne/tvp1hd/'
def decode_url(url='http://match-sport.com/stream12.php'):
    vido_url=''
    content = getUrl(url)
    iframe=re.compile('<iframe(.*?)</iframe>').findall(content)
    if iframe:
        src=re.compile('src="(.*?)"').findall(iframe[0])[0]
        if 'reklama' in src:
            src=url
        data = getUrl(src)
        query=re.search('src=["\'](.*?)["\']',data)
        if query:
            query=query.group(1)
        else:
            query=''
        
        if 'jwpsrv' in query:
            file   = re.compile('[\']*file[\']*[:, ]*[\'"](.*?)[\'"]').findall(data)
            swfUrl='http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            if file:
                vido_url = file[0] + ' swfUrl='+swfUrl + ' live=1 timeout=13  pageUrl='+src  
        elif 'soccerjumbotv.me' in query:
            decoded = getUrl(query)
            feed = re.compile('fid="(.*?)"; v_width=(.*?); v_height=(.*?);').findall(decoded)
            src2='http://www.sostart.pw/jwplayer6.php?channel=%s&vw=%s&vh=%s'%feed[0]
            src3='http://www.sostart.pw/tk.php?id=%s'%feed[0][0]
            header = {'User-Agent':UA,
                     'Referer': src2,
                     'Host':'www.sostart.pw',
                     }
            decoded = getUrl(src3,header=header)
            rtmp = re.compile('"rtmp":"(.*?)"').findall(decoded)
            if rtmp:
                vido_url=rtmp[0] + ' swfVfy=1 live=1 timeout=13'
            #TODO to be completed ... not working source
        elif 'hdcast.info' in query:
            decoded = getUrl(query)
            fnames = re.compile('file: (.*?)\(\) \+ \'/\' \+ (.*?)\(\)').findall(decoded)
            if fnames:
                fnames=fnames[0]
                stream=[]
                authen=''
                swfUrl='http://www.hdcast.info/myplayer/jwplayer.flash.swf'
                for fname in fnames:
                    idx1 = decoded.find('function '+fname)
                    idx2 = decoded[idx1:].find('}')
                    tmp = decoded[idx1:idx1+idx2]
                    s=re.search('(\[.*?\])',tmp).group(1)
                    stream.append(''.join(eval(s)).replace('\\',''))
                    # look for auth code
                    cod=re.search('join\(\"\"\) \+ (.*?).join\(\"\"\)',tmp)
                    if cod and authen=='':
                       authen = re.search(cod.group(1)+' = (\[.*?\])',decoded).group(1)
                       authen = ''.join(eval(authen))
                vido_url = stream[0] + authen +'/'+ stream[1] + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+query  
        elif 'static.bro.adca.st' in query:
            feed = re.compile('id=[\'"](.*?)[\'"]; width=[\'"](.*?)[\'"]; height=[\'"](.*?)[\'"];').findall(data)
            src2='http://ebookterritory.pw/stream.php?id=%s&width=%s&height=%s&stretching=uniform'%feed[0]
            header = {'User-Agent':UA,
                     'Referer': src,
                     }
            decoded = getUrl(src2,header=header)
            #TODO to be completed ... not working source
        elif 'castto.me' in query:
            #http://cdn.castto.me/live/ytFxxJz6QsclKSqoYuUX/playlist.m3u8
            feed = re.compile('fid="(.*?)"; v_width=(.*?); v_height=(.*?);').findall(data)
            src2='http://static.castto.me/embedlivepeer5.php?channel=%s&vw=%s&vh=%s'%feed[0]
            header = {'User-Agent':UA,
                     'Referer': src,
                     'Host':'static.castto.me',
                     }
            decoded = getUrl(src2,header=header)
            file   = re.compile('file[: ]*["\'](.*?)[\'"]').findall(decoded)
            if file:
                vido_url = file[0]
        elif 'cast4u' in query:
            #rtmp://94.102.56.215/live?wmsAuthSign=c2VydmVyX3RpbWU9NS8xNC8yMDE2IDEyOjI0OjUwIEFNJmhhc2hfdmFsdWU9MGtpQm85UmU1b0FjL1pMRU01b25MUT09JnZhbGlkbWludXRlcz0xMA==/<playpath>9tFngX8N5UWBclZMH1 <swfUrl>http://cast4u.tv/jwplayer/jwplayer.flash.swf <pageUrl>http://www.cast4u.tv/embedcr.php?live=skys1&vw=620&vh=490
            #rtmp://80.82.78.22/live?wmsAuthSign=c2VydmVyX3RpbWU9NS8xNC8yMDE2IDEyOjMxOjEyIEFNJmhhc2hfdmFsdWU9RnJoQUZZa0JFME1lSzNrQlFnZ0FTZz09JnZhbGlkbWludXRlcz0xMA==/<playpath>9tFngX8N5UWBclZMH1 <swfUrl>http://cnZ0FTZz09JnZhbGlkbWludXRlcz0xMA==/ <pageUrl>
            swfUrl='http://cast4u.tv/jwplayer/jwplayer.flash.swf'
            decoded = getUrl(query)
            # find url function names:
            fnames = re.compile('file: (.*?)\(\) \+ \'/\' \+ (.*?)\(\)').findall(decoded)
            #token = re.search('securetoken: (.*?)\n',decoded)
            token = re.search('jwplayer.key="(.*?)"',decoded)
            if fnames:
                fnames=fnames[0]
                stream=[]
                authen=''
                for fname in fnames:
                    idx1 = decoded.find('function '+fname)
                    idx2 = decoded[idx1:].find('}')
                    tmp = decoded[idx1:idx1+idx2]
                    s=re.search('(\[.*?\])',tmp).group(1)
                    stream.append(''.join(eval(s)).replace('\\',''))
                    # look for auth code
                    cod=re.search('join\(\"\"\) \+ (.*?).join\(\"\"\)',tmp)
                    if cod and authen=='':
                       authen = re.search(cod.group(1)+' = (\[.*?\])',decoded).group(1)
                       authen = ''.join(eval(authen))
                    
                vido_url = stream[0] + authen +'/'+ stream[1] + ' swfUrl='+swfUrl  + ' swfVfy=1 live=1 timeout=13 pageUrl='+query
                # if token:
                #     vido_url += ' token=play@' + token.group(1)
        elif 'openlive.org' in query:
            #rtmp://89.33.8.14/live?token=fQiiu2FsiZ1_0qn8Vg-9BQExpired=1463224405<playpath>ver0f5301f0cbb71177de0d25 <swfUrl>http://p.jwpcdn.com/6/12/jwplayer.flash.swf <pageUrl>http://openlive.org/embed.php?file=gdfgjhgkjgbg&width=640&height=480
            feed = re.compile('file=["\'](.*?)["\']; width=["\'](.*?)["\']; height=["\'](.*?)["\'];').findall(data)
            src2 = 'http://openlive.org/embed.php?file=%s&width=%s&height=%s'%feed[0]
            header = {'User-Agent':UA,
                     'Referer': src,
                     'Host':'openlive.org',
                     'Upgrade-Insecure-Requests':'1'}
            decoded = getUrl(src2,header=header)
            stream = re.compile('\'streamer\'[:, ]*\'(.*?)\'').findall(decoded)
            file   = re.compile('\'file\'[:, ]*\'(.*?)\'').findall(decoded)
            swfUrl='http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            #'http://openlive.org/embed.php?file=gdfgjhgkjgbg&width=640&height=480'
            if swfUrl and stream and file:
                vido_url = stream[0] +' playpath='+file[0] + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+src2
        elif 'tvope' in query:
            #rtmp://play5.tvope.com/tvope<playpath>stream_tvn24 <swfUrl>http://i.tvope.com/swf/player5.4.swf <pageUrl>http://tvope.com/emb/player.php?c=tvn24&w=640&h=480&jw&d=match-sport.com
            feed = re.compile('c="(.*?)"; w=(.*?); h=(.*?);').findall(data)
            query = 'http://tvope.com/emb/player.php?c=%s&w=%s&h=%s&jw&d=match-sport.com'%feed[0]
            header = {'User-Agent':UA,
                     'Referer': src,
                     'Host':'tvope.com'}
            decoded = getUrl(query,header=header)
            swfUrl = re.compile('SWFObject\(\'(.*?)\'').findall(decoded)
            stream = re.compile('\'streamer\',\'(.*?)\'\);').findall(decoded)
            file   = re.compile('\'file\',\'(.*?)\'\);').findall(decoded)
            if swfUrl and stream and file:
                vido_url = stream[0] +' playpath='+file[0] + ' swfUrl='+swfUrl[0] + ' swfVfy=1 live=1 timeout=13  pageUrl='+query
        elif 'scity' in query:
            #http://edge1.scity.tv/livehls/5FvAhDXNNcAc/chunklist_w121662231.m3u8?token=TK5e5N78FF_YfP6j6-HRvg&expire=1463168460
            feed = re.compile('fid="(.*?)"; v_width=(.*?); v_height=(.*?);').findall(data)
            query = 'http://www.scity.tv/keycdn.php?channel=%s&vw=%s&vh=%s'%feed[0]
            header = {'User-Agent':UA,
                     'Referer': query}
            url2='http://www.scity.tv/tk.php?id=%s'%feed[0][0]
            decoded = getUrl(url2,header=header)
            rtmp = re.compile('"rtmp":"(.*?)"').findall(decoded)
            if rtmp:
                vido_url=rtmp[0] + ' live=1 timeout=13'
        elif 'dotstream' in query or 'privatestream' in query:
            if 'dotstream' in query:
                query = query.replace('/pl?','/player.php?')
                header = {'User-Agent':UA,
                        'Referer': src}
                decoded = getUrl(query,header=header)
                swfUrl='http://dotstream.tv/jwp/jwplayer.flash.swf'
            elif 'privatestream' in query:
                decoded = getUrl(query)
                src2=re.compile('"(http://privatestream.tv/.*?)"').findall(decoded)
                decoded = getUrl(src2[0])   
                swfUrl='http://privatestream.tv/js/jwplayer.flash.swf'
 
            a=int(re.search('a = ([0-9]+)',decoded).group(1))
            b=int(re.search('b = ([0-9]+)',decoded).group(1))
            c=int(re.search('c = ([0-9]+)',decoded).group(1))
            d=int(re.search('d = ([0-9]+)',decoded).group(1))
            f=int(re.search('f = ([0-9]+)',decoded).group(1))
            v_part = re.search('v_part = \'(.*?)\';',decoded).group(1)
            link = 'rtmp://%d.%d.%d.%d/'%(a/f,b/f,c/f,d/f) + v_part.split('/')[1]+'/'+' playpath='+v_part.split('/')[-1]

            vido_url = link + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+query
        else:
            print 'UNKNOWN',query
    return vido_url

def decode_all_urls(out,):
    out_hrefs=[]    
    for one in out:
        print '\n',one.get('title'),': ',one.get('url','')
        vido_url = decode_url(one.get('url',''))
        if vido_url:
            print'\t',vido_url
            one['url']=vido_url
            out_hrefs.append(one) 
    return out_hrefs
##    
#rtmp://31.220.40.59/live/<playpath>matchsport?keys=WSMzC8WXuU1ZsGhrlV1f0w&keyt=1463175649 <swfUrl>http://dotstream.tv/jwp/jwplayer.flash.swf <pageUrl>http://dotstream.tv/player.php?streampage=matchsport&height=480&width=640
#rtmp://31.220.0.201/live/<playpath>polsat?keys=UwqDKBgQMRVXaILNcrUJXQ&keyt=1463175722 <swfUrl>http://dotstream.tv/jwp/jwplayer.flash.swf <pageUrl>http://dotstream.tv/player.php?streampage=polsat&height=480&width=640

# out=get_root()    
# out2=decode_all_urls(out[:])
# for one in out:
#     url=one.get('url')
#     print url
# url=out[0].get('url')
# decode_url(url)