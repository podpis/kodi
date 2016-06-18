# -*- coding: utf-8 -*-
import urllib2,urllib
import re
import time
import sys,os
import json
import cookielib
     

BASEURL='https://looknij.in/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
TIMEOUT = '10'

COOKIEFILE=r''

fix={
'Canal Film':'Canal+ Film',
'Canal Sport HD':'Canal+ Sport',
'HBOHD':'HBO',
'Minimini HD':'Minimini+',
'Polsat2HD':'Polsat 2',
'NsportHD':"nSport",
'TLC Polska HD':"TLC",
'Discovery Channel Historia':"Discovery Historia",
'TVPHD':'TVP HD',
'Natgeo Wild HD':"Nat Geo Wild",
'TVP2HD':'TVP 2',
'TVP1HD':'TVP 1',
}

def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
    return one


# def _getUrl(url,data=None,cj=None, cookies=None,useCookies=True):
#     if COOKIEFILE and os.path.isfile(COOKIEFILE) and not cj:
#         cj = cookielib.LWPCookieJar()
#         cj.load(COOKIEFILE)
#     opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),urllib2.HTTPSHandler(),urllib2.HTTPHandler(),urllib2.HTTPBasicAuthHandler())
#     urllib2.install_opener(opener)
# 
#     opener = urllib2.install_opener(opener)
#     req = urllib2.Request(url)
#     req.add_header('User-Agent', UA)
#     if cookies:
#         req.add_header("cookie", cookies)
#     try:
#         
#         response = urllib2.urlopen(req,timeout=TIMEOUT)
#         link = response.read()
#         response.close()
#     except urllib2.HTTPError as e:
#         link= e.read()
#         #link=''
#     return link

url = 'https://looknij.in/tv-online/strona[1]'
def getUrl(url,data=None):
    # cookies=cookieString(COOKIEFILE)
    # content=_getUrl(url=url,post=data,cookies=cookies)
    # if not content:
    cj = cf_setCookies(url,COOKIEFILE)
    cookies =''.join(['%s=%s;'%(c.name, c.value) for c in cj])
    #cookies=cookieString(COOKIEFILE)
    
    content=_getUrl(url,data,cj,cookies)
    return content
    
cfile=COOKIEFILE

def cf_setCookies(url,cfile):
    cj = cookielib.LWPCookieJar()
    cj = createCookie(url,cj,UA)
    dataPath=os.path.dirname(cfile)
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)
    if cj:
        cj.save(cfile) 
    return cj

def _getUrl(url, cookieJar=None,post=None,cookies=None, headers=None):
    if not cookieJar:
        cookieJar=cookielib.LWPCookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
    opener = urllib2.build_opener(cookie_handler, urllib2.HTTPSHandler()) #, urllib2.HTTPHandler()
    opener = urllib2.install_opener(opener)
    req = urllib2.Request(url)
    req.add_header('User-Agent',UA)
    # headers=[
    #     ('accept','*/*'),
    #     ('cache-control','max-age=0'),
    #     ('upgrade-insecure-requests','0')
    #     ]
    if headers:
        for h,hv in headers:
            req.add_header(h,hv)
    if cookies:
        req.add_header("cookie", cookies)
    try:
        response = urllib2.urlopen(req, timeout=10)
        link = response.read()
        response.close()
    except urllib2.HTTPError as e:
        #link= e.read()
        link=''

    return link    


def getUrl(url,data=None,header={},cookies=None):
    if not header:
        header = {'User-Agent':UA,
            'pragma':'no-cache',
            'upgrade-insecure-requests':'1',
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            "SOAPAction" : "",
        }
    req = urllib2.Request(url,data,headers=header)

    try:
        response = urllib2.urlopen(req, timeout=10)
        if cookies=='':
            cookies=response.info()['Set-Cookie']
        link = response.read()
        response.close()
    except:
        link=''
    return link    
    

def get_root(addheader=False):
    out=[]
    next_page = 1
 
    # cj = createCookie('https://looknij.in/',cj=cj,agent=UA)
    # #getUrl('https://looknij.in/',cj)
    #while next_page:
    for next_page in range(3):
        print 'page',next_page
        next_page+=1
        tmp_out,next_page = get_page(page=next_page)
        print 'channels#',len(tmp_out)
        out.extend(tmp_out)
    len(out)
    if len(out)>0 and addheader:
        t='[COLOR yellow]Updated: %s (yoy.tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':'http://yoy.tv/','group':'','urlepg':''})
    return out
    
