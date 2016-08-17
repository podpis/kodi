# -*- coding: utf-8 -*-

import urllib2,urllib
import re

BASEURL='http://psa-tv.blogspot.com/'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

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
    content = getUrl(BASEURL)
    out=[]
    s_hex = re.compile('document.write\(unescape\(\'(.*?)\'\)').findall(content)
    if s_hex:
        data = s_hex[0].replace('%','').decode('hex')
        option=re.compile('<option value="(.*?)">(.*?)</option>').findall(data)
        for href,title in option:
            h = href
            t = title.strip()
            if h and t:
                out.append({'title':t,'tvid':t,'img':'','url':h,'group':'','urlepg':''})
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (cinema-tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})
    return out

def decode_url(url=''):
    vido_url=url
    return vido_url      