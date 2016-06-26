# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time,json

BASEURL='http://wizja.tv/'
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
    url='http://wizja.tv/'
    content = getUrl(url)
    channels=re.compile('<a href="(watch.*?)"><img src="(.*?)"></a>').findall(content)
    out=[]
    if addheader:
        t='[COLOR yellow]Updated: %s (wizja.tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://wizja.tv/','group':'','urlepg':''})
    #one=match[0]
    for ch in channels:
        t = ch[1].split('/')[-1].split('.')[0].title()
        i = BASEURL + ch[1]
        h = BASEURL + ch[0]
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':''}))
    #return sorted(out, key=lambda k: k['title'],reverse=True)    
    return out
    
#rtmp://185.66.141.231:1875/haYequChasp4T3eT?event=37&token=aTL2E0ZGxyPnjVUzkiAlb1WXBQ9rg6<playpath>pHe7repheT?event=37&token=aTL2E0ZGxyPnjVUzkiAlb1WXBQ9rg6 <swfUrl>http://wizja.tv/player/StrobeMediaPlayback_v2.swf <pageUrl>http://wizja.tv/player.php?target=ams_nl1&ch=37
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
    


def decode_url(url='http://wizja.tv/watch.php?id=47'):
    vido_url=''
    if 'wizja.tv' in url:
        
        id = re.search('id=(.*?)$',url).group(1)
        
        posterurl='http://wizja.tv/porter.php?ch=%s'%id
        playerulr='http://wizja.tv/player.php?target=ams_nl2&ch=%s'%id
        
        header={
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                'Host':'wizja.tv',
                'Referer':url,
                'Cache-Control':'max-age=0',
                "Connection":"keep-alive",
                'Upgrade-Insecure-Requests':'1',
                }

        c=get_Cookies(url,header=header)
        
        cookie=' '.join(['%s;'%get_cookie_value(c,s) for s in ['__cfduid','PHPSESSID']])
        header['Cookie']=cookie
        data = getUrl(posterurl,header=header)

        mylink = re.compile('src: "(.*?)"').findall(data)
        if len(mylink)>0:
            rtmp2 = urllib.unquote(mylink[0]).decode('utf8')
            rtmp1 = re.compile('rtmp://(.*?)/(.*?)/(.*?)\?(.*?)\&streamType').findall(rtmp2)
            vido_url = 'rtmp://' + rtmp1[0][0] + '/' + rtmp1[0][1] +'/' +rtmp1[0][2]+ '?'+ rtmp1[0][3]+ ' app=' + rtmp1[0][1] + '?' +rtmp1[0][3]+' swfVfy=1 flashver=WIN\\2020,0,0,306 timeout=10 swfUrl=http://wizja.tv/player/StrobeMediaPlayback.swf live=true pageUrl='+url

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

def build_m3u(out,fname='wizjatv.m3u'):    
    entry='#EXTINF:-1 tvg-id="{tvid}" tvg-logo="{img}" url-epg="{urlepg}" group-title="{group}",{title}\n{url}\n\n'
    OUTxmu='#EXTM3U\n'
    #OUTxmu=OUTxmu+'\n#EXTINF:-1, [COLOR yellow]Update: %s [/COLOR]\nhttp://www.youtube.com/\n\n' %(time.strftime("%d/%m/%Y: %H:%M:%S"))
    for one in out:
        OUTxmu=OUTxmu+entry.format(**one)
    myfile = open(fname,'w')
    myfile.write(OUTxmu)
    myfile.close()

def build_json(out,fname=r'wizjatv.json'):
    with open(fname, 'w') as outfile:
        json.dump(out, outfile, indent=2, sort_keys=True)

# def ReadJsonFile(jfilename):
#     content = '[]'
#     if jfilename.startswith('http'):
#         content = getUrl(jfilename)
#         data=json.loads(content)
#     return data
# def get_root(addheader=False):
#     return ReadJsonFile('https://drive.google.com/uc?export=download&id=0B0PmlVIxygktOW56RHdqeTd2X00')
#     
# def decode_url(url):
#     print url
#     return url            
##
# out = get_root()
# out2 = decode_all_urls(out)