def get_page(page=1):
    url = 'https://looknij.in/tv-online/strona[%d]+'%(page)
    print url
    content = getUrl(url)
    out=[]
    hrefs = re.compile('<h3 class.*?<a href="(.*?)">(.*?)</a>').findall(content)
    imgs = re.compile('<a href="(.*?)"><img src="(.*?)"').findall(content)
    print 'hrefs',len(hrefs)
    print 'imgs',len(imgs)
    for im,href in zip(imgs,hrefs):
        group=''
        t=href[-1].split('[')[0].strip()
        i=im[-1]
        h=BASEURL[:-1]+im[0]
        t = t.title()
        for s in ['TV','TVN','MTV','TVP','BIS','TVR','TVS','HBO','BBC','AXN','ATM','AMC','HD','TLC','ID','XD','TVT','CBS']:
            t = re.sub("((?i)"+s+")",s.upper(), t) #,flags=re.IGNORECASE
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':group,'urlepg':''}))
    
    # pagination
    url_next = r'https://looknij.in/tv-online/strona[%d]+'%(page+1)
    idx=content.find(url_next)
    next_page = page+1 if idx>-1 else None
    return out,next_page

#url='https://looknij.in/tv-tvp1hd-lektor-10'
def decode_url(url):
    # cookieJar = cookielib.MozillaCookieJar()
    # rtmp://live.looknij.in/live/<playpath>FILMBOX <swfUrl>https://looknij.in/views/js/jwplayer.flash.swf <pageUrl>https://looknij.in//tv-filmbox-extra-lektor-20
    # rtmp://live.looknij.in/live/<playpath>WILDTV?token=69e26d6dcc80e355c2cfe7cc12b6c834 <swfUrl>https://looknij.in/views/js/jwplayer.flash.swf <pageUrl>https://looknij.in/tv-natgeo-wild-hd-lektor-31

    vido_url=''
    if 'looknij.in' in url:
        content = getUrl(url)
        swfUrl='https://looknij.in/views/js/jwplayer.flash.swf'
        flash = re.compile('post\([\'"](.*?)["\']').findall(content)
        if flash:
            data = getUrl(BASEURL+flash[0])
            data = getUrl(BASEURL+flash[-1])
            rtmp = re.search('"(rtmp:.*?)"',data)
            if rtmp:
                rtmp = rtmp.group(1).replace('\\','')
                vido_url = rtmp.strip() +' swfUrl='+swfUrl+' swfVfy=1 live=1 timeout='+TIMEOUT+' pageUrl='+url
    return vido_url    

##

def createCookie(url,cj,agent=UA):
    urlData=''
    try:
        class NoRedirection(urllib2.HTTPErrorProcessor):    
            def http_response(self, request, response):
                return response

        def parseJSString(s):
            try:
                offset=1 if s[0]=='+' else 0
                val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
                return val
            except:
                pass

        if cj==None:
            cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', agent)]
        try:
            response = opener.open(url)
            result=urlData = response.read()
            response.close()
        except urllib2.HTTPError as e:
            result=urlData = e.read()

            cookie =''.join(['%s=%s;'%(c.name, c.value) for c in cj])

            opener = urllib2.build_opener(NoRedirection,urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-Agent', agent)]
            opener.addheaders.append(('cookie',cookie))
            try:
                response = opener.open(query)
                response.close()
            except urllib2.HTTPError as e:
                response = e.read()
        
        return cj
    except:
        return None

def cookieString(COOKIEFILE):
    sc=''
    if os.path.isfile(COOKIEFILE):
        cj = cookielib.LWPCookieJar()
        cj.load(COOKIEFILE)
        for c in cj:
            sc+='%s=%s;'%(c.name, c.value)
    return sc

def ReadJsonFile(jfilename):
    content = '[]'
    if jfilename.startswith('http'):
        content = getUrl(jfilename)
        data=json.loads(content)
    return data
def get_root(addheader=False):
    return ReadJsonFile('https://drive.google.com/uc?export=download&id=0B0PmlVIxygktYkh5Tk5XaHNoSkk')
def decode_url(url):
    return url.replace(' swfUrl','?token=69e26d6dcc80e355c2cfe7cc12b6c834 swfUrl')
       
##    
# out=get_root(addheader=False)
# for o in out:
#     url= o.get('url')
#     print url
#     o['url']=decode_url(o.get('url'))
#     print o['url']
# with open('looknij.json', 'w') as outfile:
#     json.dump(out, outfile, indent=2, sort_keys=True)