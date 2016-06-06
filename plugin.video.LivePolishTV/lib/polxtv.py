# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import mydecode


BASEURL='http://pol-xtv.blogspot.com'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

fix={}


def fixForEPG(one):
    newName = fix.get(one.get('tvid'),'')
    if newName:
        one['title']=newName
        one['tvid']=newName
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
    content = getUrl(BASEURL)
    out=[]
    groups=re.compile("""a href=\'(.*?)\' target=''><img height='50' src='(.*?)' title='(.*?)' width='70'/></a>""").findall(content)
    for href,img,title in groups:
        t = title
        i = img
        h = href
        t = t.title()
        for s in ['TV','TVN','MTV','TVP','BIS','TVR','TVS','HBO','BBC','AXN','ATM','AMC','HD','TLC','ID','XD','TVT','CBS']:
            t = re.sub("((?i)"+s+")",s.upper(), t)
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':''}))
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (cinema-tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})
    return out
# url='http://pol-xtv.blogspot.com/p/tvp-hd.html'
# url='http://pol-xtv.blogspot.com/p/tvn.html'
def decode_url(url='http://pol-xtv.blogspot.com/p/comedy-central.html'):
    vido_url=''
    
    content = getUrl(url)
    idx1 = content.find('<div id=\'summary')
    idx2 = content[idx1:].find('createSummaryAndThumb("summary')
    data=content[idx1:idx1+idx2]
    if data.find('document.write(unescape(')>-1:
        s_hex = re.compile('unescape\(\'(.*?)\'\)').findall(data)
        data = s_hex[0].replace('%','').decode('hex')
    vido_url = mydecode.decode(url,data)
    return vido_url      
##    
# out=get_root()
# for o in out:
#     print o['title']
#     print decode_url( o['url']),'\n'