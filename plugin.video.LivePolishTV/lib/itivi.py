# -*- coding: utf-8 -*-

import re
import urllib2,urllib
import base64
import time

UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

# rtmp://app.itivi.pl/live/<playpath>TVP1HD <swfUrl>http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf <pageUrl>http://itivi.pl/program-telewizyjny/TVP_1_HD
# rtmp://app.itivi.pl/live/<playpath>TVP2HD <swfUrl>http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf <pageUrl>http://itivi.pl/program-telewizyjny/TVP_2
# rtmp://app.itivi.pl/live/<playpath>NATGEOHD <swfUrl>http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf <pageUrl>http://itivi.pl/program-telewizyjny/NATGEO_PL
# rtmp://app.itivi.pl/live/<playpath>SPORTHD <swfUrl>http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf <pageUrl>http://itivi.pl/program-telewizyjny/CANAL_SPORT
# rtmp://app.itivi.pl/live/<playpath>AXNHD <swfUrl>http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf <pageUrl>http://itivi.pl/program-telewizyjny/Axn_HD
# rtmp://app.itivi.pl/live/<playpath>DISCOVERYHD <swfUrl>http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf <pageUrl>http://itivi.pl/program-telewizyjny/Discovery_Channel


def fixForEPG(one):
    return one

def ReadJsonFile(jfilename):
    content = '[]'
    if os.path.exists(jfilename):    # local content
        with open(jfilename,'r') as f:
            content = f.read()
            if not content:
                content ='[]'
    data=json.loads(html_entity_decode(content))
    return data
    
def pPath(url):
    m=url.split('/')[-1]
    d={
    'TVP_1_HD':'TVP1HD',
    'TVP_2':'TVP2HD',
    'NATGEO_PL':'NATGEOHD',
    'CANAL_SPORT':'SPORTHD',
    'Axn_HD':'AXNHD',
    'Discovery_Channel':'DISCOVERYHD',}
    return d.get(m,'')
    
def getUrl(url,data=None,header={},cookies=None):
    if not header:
        header = {'User-Agent':UA}
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
    url='http://itivi.pl/'
    content = getUrl(url)

    match=re.compile('<a href="(.*?)"><img alt="(.*?)" src="(.*?)" style').findall(content)
   
    out=[]
    if addheader and match:
        t='[COLOR yellow]Updated: %s (itivi)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://itivi.pl/','group':'','urlepg':''})
    #m=match[0]
    for m in match:
        h = m[0]
        t = m[1].replace('Telewizja online - ','').replace('_',' ')
        i = m[2]
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':''}))
    return out

def get_root_old(addheader=False):
    return m3u2list()

def m3u2list():
    url = 'https://drive.google.com/uc?export=download&id=0B0PmlVIxygktN2FXaXYwWnNzcGc'
    
    response = getUrl(url)
    out = []
    matches=re.compile('^#EXTINF:-?[0-9]*(.*?),(.*?)\n(.*?)$',re.I+re.M+re.U+re.S).findall(response)
    
    renTags={'tvg-id':'tvid',
             'audio-track':'audio-track',
             'group-title':'group',
             'tvg-logo':'img'}
                 
    for params, title, url in matches:
        one  = {"title": title, "url": url}
        match_params =re.compile(' (.+?)="(.*?)"',re.I+re.M+re.U+re.S).findall(params)
        for field, value in match_params:
            one[renTags.get(field.strip().lower(),'bad')] = value.strip()
        if not one.get('tvid'):
            one['tvid']=title
       
        one['urlepg']=''
        one['url']=one['url'].strip()
        one['title']=one['title'].strip()
        one = fixForEPG(one)
        out.append(one)
  
    return out
       
#url='http://itivi.pl/program-telewizyjny/Discovery_Channel'    
# def decode_url(url):
#     vido_urls=''
#     data = ReadJsonFile('itivi.json')
    
    
def decode_url_old(url):
    vido_urls=''
    swfUrl='http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf'
    #rtmp://app.itivi.pl/live/<playpath>DISCOVERYHD <swfUrl>http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf <pageUrl>http://itivi.pl/program-telewizyjny/Discovery_Channel
    if 'itivi.pl' in url: 
        playpath = pPath(url)
        if playpath:
            vido_urls = 'rtmp://app.itivi.pl/live/ playpath='+ playpath + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+url
        # content = getUrl(url)
        # swfUrl='http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf'
        # link = re.compile('{file: \'(.*?)\'').findall(content)    #link=['rtmp://app.itivi.pl/live/ playpath=TVP1HD']
        # if link:
        #     vido_urls = link[0] + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+url
    return vido_urls

# url='http://itivi.pl/program-telewizyjny/TVP_1_HD'
# url='http://itivi.pl/program-telewizyjny/Fenix'
def decode_url(url):
    vido_urls=''
    #rtmp://app.itivi.pl/live/<playpath>DISCOVERYHD <swfUrl>http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf <pageUrl>http://itivi.pl/program-telewizyjny/Discovery_Channel
    if 'itivi.pl' in url: 
        content = getUrl(url)
        swfUrl='http://itivi.pl/js/jwplayer-7.0.3/jwplayer.flash.swf'
        link = re.compile('{file: \'(.*?)\'').findall(content)    #link=['rtmp://app.itivi.pl/live/ playpath=TVP1HD']
        if link:
            if link[0].startswith('http'):
                vido_urls = link[0]
            else:
                vido_urls = link[0] + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+url
    print '###itivi.pl',vido_urls
    return vido_urls 
    
def decode_all_urls(out,):
    out_hrefs=[]   
    out_d = {} 
    for one in out:
        #print one.get('title')
        print one.get('url','')
        m=one.get('url','').split('/')[-1]
        vido_url = decode_url2(one.get('url',''))
        if vido_url:
            print'\t',vido_url
            one['url']=vido_url
            p =vido_url.split(' ')[0].split('/')[-1]
            out_d[m]=p
            out_hrefs.append(one) 
    
    return out_hrefs     
    
def build_m3u(out,fname=r'D:\itivi.m3u'):    
    entry='#EXTINF:-1 tvg-id="{tvid}" tvg-logo="{img}" url-epg="{urlepg}" group-title="{group}",{title}\n{url}\n\n'
    OUTxmu='#EXTM3U\n'
    #OUTxmu=OUTxmu+'\n#EXTINF:-1, [COLOR yellow]Update: %s [/COLOR]\nhttp://www.youtube.com/\n\n' %(time.strftime("%d/%m/%Y: %H:%M:%S"))
    for one in out:
        one['title']=one['title'].strip()
        if not one.has_key('img'):
            one['img']=''
        if not one.has_key('group'):
            one['group']=''
        OUTxmu=OUTxmu+entry.format(**one)
    myfile = open(fname,'w')
    myfile.write(OUTxmu)
    myfile.close()

    
##
# out=get_root_old()    
# out2=decode_all_urls(out)

# for h in out_hrefs:
#     l= h.get('url').split(' ')[0]
#     if 'itivi' in l:
#         print l
#         
#         
# for o in out:
#     print o.get('img')
#     if o.get('url').startswith('http'):
#         o['url']=o.get('url').split(' ')[0]
# import json
# 
# with open(r'D:\itivi.json', 'w') as outfile:
#     json.dump(out, outfile, indent=2, sort_keys=True)
