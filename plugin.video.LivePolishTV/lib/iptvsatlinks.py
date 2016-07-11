# -*- coding: utf-8 -*-
import urllib2,urllib
import re
import urlparse


def getUrl(url,data=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    try:
        response = urllib2.urlopen(req, timeout=10)
        link = response.read()
        response.close()
    except:
        link=''
    return link

def get_playlist():
    url='http://iptvsatlinks.blogspot.be/search/label/m3u%20playlists'
    content = getUrl(url)
    h3 = re.compile('<h3(.*?)</h3>',re.DOTALL).findall(content)
    out=[]
    for i,item in enumerate(h3):
        href_title = re.compile('href=[\'"](.*?)[\'"]>(.*?)<').findall(item)
        if href_title:
            ht=href_title[0]
            # out.append({'title':href_title[0][1],'url':href_title[0][0]})
            #out = get_m3u_servers(href_title[0][0])
            out_temp = get_m3u_servers(ht[0])
            if out_temp:
                out.append({'title':'[COLOR blue]'+ht[1]+'[/COLOR]','url':''})
                out.extend(out_temp)
        if i>1:
            break
    return out

def get_m3u_servers(url):
    content = getUrl(url)
    m3u=re.compile('<div class="code">(.*?)</div>',re.DOTALL).findall(content)
    out=[]
    if m3u:
        m3ul=re.compile('(http[^<]*)').findall(m3u[0])
        for i,link in enumerate(m3ul):
            title = '(server %d) %s'%(i+1,urlparse.urlparse(link).netloc.split(':')[0])
            href = link.replace('&amp;','&')
            out.append({'title':title,'url':href})
    return out

# out=get_playlist()
# url=out[3]['url']
def m3u2list(url):
    m3u_content = getUrl(url)
    out = []
    matches=re.compile('^#EXTINF:-?[0-9]*(.*?),(.*?)\n(.*?)$',re.I+re.M+re.U+re.S).findall(m3u_content)
    
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
        out.append(one)
  
    return out