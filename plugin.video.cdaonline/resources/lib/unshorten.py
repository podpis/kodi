# -*- coding: utf-8 -*-
import re
import time
import json
import urllib2


_headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36'}
_timeout = 10

def getUrl(url,data={},headers={}):
    req = urllib2.Request(url,json.dumps(data),headers=headers)
    try:
        response = urllib2.urlopen(req, timeout=10)
        link = response.read()
        response.close()
    except:
        link=''
    return link


def unshorten(url):
    if 'sh.st/' in url:
        url = _unshorten_shst(url)
    elif 'safelinking.net' in url:
        url = _safelinking(url)
    return url

#url = 'https://safelinking.net/p/FpEBxtg'
def _safelinking(url):
    hash = url.split('/')[-1]
    post_data = {'hash': hash}
    headers = { "Accept": "application/json, text/plain, */*",
                "Content-Type": 'application/json'}
    response = getUrl('http://safelinking.net/v1/protected',data=post_data,headers=headers)
    jr = json.loads( response)   
    if jr:
        links=jr.get('links',[])
        if len(links):
            url=links[0].get('url','')
    return url
    
#uri='http://sh.st/Pm6Vf'
def _unshorten_shst(uri):
    urlo=''
    html = getUrl(uri, headers=_headers)
    session_id = re.findall(r'sessionId\:(.*?)\"\,', html)
    if len(session_id) > 0:
        session_id = re.sub(r'\s\"', '', session_id[0])

        http_header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.46 Safari/535.11",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "en-US,en;,q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "sh.st",
            "Referer": uri,
            "Origin": "http://sh.st",
            "X-Requested-With": "XMLHttpRequest"
        }

        time.sleep(5)

        urle = 'http://sh.st/shortest-url/end-adsession?adSessionId=%s&adbd=1&callback=c'%session_id
        response = getUrl(urle, headers=http_header)
        
        urlo=re.search('"destinationUrl":"(.*?)"',response)
        if urlo:
            urlo=urlo.group(1).replace('\\','')

    return urlo
