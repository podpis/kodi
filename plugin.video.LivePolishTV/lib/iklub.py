# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
try:
    import execjs
except:
    import js2py


def fixForEPG(one):
    return one
    
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
    
def get_root(addheader=False):
    url='http://iklub.net/all/'
    content = getUrl(url)
    idx1=content.find('class="entry-content"')
    idx2=content[idx1:].find('.entry-content')
    content = content[idx1:idx1+idx2]    
    #match=re.compile('<a href="(http://iklub.net/.*?)"><img alt="(.*?)" src="(.*?)" style').findall(content)
    
    href=re.compile('<a href="(http://iklub.net/.*?)"').findall(content)
    title = re.compile('alt="(.*?)"').findall(content)
    img = re.compile('src="(.*?)"').findall(content)
    # print len(title),len(href),len(img)
    out=[]
    if addheader:
        t='[COLOR yellow]Updated: %s (iklub)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.append({'title':t,'tvid':'','img':'','url':'http://iklub.net','group':'','urlepg':''})
    #one=match[0]
    for h,t,i in zip(href,title,img):
        #print h,t,i
        t = t.replace('Telewizja online - ','').replace('_',' ')
        out.append(fixForEPG({'title':t,'tvid':t,'img':i,'url':h,'group':'','urlepg':''}))
    #return sorted(out, key=lambda k: k['title'],reverse=True)    
    return out

#url='http://iklub.net/filmboxfamily'
# url='http://iklub.net/eurosport/'
url='http://iklub.net/fightbox-2/'
url='http://iklub.net/mini-2/'
def decode_url(url='http://iklub.net/tvp2/'):
    vido_urls=[]
    if 'iklub.net' in url:
        urlpl = getUrl(url)
        iframes = re.compile('<iframe(.*?)</iframe>').findall(urlpl)
        zapas = re.compile('<a href="(.*?)"><img src=".*?" alt="Zapasowy Player"').findall(urlpl)
        if zapas:
            urlpl2 = getUrl(zapas[0])
            iframe2 = re.compile('<iframe(.*?)</iframe>').findall(urlpl2)
            if iframe2: 
                iframes.extend(iframe2)
        #iframe= iframes[0]
        for iframe in iframes:
            pageUrl = re.compile('src="(.*?)"').findall(iframe)
            if pageUrl:
                content=getUrl(pageUrl[0])

                fun_hex = re.compile('eval\(unescape\(\'(.*?)\'\)\);\neval').findall(content)
                if fun_hex:
                    fun = fun_hex[0].replace('%','').decode('hex')
                    fun_name = re.search('function (.*?)\(',fun).group(1)
                    
                    code = re.search('\+ \'(.*?)\' \+',content).group(1)
                    try:
                        ctx = execjs.compile(fun)
                        decoded = ctx.call(fun_name, code)
                    except:
                        context = js2py.EvalJs() 
                        context.execute('pyimport urllib;'+fun.replace('\t','').replace('\n','').replace('unescape(','urllib.unquote(') )
                        decoded = getattr(context,fun_name)(code)
                else:
                    fun_hex = re.compile('write\(\'(.*?)\'\);').findall(content)
                    if fun_hex:
                        decoded = fun_hex[0].decode('unicode-escape')
                        
                    else:
                        decoded=''
                
                src = re.search('src="(.*?)"',decoded)
                if src:
                    src=src.group(1)
                    if src.startswith('//'): 
                        src='http:'+src
                else:
                    src=''
                
                if decoded.find('var a =')>0:
                    a=int(re.search('a = ([0-9]+)',decoded).group(1))
                    b=int(re.search('b = ([0-9]+)',decoded).group(1))
                    c=int(re.search('c = ([0-9]+)',decoded).group(1))
                    d=int(re.search('d = ([0-9]+)',decoded).group(1))
                    f=int(re.search('f = ([0-9]+)',decoded).group(1))
                    v_part = re.search('v_part = \'(.*?)\';',decoded).group(1)
                    link = 'rtmp://%d.%d.%d.%d/'%(a/f,b/f,c/f,d/f) + v_part.split('/')[1]+'/'+' playpath='+v_part.split('/')[-1]
                    swfUrl=re.compile('src="(.*?)"').findall(decoded)[-1]
                    swfUrl=swfUrl.replace('.js','.flash.swf').replace('_remote','')
                    vido_url = link + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+pageUrl[0]
                    vido_urls.append(vido_url)
                    #rtmp://31.220.0.201/privatestream/<playpath>tvvvppspportch <swfUrl>http://privatestream.tv/js/jwplayer.flash.swf <pageUrl>http://iklub.net/tvpsportl.html
                else:
                    data = getUrl(src)
                    if data:
                        idx = data.find('Initialize player')
                        if idx<0:
                            src = re.search('src="(.*?)"',data)
                            if src:
                                src=src.group(1)
                                if src.startswith('//'): 
                                    src='http:'+src
                                data = getUrl(src)
                                idx = data.find('Initialize player')
                        data = data[idx:]
                        swfUrl = re.search('"flashplayer": "(.*?)"',data)
                        if swfUrl:
                            swfUrl=swfUrl.group(1)
                            if swfUrl.startswith('//'): 
                                swfUrl='http:'+swfUrl
                        file = re.search('"file": "(.*?)",[\n\t ]+"type"',data)
                        if file:
                            file=file.group(1)
                            if file.endswith('m3u8'):
                                vido_url = file
                            else:
                                #link = file.replace('live/','live/ playpath=')
                                vido_url = file + ' swfUrl='+swfUrl + ' swfVfy=1 live=1 timeout=13 pageUrl='+pageUrl[0]
                            vido_urls.append(vido_url)
    #rtmp://212.47.226.36/live/<playpath>1 swfUrl=http://ssl.p.jwpcdn.com/player/v/7.4.2/jwplayer.flash.swf pageUrl=http://iklub.net/tvp1i.html
    #rtmp://31.220.0.201/privatestream/<playpath>tvvppdwahd <swfUrl>http://privatestream.tv/js/jwplayer.flash.swf <pageUrl>http://iklub.net/tvp2l.html
    return vido_urls

def decode_all_urls(out,):
    out_hrefs=[]    
    for one in out:
        print one.get('title'),': ',one.get('url','')
        vido_url = decode_url(one.get('url',''))
        if vido_url:
            print'\t',vido_url
            one['url']=vido_url
            out_hrefs.append(one) 
    return out_hrefs

def build_m3u(out,fname='iklub.m3u'):    
    entry='#EXTINF:-1 tvg-id="{tvid}" tvg-logo="{img}" url-epg="{urlepg}" group-title="{group}",{title}\n{url}\n\n'
    OUTxmu='#EXTM3U\n'
    #OUTxmu=OUTxmu+'\n#EXTINF:-1, [COLOR yellow]Update: %s [/COLOR]\nhttp://www.youtube.com/\n\n' %(time.strftime("%d/%m/%Y: %H:%M:%S"))
    for one in out:
        OUTxmu=OUTxmu+entry.format(**one)
    myfile = open(fname,'w')
    myfile.write(OUTxmu)
    myfile.close()

##

# out=get_root()
# for one in out:
#     print one.get('title'),one.get('url'),one.get('img')
# 
# vido_url = decode_url(url='http://iklub.net/tvp1/')
# 
# out2=decode_all_urls(out)
# build_m3u(out2)
# len(out2)