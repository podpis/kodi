# -*- coding: utf-8 -*-
import urllib2,urllib
import re,json
import urlparse

BASEURL='http://www.ceskatelevize.cz'
def getUrl(url,data={},headers={}):
    if headers:
        my_header=headers
    else:
        my_header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'}
    req = urllib2.Request(url,urllib.urlencode(data),my_header)
    try:
        response = urllib2.urlopen(req,timeout=10)
        link =  response.read()
        response.close()
    except:
        link=''
    return link
    
def get_root(url=BASEURL):
    content = getUrl(url)    
    out=[]
    onairs = re.compile('<div class="panel-onair(.*?)</div>[\n\t ]*</div>',re.DOTALL).findall(content)
    for live in onairs:
        #live=onairs[0]
        href = re.compile('<a href=".*?" onclick="delayUAEvent\(this, {\'event\':\'Homepage.live\',\'eAction\':\'(.*?)\',').findall(live)
        img = re.compile('src="(.*?)"').findall(live)
        title  = re.compile('alt="(.*?)"').findall(live)
        title2 = re.compile('<span class="s_130p">(.*?)</span>').findall(live)
        if href and title:
            href = href[0]
            img = img[0] if img else ''
            title = title[0].strip()
            if title2:
                title +=' [COLOR lightblue]%s[/COLOR]'%title2[0].strip()
            out.append({'title':title,'url':href,'img':img})
    return out

# url='/ivysilani/10090925908-vsechnoparty/216522161600027/'
#url='/ct24/zive-vysilani/'
def getVideo2(url):
    myurl = url
    video_url={'msg':'','url':''}
    if url.startswith('/'):
        myurl = BASEURL+myurl
    content = getUrl(myurl) 
    idtype = re.search('getPlaylistUrl\(\[{"type":"(.*?)","id":"(.*?)"}\]',content)
    if idtype:
        print idtype.group(2),idtype.group(1),url
        video_url =getstream( idtype.group(2),idtype.group(1),url)
    return video_url

def test():
    out = get_root()
    for one in out:
        url=one.get('url')
        print url
        getVideo(one.get('url'))
        
def getVideo(ch='ct24'):
    channels={'ct1':'1','ct2':'2','ct24':'24','sport':'4','D':'5','art':'6'}
    video_url={'msg':'','url':''}
    if ch in channels.keys():
        print 'czeskatv',channels[ch]
        url='http://www.ceskatelevize.cz/ivysilani/ajax/get-client-playlist'
        rurl='/ivysilani/embed/iFramePlayerCT24.php'
        header={ 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36','x-addr': '127.0.0.1',}
        post_data = {'playlist[0][id]': channels[ch],'playlist[0][type]': "channel",'requestUrl': rurl,'requestSource': "iVysilani",'addCommercials': 0,'type': "html"}
        content = getUrl(url, post_data, headers=header)
        tmpurl=json.loads(content).get('url')
        if tmpurl.startswith('http'):
            data = getUrl(tmpurl)
            if data:
                data = json.loads(data)
                src=data['playlist'][0]['streamUrls']['main']
                m3u=getUrl(src)
                bw=re.compile('(BANDWIDTH=.*?)\n(.*?)\n').findall(m3u)
                video_url['url'] = bw
        else:
            video_url['msg'] = tmpurl
    else:
        video_url['msg']='Unknown channel [%s]'%ch
    return video_url

def getstream(chid='ct24',chtype='channel',churl='/ivysilani/embed/iFramePlayerCT24.php'):
    video_url={'msg':'','url':''}
    url='http://www.ceskatelevize.cz/ivysilani/ajax/get-client-playlist'
    header={ 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36','x-addr': '127.0.0.1',}
    post_data = {'playlist[0][id]': chid,'playlist[0][type]': chtype,'requestUrl': churl,'requestSource': "iVysilani",'addCommercials': 0,'type': "html"}
    content = getUrl(url, post_data, headers=header)
    tmpurl=json.loads(content).get('url')
    if tmpurl.startswith('http'):
        data = getUrl(tmpurl)
        if data:
            data = json.loads(data)
            src=data['playlist'][0]['streamUrls']['main']
            m3u=getUrl(src)
            bw=re.compile('(BANDWIDTH=.*?)\n(.*?)\n').findall(m3u)
            video_url['url'] = bw
    else:
        video_url['msg'] = tmpurl

    return video_url
    



