# -*- coding: utf-8 -*-

import urllib2,urllib
import re
 
BASEURL=''
TIMEOUT = 5
 
def getUrl(url,data=None,cookies=None):
    req = urllib2.Request(url,data)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    if cookies:
        req.add_header("Cookie", cookies)
    try:
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link = response.read()
        response.close()
    except:
        link=''
    return link

def scanMainpage(url,page=1):
    url += '/' if url[-1] != '/' else ''
    content = getUrl(url + 'page/%d/' %page)
    nextpage=False
    if content.find(url + 'page/%d/' %(page+1))>0:
        nextpage = page+1
        
    ids = [(a.start(), a.end()) for a in re.finditer('<div id=\"mt.*\" class=\"item\">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<div class="boxinfo">[\s\n]+<a href="(.*?)">',re.DOTALL).search(subset)
        title = re.compile('<span class="tt">(.*?)</span>',re.DOTALL).search(subset)
        plot = re.compile('<span class="ttx">\n(.*?)(?:<div class="degradado"></div>){0,1}[\s\n]*</span>[\s\n]*',re.DOTALL).search(subset)
        img = re.compile('<div class="image">[\s\n]+<img src="(.*?)"',re.DOTALL).search(subset)
        imdb = re.compile('<span class="imdbs">(.*?)</span>',re.DOTALL).search(subset)
        year =  re.compile('<span class="year">(.*?)</span>',re.DOTALL).search(subset)
        quality = re.compile('<span class="calidad2">(.*?)</span>',re.DOTALL).search(subset)
        
        if href and title:
            img = img.group(1) if img else ''
            if img.startswith('//'):
                img = 'http:'+img
            one = {'href'   : href.group(1),
                'title'  : unicodePLchar(title.group(1)),
                'plot'   : unicodePLchar(plot.group(1)) if plot else '',
                'img'    : img,
                'rating' : imdb.group(1) if imdb else '?',
                'year'   : year.group(1) if year else '?',
                'code'  : quality.group(1) if quality else '?',
                    }
            out.append(one)
    nextPage=False
    if content.find(url + 'page/%d/' %(page+1))>0:
        nextPage = page+1
    prevPage = page-1 if page>1 else False
    return (out, (prevPage,nextPage))

#url='http://ouo.io/zd1BL3' 
#https://github.com/mirror/jdownloader/blob/8e0aada1b0e2fc7e7146136eb9cf993e1722f441/src/jd/plugins/decrypter/OuoIo.java
#https://github.com/mirror/jdownloader/blob/master/src/org/jdownloader/captcha/v2/challenge/recaptcha/v2/CaptchaHelperCrawlerPluginRecaptchaV2.java

def ouo(url):
    content = getUrl(url)
    token = re.search('name="_token" type="hidden" value="(.*?)">',content).group(1)
    sitekey = re.search('sitekey: "(.*?)"',content).group(1)
    params = {'_token':'MgZMB1Wf4UBGphYF1i63mO467wxG8S5k5ckp4MOj',
            'g-recaptcha-response':'03AHJ_VuvwwkKF1I9LNhURRsPJsQO5_SlHqGqV9borBaUWqmnqNDfqH1pTIPymqUwLLkj4xh6nWgAmBnwVcZBVugmMJiVcpL6-T2cJGu5fDKmEsxaZs1OQGQxp8tOr2YpaVcAVpePetQlBV0yA8gTCQcpmnfYdOScQkxU9o_s5Q4sjP4Hov2QbbhGV9SI4O8a-VRAVXrUzpf6xyuevYsuX3HxHa_BsYQC9U7DX0jfjBJDmilJab6UDRdVCleG-jFw7RKp75UUhlzXALOFoh3IWaZW9jLe0F3mVemVTQ-13p0OAynwuoATZWFthEL8C0NKMUbdVg5d-_628k_BwD1R6Kd4XjuA9flQCEMgU5hzLm8R_K3FKaFkPpiuUS3mr-tXz7vstL9BIPXjQw68Y1umk_7rQvKJgIQA2Nfb5waTADF1gaCusYM4d14NH9F52kE4lrdbaY2US9uiNCqEfYhAczXyFgxxqBJ58B6PPz0k3M7-XqZStPzaMP4MDRFr4yuJ1An7don4im69cO8pC0yvgayWxsalM8JLCDiT7VmSka78GYd0BdwS_dC1TxTikhV8cH9adJXY5AtCJCI2ejtAccyY5iycie-zvNZejvaC8GYIfwKNeYA3Vi60gYNgIev2a5UMIQZfY4zWf_pjs8T7wDLqr08kRHtR7hybmmKsvYwGFkiDMveeqQx-vzVD4c9te79ZpOuRSmAN8ii2ArdYHWb_M69a0HffagzPtU8MCc6Lwu8T65w1xq7ILnQRoccppMwC9B8T8lzdIqS2yLCsgKxzcLFOeqpt_QAIdNgibyF3q7DZecl41r2hxNkHp6mT1kjkC8gwzCbgvJAoq7zuZUXvoQCuEEUNAucItHM9UcMDQ4iMYPwBWbsUfezABiOWne0F7QQcE_KVY4yE4RFSEntWl9nyyX9O2OY6hEi2e1G5BAeXD_1yiL9s-s68plikFF_lBrQY0vcaPnM69QSfnrUAnF5h7BGwlTkqBglw62uOw5Pn2ktygRP-BTTpgUxVa0fthxEjR_31VCUvBmD3nwviOOARBkNxwzNLvzB-LHQ4Iwt8RWVj1HD22QYAWjFTHUZNMYog3rFR11Xi2_7FUcUcOGFMzzkCmIofpX813lk5deDmHiVzoNXg2uRiaDJqdDgltT78AhMSFMZhoMimJUvHluuB09IFCkE0M_6dzPyi23gidZRjYod8pqV20G4Y1bC6ZzttlDbcRccDfKadcJu9EpGMcVLQnnBzseTS0CGm8N1NluDcjMhwnzm8teTJIegesipsH7QZ8UyfgcyFPd0-8cOkkmKgleEUDVXCtAkZSbYT03S-tUqKxikQ7QxJOEVrHM0Y5wVjLNTs0TWFUEDEo5iXv-6qw98zu6yiWiQ2pFb7SbxvfmXhK3qFWvkUClxjgBh7kVu5tkkDN011SB5ReoCJuLdfHLtOh2FqZ2w7PhGKBjevdAL2fCREhX1JtYN8yAUiPNjxkABtAbmyL7s-Kp2WbvvRqL4357tT6mNXCqg-fnM1iQ9oYAtPimJodvD8ZCKY5B9mc3aOuDIQzv6LT_opevVa97oF0lediU8gO63Euqm6gI5K0j5VPeVvpc0zyaYVXF9tx5QzFKtOEAC_KaTh-Su7UJnW4QbHUi9PlsggQP0JA56_ghTO8BjPY2u8K99HDh_dp4Eb1E0T9A1xtzrbX3ZgF05wCEJe5Lm2qX0UdZXy_AVuq7S3EM3MjhJIZ-Kbje7PofqlxGm09IhJxRcdE4jXZgrld7aPhv0BT1Q91DXrR8lLtY6NRBsZfkh9N'
           }
    data=urllib.urlencode(params) 
    a=getUrl('http://ouo.io/go/Fkbcu',data)
    print a
    
def _getOrginalURL(url,host=''):
    orginal_link=''
    if url.startswith('http'):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
        try:
            response = urllib2.urlopen(req)
            if response:
                orginal_link=response.url
                if orginal_link==url:
                    content=response.read()
                    links = re.compile('<a href="(.*)" class').findall(content)
                    for l in links:
                        if host in l:
                            orginal_link = l
                            break
                response.close()
        except:
            pass
    return orginal_link

#url='http://cda-online.pl/carte-blanche/'
#url='http://cda-online.pl/critters-2/'

def getVideoLinks(url):
    content = getUrl(url)
    out  =[]
    iframe = re.compile('<iframe (.*?)</iframe>',re.DOTALL).findall(content)

    for frame in iframe:
        href = re.compile('src="(.*?)"',re.DOTALL).search(frame)
        if href:
            href_go = 'http'+ href.group(1).split('http')[-1]
            host = href_go.split('/')[2]

            if href_go.startswith('http') and not 'youtube' in href_go:
                one = {'url' : href_go,
                    'title': "[%s]" %(host),
                    'host': host    }
                out.append(one)
    return out
    

def getVideoLinks_odl(url):
    content = getUrl(url)
        
    ids = [(a.start(), a.end()) for a in re.finditer('<li class="elemento">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        href = re.compile('<a href="(.*?)"',re.DOTALL).search(subset)
        host = re.compile('<img src="(?:.*?)" alt="(.*?)">[\s\n]+(.*?)</span>').search(subset)
        jezyk = re.compile('<span class="c">(.*?)</span>',re.DOTALL).search(subset)
        jakosc =re.compile('<span class="d">(.*?)</span>',re.DOTALL).search(subset)
        
        if href and host:
            j= jezyk.group(1) if jezyk else ''
            q= jakosc.group(1) if jakosc else ''
            host = host.groups()[-1]
            href_go = 'http'+ href.group(1).split('http')[-1]
            
            print i,host,href.group(1),href_go,'\n'
            
            if host.startswith('openload'):
                link=''
            else:
                link = _getOrginalURL(href_go.replace('http://cda-online.pl?',''),host)
            
            if link:
                if 'openload' in host:
                    continue
                one = {'url' : link,
                    'title': "[%s] %s, %s" %(host,j,q),
                    'host': host    }
                out.append(one)
    return out

def scanTVshow(url):
    content = getUrl(url)
    ids = [(a.start(), a.end()) for a in re.finditer('<div class="numerando">', content)]
    ids.append( (-1,-1) )
    out=[]
    for i in range(len(ids[:-1])):
        #print content[ ids[i][1]:ids[i+1][0] ]
        subset = content[ ids[i][1]:ids[i+1][0] ]
        hreftitle = re.compile('<a href="(.*?)">[\s\n]+(.*?)</a>',re.DOTALL).search(subset)
        date = re.compile('<span class="date">(.*?)</span>').search(subset)
    
        
        if hreftitle:
            d= date.group(1) if date else ''
            t= hreftitle.group(2) + ' ' + d
            one = {'href'  : hreftitle.group(1),
                'title' : unicodePLchar(t.strip())}
            out.append(one)
    return out


def getGatunekRok(rodzaj='film',typ='gatunek'):
    content = getUrl('http://cda-online.pl/')
    selected = []
    if rodzaj=='film':
        if typ=='gatunek':
            selected = re.compile('<a href="(http://cda-online.pl/kategoria/.*?/)" >(.*?)</a> <span>(\d+)</span>').findall(content)
        else:
            selected = re.compile('<a href="(http://cda-online.pl/rok/\d{4}/)">(\d{4})</a>').findall(content)
    elif rodzaj=='serial':
        if typ=='gatunek':
            selected = re.compile('<a href="(http://cda-online.pl/seriale-gatunek/.*?/)" >(.*?)</a> <span>(\d+)</span>').findall(content)
        else:
            selected = re.compile('<a href="(http://cda-online.pl/seriale-rok/\d{4}/)">(\d{4})</a>').findall(content)
    if selected:
        url_list = [x[0] for x in selected]
        display = [' '.join(x[1:]) for x in selected]
        return (display,url_list)
    return False

def unicodePLchar(txt):
    txt = txt.replace('#038;','')
    txt = txt.replace('&lt;br/&gt;',' ')
    txt = txt.replace('&#34;','"')
    txt = txt.replace('&#39;','\'').replace('&#039;','\'')
    txt = txt.replace('&#8221;','"')
    txt = txt.replace('&#8222;','"')
    txt = txt.replace('&#8217;','\'')
    txt = txt.replace('&#8211;','-').replace('&ndash;','-')
    txt = txt.replace('&quot;','"').replace('&amp;quot;','"')
    txt = txt.replace('&oacute;','ó').replace('&Oacute;','Ó')
    txt = txt.replace('&amp;oacute;','ó').replace('&amp;Oacute;','Ó')
    #txt = txt.replace('&amp;','&')
    txt = txt.replace('\u0105','ą').replace('\u0104','Ą')
    txt = txt.replace('\u0107','ć').replace('\u0106','Ć')
    txt = txt.replace('\u0119','ę').replace('\u0118','Ę')
    txt = txt.replace('\u0142','ł').replace('\u0141','Ł')
    txt = txt.replace('\u0144','ń').replace('\u0144','Ń')
    txt = txt.replace('\u00f3','ó').replace('\u00d3','Ó')
    txt = txt.replace('\u015b','ś').replace('\u015a','Ś')
    txt = txt.replace('\u017a','ź').replace('\u0179','Ź')
    txt = txt.replace('\u017c','ż').replace('\u017b','Ż')
    return txt
    

if __name__=="dupa":
    url='http://cda-online.pl/filmy-online/'
    url='http://cda-online.pl/seriale-rok/2016'
    url='http://cda-online.pl/rok/2015/'
    url='http://cda-online.pl/seriale/'
    url='http://cda-online.pl/rok/2016/'
    out,pagination = scanMainpage(url,1)
    out[0].get('img')
    ## get vidoe sources
    url = out[0].get('href')
    links = getVideoLinks(url)

    ## get tv show episodes
    url='http://cda-online.pl/seriale/breaking-bad/'
    out = scanTVshow(url)
    url = out[0].get('href')
    links = getVideoLinks(url)
    
    url='http://cda-online.pl/igrzyska-smierci-kosoglos-czesc-2/'
    links = getVideoLinks(url)
    _getOrginalURL('http://go.cda-online.pl/Juv6D')
    data=getGatunekRok(rodzaj='film',typ='gatunek')
 
    