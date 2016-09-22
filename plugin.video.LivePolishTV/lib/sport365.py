# -*- coding: utf-8 -*-
import urllib2,urllib
import re
import time,json,base64
import cookielib,aes,os

BASEURL='http://www.sport365.live/pl/main'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

def fixForEPG(item):
    return(item)


def getUrl(url,data=None,header={},useCookies=True):
    if useCookies:
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
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
    ret=''
    content = getUrl(BASEURL)
    wrapper = re.compile('(http[^"]+/wrapper.js\?\d+)').findall(content)
    if wrapper:
        content=JsUnwiser().unwiseAll(getUrl(wrapper[0]))
        ret = re.compile('return "(.*?)"').findall(content)
        ret = ret[0]
    url='http://www.sport365.live/pl/events/-/1/-/-/120'
    content = getUrl(url)
    ids = [(a.start(), a.end()) for a in re.finditer('__showLinks', content)]
    ids.append( (-1,-1) )
    out=[]
    i=0
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        links=re.compile('\("([^"]+)", "([^"]+)", "[^"]+", 1\)').findall(subset)
        title2=re.compile('<img alt="(.*?)"').findall(subset)
        t=re.compile('>([^<]+)<').findall(subset)
        if links and title2:
            event,urlenc=links[0]
            url = 'http://www.sport365.live/en/links/%s/1@%s'%(event.split('_')[-1],ret)
            etime,title1= t[:2]
            lang = t[-1]
            quality =  t[-2].replace('&nbsp;',',') if len(t)==4 else ''
            title = '%s: [COLOR blue]%s[/COLOR] %s'%(etime,title1,title2[0])
            code=quality+lang
            out.append({'title':title,'tvid':'','img':'','url':url,'group':'','urlepg':'','code':code})
    return out

def get_streams(url,title):
    myurl,ret=url.split('@')
    content = getUrl(myurl)
    sources=re.compile('__showWindow\([\'"](.*?)[\'"]').findall(content)
    #s=sources[0]
    out=[]
    for s in sources:
        enc_data=json.loads(base64.b64decode(s))
        ciphertext = 'Salted__' + enc_data['s'].decode('hex') + base64.b64decode(enc_data['ct'])
        src=aes.decrypt(ret,base64.b64encode(ciphertext))
        src=src.strip('"').replace('\\','')
        out.append({'title':title,'tvid':title,'key':ret,'url':src,'refurl':myurl,'urlepg':''})
    return out

# out=get_root()
# url = out[0].get('url')
# streams = get_streams(url,'test')
#item=streams[0]
# url=streams[0].get('url')
#item['url']=

def get_link(item):
    content = getUrl(item.get('url'),useCookies=True)
    link=re.compile('(http://www.[^\.]+.pw/(?!&#)[^"]+)', re.IGNORECASE + re.DOTALL + re.MULTILINE + re.UNICODE).findall(content)
    if link:
        link=re.sub(r'&#(\d+);', lambda x: chr(int(x.group(1))), link[0])
        header = {'User-Agent':UA,
                  'Referer':item.get('url')}
        data = getUrl(link,header=header,useCookies=True)
        f=re.compile('.*?name="f"\s*value=["\']([^"\']+)["\']').findall(data)
        r=re.compile('[\'"]action[\'"][,\s]*[\'"](http.*?)[\'"]').findall(data)
        if f and r:
            enc_data=json.loads(base64.b64decode(f[0]))
            ciphertext = 'Salted__' + enc_data['s'].decode('hex') + base64.b64decode(enc_data['ct'])
            src=aes.decrypt(item.get('key'),base64.b64encode(ciphertext))
            src=src.replace('"','').replace('\\','').encode('utf-8')
            #print src
            if src.startswith('http'):
                href =src+'|Referer=%s&User-Agent=%s&X-Requested-With=ShockwaveFlash/22.0.0.209'%(urllib.quote(r[0]),UA)
                return href
            else:
                href=aes.decode_hls(src)
                if href:
                    href +='|Referer=%s&User-Agent=%s&X-Requested-With=ShockwaveFlash/22.0.0.209'%(urllib.quote(r[0]),UA)
                    return href
    return ''


# def get_link_old(item):
#     content = getUrl(item.get('url'),useCookies=True)
#     link=re.compile('(http://www.[^\.]+.pw/(?!&#)[^"]+)', re.IGNORECASE + re.DOTALL + re.MULTILINE + re.UNICODE).findall(content)
#     if link:
#         link=re.sub(r'&#(\d+);', lambda x: chr(int(x.group(1))), link[0])
#         header = {'User-Agent':UA,
#                   'Referer':item.get('url')}
#         data = getUrl(link,header=header,useCookies=True)
#         f=re.compile('.*?name="f"\s*value=["\']([^"\']+)["\']').findall(data)
#         s=re.compile('.*?name="s"\s*value=["\']([^"\']+)["\']').findall(data)
#         r=re.compile('[\'"]action[\'"][,\s]*[\'"](http.*?)[\'"]').findall(data)
#         sk=''
#         if s:
#             s=aes.decode_hls(s[0])
#             sk=re.compile('"stkey":"(.*?)"').findall(s)
#             sk = sk[0] if sk else ''
#         if f and r:
#             enc_data=json.loads(base64.b64decode(f[0]))
#             ciphertext = 'Salted__' + enc_data['s'].decode('hex') + base64.b64decode(enc_data['ct'])
#             src=aes.decrypt(item.get('key'),base64.b64encode(ciphertext))
#             src=src.replace('"','').replace(sk,'').replace('\\','').encode('utf-8')
#             print src
#             if src.startswith('http'):
#                 href =src+'|Referer=%s&User-Agent=%s'%(urllib.quote(item.get('url')),UA)
#             else:
#                 href=aes.decode_hls(src)
#                 if href:
#                     href +='|Referer=%s&User-Agent=%s'%(urllib.quote(r[0]),UA)
#                     return href
#     return ''


class JsUnwiser:
    def unwiseAll(self, data):
        try:
            in_data=data
            sPattern = 'eval\\(function\\(w,i,s,e\\).*?}\\((.*?)\\)'
            wise_data=re.compile(sPattern).findall(in_data)
            for wise_val in wise_data:
                unpack_val=self.unwise(wise_val)
                #print '\nunpack_val',unpack_val
                in_data=in_data.replace(wise_val,unpack_val)
            return re.sub(re.compile("eval\(function\(w,i,s,e\).*?join\(''\);}", re.DOTALL), "", in_data, count=1)
        except: 
            traceback.print_exc(file=sys.stdout)
            return data
        
    def containsWise(self, data):
        return 'w,i,s,e' in data
        
    def unwise(self, sJavascript):
        #print 'sJavascript',sJavascript
        page_value=""
        try:        
            ss="w,i,s,e=("+sJavascript+')' 
            exec (ss)
            page_value=self.__unpack(w,i,s,e)
        except: traceback.print_exc(file=sys.stdout)
        return page_value
        
    def __unpack( self,w, i, s, e):
        lIll = 0;
        ll1I = 0;
        Il1l = 0;
        ll1l = [];
        l1lI = [];
        while True:
            if (lIll < 5):
                l1lI.append(w[lIll])
            elif (lIll < len(w)):
                ll1l.append(w[lIll]);
            lIll+=1;
            if (ll1I < 5):
                l1lI.append(i[ll1I])
            elif (ll1I < len(i)):
                ll1l.append(i[ll1I])
            ll1I+=1;
            if (Il1l < 5):
                l1lI.append(s[Il1l])
            elif (Il1l < len(s)):
                ll1l.append(s[Il1l]);
            Il1l+=1;
            if (len(w) + len(i) + len(s) + len(e) == len(ll1l) + len(l1lI) + len(e)):
                break;
            
        lI1l = ''.join(ll1l)#.join('');
        I1lI = ''.join(l1lI)#.join('');
        ll1I = 0;
        l1ll = [];
        for lIll in range(0,len(ll1l),2):
            #print 'array i',lIll,len(ll1l)
            ll11 = -1;
            if ( ord(I1lI[ll1I]) % 2):
                ll11 = 1;
            #print 'val is ', lI1l[lIll: lIll+2]
            l1ll.append(chr(    int(lI1l[lIll: lIll+2], 36) - ll11));
            ll1I+=1;
            if (ll1I >= len(l1lI)):
                ll1I = 0;
        ret=''.join(l1ll)
        if 'eval(function(w,i,s,e)' in ret:
            ret=re.compile('eval\(function\(w,i,s,e\).*}\((.*?)\)').findall(ret)[0] 
            return self.unwise(ret)
        else:
            return ret
