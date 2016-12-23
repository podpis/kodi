# -*- coding: utf-8 -*-

import xbmc
import re
import os
import json
import jsunpack
import urllib
import urllib2
import urlparse
import cookielib
import random
import base64
import common

class ExternalBase:
    BASE_URLS = ['http://bajkionline.com/',
                 'http://segos.es',
                 'http://iitv.pl/',
                 'http://nasze-kino.online',
                 'http://www.ekabaret.pl/',
                 'http://www.cda.pl',
                 'https://api.dailymotion.com',
                 'https://www.laczynaspilka.pl/lista-filmow,1.html',
                 'http://lech.tv',
                 'http://www.livefootballol.me']
    TIMEOUT = 30
    UA = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
    COOKIEFILE = xbmc.translatePath(os.path.join('special://home','addons',common.addonID, 'resources', 'cookies'))

    def getUrl(self, url, data=None, header={}, useCookies=True, saveCookie=False):
        if self.COOKIEFILE and useCookies:
            cj = cookielib.LWPCookieJar()
            if os.path.isfile(self.COOKIEFILE):
                cj.load(self.COOKIEFILE)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)

        req = urllib2.Request(url, data)
        if not header:
            header = {'User-Agent': self.UA}
        req = urllib2.Request(url, data, headers=header)
        try:
            response = urllib2.urlopen(req, timeout=self.TIMEOUT)
            link = response.read()
            response.close()
            if self.COOKIEFILE and os.path.isfile(self.COOKIEFILE) and saveCookie and useCookies:
                cj.save(self.COOKIEFILE, ignore_discard=True)
        except:
            link = ''
        return link


"""
Created on Thu Feb 11 18:47:43 2016

@author: ramic
"""

class cdaresolver(ExternalBase):
    def _get_encoded_unpaker(self, content):
        src = ''
        packedMulti = re.compile("eval(.*?)\{\}\)\)", re.DOTALL).findall(content)
        for packed in packedMulti:
            packed = re.sub('  ', ' ', packed)
            packed = re.sub('\n', '', packed)
            try:
                unpacked = jsunpack.unpack(packed)
            except:
                unpacked = ''
            if unpacked:
                unpacked = re.sub(r'\\', r'', unpacked)
                src1 = re.compile('file:\s*[\'"](.+?)[\'"],', re.DOTALL).search(unpacked)
                src2 = re.compile('url:\s*[\'"](.+?)[\'"],', re.DOTALL).search(unpacked)
                if src1:
                    src = src1.group(1)
                elif src2:
                    src = src2.group(1)
                if src:
                    break
        return src

    def _get_encoded(self, content):
        src = ''
        idx1 = content.find('|||http')
        if idx1 > 0:
            idx2 = content.find('.split', idx1)
            encoded = content[idx1:idx2]
            if encoded:
                tmp = encoded.split('player')[0]
                tmp = re.sub(r'[|]+\w{2,3}[|]+', '|', tmp, re.DOTALL)
                tmp = re.sub(r'[|]+\w{2,3}[|]+', '|', tmp, re.DOTALL)

                remwords = ['http', 'logo', 'width', 'height', 'true', 'static', 'false', 'video', 'player',
                            'file', 'type', 'regions', 'none', 'czas', 'enabled', 'duration', 'controlbar', 'match',
                            'bottom',
                            'center', 'position', 'userAgent', 'navigator', 'config', 'html', 'html5', 'provider',
                            'black',
                            'horizontalAlign', 'canFireEventAPICalls', 'useV2APICalls', 'verticalAlign',
                            'timeslidertooltipplugin',
                            'overlays', 'backgroundColor', 'marginbottom', 'plugins', 'link', 'stretching', 'uniform',
                            'static1',
                            'setup', 'jwplayer', 'checkFlash', 'SmartTV', 'v001', 'creme', 'dock', 'autostart',
                            'idlehide', 'modes',
                            'flash', 'over', 'left', 'hide', 'player5', 'image', 'KLIKNIJ', 'companions', 'restore',
                            'clickSign',
                            'schedule', '_countdown_', 'countdown', 'region', 'else', 'controls', 'preload',
                            'oryginalne', 'style',
                            '620px', '387px', 'poster', 'zniknie', 'sekund', 'showAfterSeconds', 'images', 'Reklama',
                            'skipAd',
                            'levels', 'padding', 'opacity', 'debug', 'video3', 'close', 'smalltext', 'message', 'class',
                            'align',
                            'notice', 'media']

                for one in remwords:
                    tmp = tmp.replace(one, '')

                cleanup = tmp.replace('|', ' ').split()

                out = {'server': '', 'e': '', 'file': '', 'st': ''}
                if len(cleanup) == 4:
                    print 'Length OK'
                    for one in cleanup:
                        if one.isdigit():
                            out['e'] = one
                        elif re.match('[a-z]{2,}\d{3}', one) and len(one) < 10:
                            out['server'] = one
                        elif len(one) == 22:
                            out['st'] = one
                        else:
                            out['file'] = one
                    src = 'http://%s.cda.pl/%s.mp4?st=%s&e=%s' % (
                    out.get('server'), out.get('file'), out.get('st'), out.get('e'))
        return src

    def _scanforVideoLink(self, content):
        src1 = re.compile('file: [\'"](.+?)[\'"],', re.DOTALL).search(content)
        src2 = re.compile('url: [\'"](.+?)[\'"],', re.DOTALL).search(content)
        if src1:
            print 'found RE [file:]'
            video_link = src1.group(1)
        elif src2:
            print 'found RE [url:]'
            video_link = src2.group(1)
        else:
            print 'encoded : unpacker'
            video_link = self._get_encoded_unpaker(content)
            if not video_link:
                print 'encoded : force '
                video_link = self._get_encoded(content)
        return video_link

    def getVideoUrls(self, url):
        if 'ebd.cda.pl' in url:
            id = url.split('/')[-1]
            url = 'http://www.cda.pl/video/%s' % id
        playerSWF1 = '|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/player5.9/player.swf'
        playerSWF = '|Referer=http://static.cda.pl/player5.9/player.swf'
        content = self.getUrl(url)
        src = []
        if not '?wersja' in url:
            quality_options = re.compile('<a data-quality="(.*?)" (?P<H>.*?)>(?P<Q>.*?)</a>', re.DOTALL).findall(
                content)
            for quality in quality_options:
                link = re.search('href="(.*?)"', quality[1])
                hd = quality[2]
                src.insert(0, (hd, self.BASE_URLS[5] + link.group(1)))
        if not src:
            src = self._scanforVideoLink(content)
            if src:
                src += playerSWF1 + playerSWF

        return src

    def getVideoUrlsQuality(self, url, quality=0):
        src = self.getVideoUrls(url)
        if type(src) == list:
            selected = src[quality]
            src = self.getVideoUrls(selected[1])
        return src


class rapidvideoresolver(ExternalBase):
    def getVideoUrls(self, url):
        url = url.replace('http:','https:').replace('/embed/','/?v=')
        content,c = self.getUrl(url)
        match = re.findall('''["']?sources['"]?\s*:\s*(\[.*?\])''', content)
        videos=''
        if not match:
            data = {}
            data['confirm.y'] = random.randint(0, 120)
            data['confirm.x'] = random.randint(0, 120)
            header={'User-Agent':UA,'Referer':url}
            post_url = url + '#'
            content,c = self.getUrl(post_url,urllib.urlencode(data),header=header)
            match = re.findall('''["']?sources['"]?\s*:\s*(\[.*?\])''', content)

        if match:
            print match
            try:
                data = json.loads(match[0])
                videos=[]
                for d in data:
                    if isinstance(d,dict):
                        vu = d.get('file','')+'|User-Agent=%s&Referer=%s'%(UA,url)
                        videos.append((d.get('label',''),vu))
            except:
                videos = re.findall('''['"]?file['"]?\s*:\s*['"]?([^'"]+)''', match[0])
                if videos:
                    videos = videos[0].replace('\/', '/')
                    videos += '|User-Agent=%s&Referer=%s'%(UA,url)
        return videos


class extragoalsresolver(ExternalBase):
    def getVideoUrls(self, url):
        if url.startswith('//'):
            url = 'https:' + url
        src = ''
        BRAMKA = 'http://www.bramka.proxy.net.pl/index.php?q='
        content = self.getUrl(BRAMKA + url)
        srcs = re.compile('src=["\'](//.+?)["\']', re.DOTALL).findall(content)
        if srcs:
            src = srcs[0]
            if src.startswith('//'):
                src = 'http:' + src
        return src


class bajkionline(ExternalBase):

    def getList(self, url):
        content = self.getUrl(url)
        lis = re.compile('<li class="cat-item cat-item-\d+">[\n\s]*(.*?)</li>',re.DOTALL).findall(content)
        out=[]
        for subset in lis:
            href = re.compile('[<a]*\s*href="(.*?)"',re.DOTALL).findall(subset)
            plot = re.compile('title="(.*?)"',re.DOTALL).findall(subset)
            title = re.compile('>(.*?)<',re.DOTALL).findall(subset)

            if href and title:

                one = {'url'  : href[0],
                    'title'  : common.unicodePLchar(title[0]),
                    'plot'   : common.unicodePLchar(plot[0]) if plot else '',

                    }
                out.append(one)
        return out

    def getContent(self, url,page='1'):

        content = self.getUrl(url)
        nextPage=False

        ids = [(a.start(), a.end()) for a in re.finditer('<div class="col-md-3 col-sm-6 col-xs-6 ">', content)]
        if not ids:
            ids = [(a.start(), a.end()) for a in re.finditer('<a class="element gallery-sizer"', content)]
        ids.append( (-1,-1) )
        out=[]
        for i in range(len(ids[:-1])):
            subset = content[ ids[i][1]:ids[i+1][0] ]
            href = re.compile('[<a]*\s*href="(.*?)"',re.DOTALL).findall(subset)
            title = re.compile('title="(.*?)"',re.DOTALL).findall(subset)
            plot = re.compile('<p[^>]*>(.*?)</p>',re.DOTALL).findall(subset)
            img = re.compile('src="(.*?)"',re.DOTALL).findall(subset)


            if href and title:

                year =  re.compile('(\d{4})',re.DOTALL).search(title[0])
                one = {'url'   : href[0],
                    'title'  : common.unicodePLchar(title[0]),
                    'plot'   : common.unicodePLchar(plot[0]) if plot else '',
                    'img'    : img[0] if img else '',
                    'year'   : year.group(1) if year else '',
                        }
                out.append(one)

        pagination=re.compile('var pbd_alp\s*=\s*({.*?})').findall(content)
        if pagination:
            pagination = json.loads(pagination[0])
            nextPage = pagination.get('nextLink')
        prevPage =  False
        return out,(prevPage,nextPage)

    def getVideoLink(self, url):
        content = self.getUrl(url)
        iframes = re.compile('<iframe(.*?)</iframe',re.DOTALL).findall(content)
        for frame in iframes:
            src = re.compile('src="(http.*?)"').findall(frame)
            if src:
                return src[0]
        return ''


class ekabaretypl(ExternalBase):
    def getMovies(self, url='http://www.ekabaret.pl/toplista.html',data=None):
        content = self.getUrl(url,data)
        ids = [(a.start(), a.end()) for a in re.finditer('<div class="ico_video">', content)]
        ids.append( (-1,-1) )
        out=[]
        for i in range(len(ids[:-1])):
            subset = content[ ids[i][1]:ids[i+1][0] ]
            href_title = re.compile('<div style="margin-top: 15px;"><a href="(.*?)" title="(.*?)">').findall(subset)
            img = re.compile('transparent url\(\'(.*?)\'\)').findall(subset)
            if href_title :
                title = href_title[0][1].strip()
                href = urlparse.urljoin(self.BASE_URLS[4],href_title[0][0])
                one = {'url'   : href,
                    'title'  : common.unicodePLchar(title),
                    'img'    : img[0] if img else '',
                        }
                out.append(one)

        prevPage=re.compile('<a href="([^"]*)">&lt;&lt;&lt; poprzednia</a>').findall(content)
        prevPage = urlparse.urljoin(self.BASE_URLS[4],prevPage[0]) if prevPage else False
        nextPage=re.compile('<a href="([^"]*)">następna &gt;&gt;&gt; </a>').findall(content)
        nextPage = urlparse.urljoin(self.BASE_URLS[4],nextPage[0]) if nextPage else False
        return out,(prevPage,nextPage)

    def getCategories(self, url,data=None):
        content = self.getUrl(url,data)
        ids = [(a.start(), a.end()) for a in re.finditer('<div class="box">', content)]
        ids.append( (-1,-1) )
        out=[]
        for i in range(len(ids[:-1])):
            subset = content[ ids[i][1]:ids[i+1][0] ]
            href_title = re.compile('<b><a href="(.*?)" title="(.*?)">').findall(subset)
            img = re.compile('transparent url\(\'(.*?)\'\)').findall(subset)
            plot = re.compile('<div style="font-size: 12px; line-height: 17px;">(.*?)<',re.DOTALL).findall(subset)
            info = re.compile('<div class="inboxKATinfo"(.*?)</div>',re.DOTALL).findall(subset)
            Nskeczy=''
            for tmp in info:
                if 'Skeczy video:' in tmp:
                    Nskeczy = re.compile('<b>(\d+)</b>').findall(tmp)
                    break

            if href_title :
                title = href_title[0][1].strip()
                id = re.search('(\d+)-',href_title[0][0])
                if id:
                    href = 'http://www.ekabaret.pl/wideokat-%s.html'%id.group(1)
                else:
                    href = urlparse.urljoin(self.BASE_URLS[4],href_title[0][0])

                title += ' (%s)'%Nskeczy[0] if Nskeczy else ''
                one = {'url'   : href,
                    'title'  : common.unicodePLchar(title),
                    'plot'  : common.unicodePLchar(plot[0].strip()) if plot else '',
                    'img'    : common.urlparse.urljoin(self.BASE_URLS[4],img[0]) if img else '',
                        }
                out.append(one)

        prevPage=re.compile('<a href="([^"]*)">&lt;&lt;&lt; poprzednia</a>').findall(content)
        prevPage = urlparse.urljoin(self.BASE_URLS[4],prevPage[0]) if prevPage else False
        nextPage=re.compile('<a href="([^"]*)">następna &gt;&gt;&gt; </a>').findall(content)
        nextPage = urlparse.urljoin(self.BASE_URLS[4],nextPage[0]) if nextPage else False
        return out,(prevPage,nextPage)

    def getVideoUrl(self, url):
        content = self.getUrl(url)
        video_url=''
        iframes = re.compile('<iframe(.*?)</iframe>',re.DOTALL).findall(content)
        for iframe in iframes:
            src = re.compile('src=[\'"](.*?)[\'"]').findall(iframe)
            if src:
                video_url=src[0].strip()
                break
        return video_url


    def tvpResolve(self, ex_link='http://kabarety.tvp.pl/wideo/skecze/hrabi/hrabi-pogrzeb-cioci-15438607'):
        id = re.search('-(\d+)',ex_link)
        video_url=''
        if id:
            data=self.getUrl('http://tvpstream.tvp.pl/sess/tvplayer.php?object_id=%s'%id.group(1))
            live_src = re.compile("1:{src:'(.*?)'", re.DOTALL).findall(data)
            if live_src:
               video_url=live_src[0]
        return video_url


class ekstraklasa(ExternalBase):
    GATE = 'http://invisiblesurf.review/index.php?q='

    def getUrlByGate(self, url, data=None):
        if self.GATE:
            url = self.GATE + base64.b64encode(url) + '&hl=ed'
        return self.getUrl(url, data)

    def getLive(self, user):
        url = self.BASE_URLS[6] + "/user/" + user + "/videos?flags=live_onair&fields=" + urllib.quote(
            'id,duration,title,onair,private,thumbnail_240_url')
        content = self.getUrlByGate(url)
        list = []
        if content:
            data = json.loads(content)
            list = data.get('list', [])
        return list

    def getVideos(self, user, sort='recent', page='1'):
        fields = 'id,uri,duration,record_status,duration_formatted,title,onair,private,views_total,created_time,thumbnail_240_url'
        query = {'fields': fields,
                 'page': page,
                 'thumbnail_ratio': 'widescreen',
                 'sort': sort,
                 'limit': 50,
                 'localization': 'pl_PL'
                 }
        nextPage = False
        prevPage = False

        if sort == 'live':
            list = self.getLive(user)
        else:
            url = self.BASE_URLS[6] + "/user/" + user + "/videos?" + urllib.urlencode(query)
            content = self.getUrlByGate(url)
            data = json.loads(content)
            list = data.get('list', [])
            nextPage = {'user': user, 'sort': sort, 'page': data.get('page', page) + 1} if data.get('has_more',
                                                                                                    False) else False
            prevPage = {'user': user, 'sort': sort, 'page': data.get('page', page) - 1} if data.get('page',
                                                                                                    page) > 1 else False
        return (list, (prevPage, nextPage))

    def getVideoLinks(self, media_id='x4r4uoo'):
        content = self.getUrlByGate('http://www.dailymotion.com/embed/video/%s' % media_id)
        srcs = re.compile('"(1080|720|480|380)":(\[{[^\]]*\])', re.DOTALL).findall(content)
        out = []
        for quality, links in srcs:
            url = ''
            for type, href in re.compile('"type":"(.*?)","url":"(.*?)"').findall(links):
                if 'video' in type:
                    url = href
                    break
            if url:
                if self.GATE:
                    url = self.GATE + base64.b64encode(url.replace('\\', '')) + '&hl=ed'
                out.append({'label': quality, 'url': url.replace('\\', '')})

        if not out:
            srcs = re.compile('"(auto)":\[{"type":"(.*?)","url":"(.*?)"}\]', re.DOTALL).findall(content)
            for quality, type, url in srcs:
                print url
                m3u = self.getUrlByGate(url.replace('\\', '') + '&redirect=0')
                if '#EXTM3U' in m3u:
                    qq = re.compile('NAME="(.*?)"\n(.*?)\n').findall(m3u)
                    for label, url in qq:
                        out.append({'label': label, 'url': url})
                else:
                    burl = m3u.split('live.isml')[0] + 'live.isml/'
                    m3u2 = self.getUrlByGate(url.replace('\\', ''))
                    if '#EXTM3U' in m3u2:
                        qq = re.compile('RESOLUTION=(.*?)\n(.*?)\n').findall(m3u2)
                        for label, pp in qq:
                            out.append({'label': label, 'url': burl + pp})
        return out


class estadios(ExternalBase):

    def getLigue(self, url='http://estadios.pl/skroty-meczow'):
        content = self.getUrl(url)
        divs = re.compile('<div class="przyciski_lig">(.*?)</div>',re.DOTALL).findall(content)
        lgas=[]
        if divs:
            lgas = re.compile('<a href="(.*?)".*title="(.*?)">').findall(divs[0])
        return lgas

    def getMatchShorts(self, url):
        content = self.getUrl(url)
        TRs = re.compile('<tr class="dol_ciemny_tr" itemscope itemtype="http://data-vocabulary.org/Event">(.*?)</tr>',re.DOTALL).findall(content)
        out=[]
        for tr in TRs:
            title = re.compile('<div itemprop="summary" style="font-size: 1px; color: #F5F5F5;">(.*?)</div>(.*?)</td>',re.DOTALL).findall(tr)
            href = re.compile('<a href="(.*?)" title="Zobacz mecz" itemprop="url">(.*?)</a>').findall(tr)
            if title and href:
                when = re.compile('>(.*?)<').search(title[0][1]).group(1) if '<' in title[0][1] else title[0][1].strip()
                t=common.unicodePLchar('%s [COLOR lightblue]%s[/COLOR]'%(when,title[0][0].strip()))
                u=href[0][0]
                c=href[0][1]
                out.append( {'title':t,'url':u,'code':c} )
        return out

    def getVideoLinks(self, url):
        content = self.getUrl(url)
        iframe = re.compile('<div class="klip_film">(.*?)</div>',re.DOTALL).findall(content)
        src=''
        if iframe:
            src = re.findall('src="(.*?)"',iframe[0])
            src = src[0] if src else ''
            if 'playwire' in src:
                src = re.findall('data-config="(.*?)"',iframe[0])
                src = src[0] if src else ''
            print src
        return src


class footballorgin(ExternalBase):
    def getContent(self, url, page='1'):
        if url:
            content = self.getUrl(url)
            data = False
        if not url:
            url = 'http://www.footballorgin.com/wp-admin/admin-ajax.php'
            data = 'action=infinite_scroll&page_no=%d' % int(page)
            content = self.getUrl(url, data)

        ids = [(a.start(), a.end()) for a in re.finditer('<article id="post', content)]
        ids.append((-1, -1))
        out = []
        for i in range(len(ids[:-1])):
            subset = content[ids[i][1]:ids[i + 1][0]]

            img = re.compile('src="(.*?)"').findall(subset)
            href_title = re.compile('<h2 class="entry-title" itemprop="headline"><a href="(.*?)".*?>(.*?)</a>').findall(
                subset)
            code = re.compile('rel="category tag">(.*?)<').findall(subset)

            if href_title and img:
                h = href_title[0][0]
                t = href_title[0][1].strip()
                c = code[-1] if code else ''
                out.append({'url': h, 'title': common.unicodePLchar(t), 'img': img[0], 'code': c})

        nextPage = {'page': int(page) + 1} if len(out) == 10 and data else False
        prevPage = {'page': int(page) - 1} if int(page) > 1 and data else False
        return out, (prevPage, nextPage)

    def getVideos(self, url):
        content = self.getUrl(url)
        out = []
        subpages = re.compile('<li class="subpage-.*?"><a href="(.*?)">(.*?)</a></li>').findall(content)
        src = re.compile('data-config="(//.*\.json)"').findall(content)
        if subpages:
            for sp in subpages:
                if sp[0] == url and src:
                    pass
                else:
                    content2 = getUrl(sp[0])
                    src = re.compile('data-config="(//.*\.json)"').findall(content2)
                src = src[0] if src else ''
                out.append({'url': src, 'title': sp[1]})
                src = []
        elif src:
            out = [{'url': src[0], 'title': 'video'}]
        return out

    def getMain(self):
        out = [
            {'title': 'Full Match Replay', 'url': '', 'params': {'page': 1}},
            {'title': 'Review Show', 'url': 'http://www.footballorgin.com/category/motd/', 'params': {}},
            {'title': 'Premier League', 'url': 'http://www.footballorgin.com/category/epl/', 'params': {}},
            {'title': 'Champions league (UCL)', 'url': 'http://www.footballorgin.com/category/champions-league-ucl/',
             'params': {}},
            {'title': 'Championship', 'url': 'http://www.footballorgin.com/category/championship/', 'params': {}},
            {'title': 'SPFL', 'url': 'http://www.footballorgin.com/category/spfl/', 'params': {}},
            {'title': 'Bundesliga', 'url': 'http://www.footballorgin.com/category/bundesliga/', 'params': {}},
            {'title': 'La liga', 'url': 'http://www.footballorgin.com/category/la-liga/', 'params': {}},
            {'title': 'Serie A', 'url': 'http://www.footballorgin.com/category/serie-a/', 'params': {}},
            {'title': 'TV show', 'url': 'http://www.footballorgin.com/category/tv-show/', 'params': {}},
        ]
        return out


class goalsarena(ExternalBase):
    def getContent(self, type='latest_highlights'):
        xbmc.log(type)
        if type == 'latest_highlights':
            return self.getLatestHighLights()
        elif type == 'must_watch':
            return self.getMustWatch()
        return [], (False, False)

    def getLatestHighLights(self):
        content = self.getUrl('http://www.goalsarena.org/en')
        goalvideos = re.compile('<div class="goalvideos"><h2><span class="flags sprite-\d+"(.*?)</div>',
                                re.DOTALL).findall(content)
        out = []
        for goal in goalvideos:
            href_title = re.compile('<a title="(.*?)" href="(.*?)">').findall(goal)
            if href_title:
                out.append({'title': href_title[0][0], 'url': href_title[0][1]})
        return out, (False, False)

    def getMustWatch(self):
        content = self.getUrl('http://www.goalsarena.org/en')
        goalvideos = re.compile('<div class="thumboverlay">(.*?)</div>', re.DOTALL).findall(content)
        out = []
        for goal in goalvideos:
            href_img_title = re.compile(
                '<a href="(.*)"><img class="thumbwrapper" src="(.*)" width="170px" height="120px" alt="(.*)"/>').findall(
                goal)
            if href_img_title:
                out.append(
                    {'title': href_img_title[0][2].strip(), 'img': href_img_title[0][1], 'url': href_img_title[0][0]})
        return out, (False, False)

    def getVideos(self, url):
        content = self.getUrl(url)
        v = {'msg': 'Video link not found or not supported yet'}
        src = re.compile('data-config="(.*\.json)"').findall(content)
        if src:
            v = {'msg': '', 'url': src[0].replace('player.json', 'zeus.json')}
        return v

    def getMain(self):
        out = [
            {'title': 'Latest Highlights', 'url': 'latest_highlights',
             'params': {'type': 'latest_highlights', 'page': 1}},
            {'title': 'Must Watch', 'url': 'must_watch', 'params': {'type': 'must_watch', 'page': 1}},
        ]
        return out


class Iitv(ExternalBase):
    def getSerials(self, page=1):
        page = int(page)
        url = 'http://iitv.pl/ajax/getCellsList/%d?init=false' % int(page)
        out = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://iitv.pl/'}
        content = self.getUrl(url, None, headers)
        if content:
            data = json.loads(content)
            for k, v in data['results'].iteritems():
                one = {}
                one['title'] = '%s %s' % (v.get('seasonAndEpisodeCode', ''), v.get('seriesTitle'))
                one['plot'] = v.get('description', '')
                one['img'] = v.get('imageUrl', '')
                one['url'] = v.get('url', '')
                one['data'] = v.get('date', '')
                one['code'] = v.get('flag', '')
                one['urlSeries'] = v.get('theSeriesUrl', '')
                out.append(one)

        nextPage = int(page) + 1 if len(out) else False
        prevPage = page - 1 if page > 1 else False
        return (out, (prevPage, nextPage))

    def getPopular(self):
        content = self.getUrl(self.BASE_URLS[2])
        ul = re.compile('<ul id="popular-list">(.*?)</ul>', re.DOTALL).findall(content)
        out = []
        for u in ul:
            ps = re.compile('<a href="(http:.*?)">([^<]+)<').findall(u)
            for u, t in ps:
                out.append({'title': common.unicodePLchar(t), 'url': u})
        return out

    def getList(self):
        content = self.getUrl(self.BASE_URLS[2])
        ul = re.compile('<ul id="list">(.*?)</ul>', re.DOTALL).findall(content)
        out = []
        for u in ul:
            ps = re.compile('<a href="(http:.*?)">([^<]+)<').findall(u)
            for u, t in ps:
                out.append({'title': common.unicodePLchar(t), 'url': u})
        return out

    def getEpisodes(self, url):
        content = self.getUrl(url)
        out = []
        el = re.compile('<div class="episodes-list">(.*?)</div>', re.DOTALL).findall(content)
        if el:
            for li in re.compile('<li>(.*?)</li>', re.DOTALL).findall(el[0]):
                date = re.compile('class="column date">(.*?)<').search(li)
                epis = re.compile('episode-code">(.*?)<').search(li)
                href = re.compile('href="(http.*?)"[^>]*>(.*?)<').search(li)
                if href:
                    code = date.group(1) if date else ''
                    title = epis.group(1) if date else ''
                    title += ' ' + href.group(2) if date else ''
                    out.append({'title': common.unicodePLchar(title), 'url': href.group(1), 'code': code})
        return out

    def getLinks(self, url):
        content = self.getUrl(url)
        ul = re.compile('<ul class="tab-content"(.*?)</ul>', re.DOTALL).findall(content)
        out = []
        for u in ul:
            lang = re.compile('id="(.*?)"').search(u)
            lang = lang.group(1) if lang else ''
            lang = lang.replace('org', '[COLOR grey]ORYGINAŁ[/COLOR]')
            lang = lang.replace('lecPL', '[COLOR green]Lektor[/COLOR]')
            lang = lang.replace('subPL', '[COLOR orange]Napisy[/COLOR]')
            links = re.compile('<a class="video-link" href="(.*?)" data-link-id=".*?">(.*?)</a>').findall(u)
            for l in links:
                out.append({'title': '[%s] %s' % (lang, l[-1]), 'url': l[0]})
        return out

    def getHostUrl(self, url):
        content = self.getUrl(url)
        src = ''
        iframes = re.compile('<iframe(.*?)</iframe>', re.DOTALL).findall(content)
        for frame in iframes:
            src = re.compile('src=["\'](.*?)["\']').search(frame)
            src = src.group(1) if src else ''
        return src


class laczynaspilka(ExternalBase):

    def getContent(self, url):
        if not url: url = self.BASE_URLS[7]
        content = self.getUrl(url)
        out=[]
        tds = re.compile('<a (href="//www.youtube.com.*?)</a>',re.DOTALL).findall(content)
        nextPage=False
        prevPage=False
        for td in tds:
            href = re.compile('href="(.*?)"').findall(td)
            title = re.compile('data-title="(.*?)"').findall(td)
            date = re.compile('data-date="(.*?)"').findall(td)
            img=re.compile('<img src="(.*?)"').findall(td)
            if href and title:
                h = 'http:'+href[0]
                t = title[0].strip()
                i = img[0] if img else ''
                code = date[0] if date else ''
                out.append({'url':h,'title':t,'img':i,'code':code})
        if out:
            nextPage = re.compile('<a href="(http.*?)">Następna').findall(content)
            nextPage = {'urlp': nextPage[0]} if nextPage else False
            prevPage = re.compile('<a href="(http.*?)"> &laquo; Poprzednia').findall(content)
            prevPage = {'urlp': prevPage[0]} if prevPage else False
        return (out,(prevPage,nextPage))

    def getVideos(self, url):
        return {'msg':'','url':url}


class lechtv(ExternalBase):
    def getContent(self, type='category',page=1,category=7):
        iteppp = 25
        if type == 'category':
            url='http://lech.tv/lechtv_ajax/get_videos_category.php'
            data='video_start_number=%d&video_stop_number=%d&category_id=%d'%(int(page)*iteppp,iteppp,int(category))
        elif type== 'popular':
            url='http://lech.tv/lechtv_ajax/get_videos_most_popular.php'
            data=''
        else:
            url='http://lech.tv/lechtv_ajax/get_videos_newest.php'
            data='video_start_number=%d&video_stop_number=%d'%(int(page)*iteppp,iteppp)

        content = self.getUrl(url,data)
        out = self.parseContent(content)

        nextPage = {'type':type,'page':int(page)+1,'category':category} if len(out) == iteppp else False
        prevPage = {'type':type,'page':int(page)-1,'category':category} if int(page)>0 else False
        return out,(prevPage,nextPage)

    def parseContent(self, content):
        content = content.decode('unicode_escape')
        ids = [(a.start(), a.end()) for a in re.finditer('<td class="video_medium_box">', content)]
        ids.append( (-1,-1) )
        out=[]
        for i in range(len(ids[:-1])):
            subset = content[ ids[i][1]:ids[i+1][0] ].replace('\\','').encode('utf-8')
            img = re.compile('<img src="(.*?)" alt=".*?"').findall(subset)
            href = re.compile('<a href="video-id-(\d+)-.*?"').findall(subset)
            title = re.compile('<img src=".*?" alt="(.*?)"').findall(subset)
            plot = re.compile('<a href=".*?" class="video_medium_desc_short">(.*?)</a>').findall(subset)
            code = re.compile('<span class="video_medium_date">(.*?)</span>').findall(subset)
            if not code:
                code = re.compile('<a href=".*?" class="video_medium_category">(.*?)</a>').findall(subset)

            if href and title:
                h = href[0]
                t = common.unicodePLchar(title[0].strip())
                i = urlparse.urljoin(self.BASE_URLS[8],img[0]) if img else ''
                p = common.unicodePLchar(plot[0].strip()) if plot else ''
                c = common.unicodePLchar(code[0].strip()) if code else ''
                out.append({'url':h,'title':t,'img':i,'plot':p,'code':c})
        return out

    def getExtraclassTable(self):
        content= self.getUrl(self.BASE_URLS[8])
        table = re.compile('<table class="league_table">(.*?)</table>',re.DOTALL).findall(content)
        out = []
        if table:
            pos = re.compile('<td class="league_table_position">(.+?)<').findall(table[0])
            pts = re.compile('<td class="league_table_points">(.+?)<').findall(table[0])
            team = re.compile('<td class="league_table_team">(.+?)<').findall(table[0])
            for p,pt,name in zip(pos,pts,team):
                out.append({'title':'%s [B]%s[/B]'%(p,name),'code':'[COLOR blue][B]%s[/B][/COLOR]'%pt})
        return out

    def getVideos(self, id='23422'):
        url='http://lech.tv/lechtv_ajax/get_player_new.php'
        data='id='+id+'&ads_param='
        content = self.getUrl(url,data)
        video_url={'msg':'Video link not found or not supported yet'}
        src = re.compile('src=["\'](.*?)["\']').findall(content)
        if src:
            data = self.getUrl(src[0])
            srcs=re.compile('src\s*=\s*\[\s*\[(.*?)\]\s*\];',re.DOTALL).findall(data)
            if srcs:
                links=re.compile('"(http.*?)"').findall(srcs[0])
                for link in links:
                    if link.endswith('.m3u8') or link.endswith('.mp4'):
                        video_url={'msg':'','url':link,'resolved':True}
                        break
        return video_url


class livefootballol(ExternalBase):

    def getMain(self, url='http://www.livefootballol.me/video/'):
        content = self.getUrl(url)
        divs = re.compile('<h3 class="page-header item-title">(.*?)</h3>',re.DOTALL).findall(content)
        out=[]
        for div in divs:
            href_title = re.compile('<a href="(.*?)">(.*?)</a>',re.DOTALL).findall(div)
            count = re.compile('title="Article Count:">(.*?)<',re.DOTALL).findall(div)
            if href_title and count:
                h = self.BASE_URLS[9] + href_title[0][0]
                t = href_title[0][1].strip() + ' ([COLOR blue]' +count[0].strip() +'[/COLOR])'
                out.append({'url':h,'title':t})
        return out

    def getContent(self, url):
        content = self.getUrl(url)
        tds = re.compile('<td>(.*?)</td>',re.DOTALL).findall(content)
        out=[]
        nextPage=False
        prevPage=False
        for td in tds:
            href = re.compile('<a href="(.*?)"',).findall(td)
            title = re.compile('>(.*?)<',re.DOTALL).findall(td)
            if href and title:
                h = self.BASE_URLS[9] + href[0]
                t = title[0].strip()
                t = re.sub('(\d+-\d+)','[COLOR blue]\g<1>[/COLOR]',t)
                out.append({'url':h,'title':t})
        if out:
            nextPage = re.compile('<a class="next" href="(.*?)" ').findall(content)
            nextPage = {'urlp':self.BASE_URLS[9] + nextPage[0]} if nextPage else False
            prevPage = re.compile('<a class="previous" href="(.*?)" ').findall(content)
            prevPage = {'urlp':self.BASE_URLS[9] + prevPage[0]} if prevPage else False
        return (out,(prevPage,nextPage))


    def getVideos(self, url):
        content = self.getUrl(url)
        v={'msg':'Video link not found or not supported yet'}
        src = re.compile('data-config="(//.*\.json)"').findall(content)
        if src:
            v={'msg':'','url':src[0].replace('player.json','zeus.json')}
        return v


class naszekino(ExternalBase):
    def getForum(self):
        out = [
            {'title': 'Filmy', 'url': 'http://nasze-kino.online/forumdisplay.php/57-Filmy-Online',
             'img': 'http://nasze-kino.online/images/filmy.png'},
            {'title': 'Seriale', 'url': 'http://nasze-kino.online/forumdisplay.php/58-Seriale-Online',
             'img': 'http://nasze-kino.online/images/seriale.png'},
            {'title': 'Rozrywka', 'url': 'http://nasze-kino.online/forumdisplay.php/59-Rozrywka-Online',
             'img': 'http://nasze-kino.online/images/rozrywka.png'},
            {'title': 'Sport', 'url': 'http://nasze-kino.online/forumdisplay.php/60-Sport-Online',
             'img': 'http://nasze-kino.online/images/sport.png'},
            {'title': 'Bajki', 'url': 'http://nasze-kino.online/forumdisplay.php/71-Bajki-Online',
             'img': 'http://nasze-kino.online/images/bajki.png'}
        ]
        return out, (False, False)

    def getForumEntry(self, url):
        content = self.getUrl(url)
        ids = [(a.start(), a.end()) for a in re.finditer('<table class="vbs_forumrow threadbit', content)]
        ids.append((-1, -1))
        out = []
        next = False
        prev = False

        for i in range(len(ids[:-1])):
            subset = content[ids[i][1]:ids[i + 1][0]]

            img = re.compile('<img class="preview" src="(.*?)"').findall(subset)
            href = re.compile('href="(.*?)" id="thread_title_.*?">(.*?)</a>').findall(subset)
            if href:
                h = urlparse.urljoin(self.BASE_URLS[3], href[0][0])
                t = common.unicodePLchar(href[0][1])
                i = img[0] if img else ''
                out.append({'title': t, 'url': h, 'img': i})
        if out:
            nextPage = re.compile('<a rel="next" href="(.*?)" title="(.*?)"><img src="(.*?)"').search(content)
            if nextPage:
                next = {'url': urlparse.urljoin(self.BASE_URLS[3], nextPage.group(1)),
                        'title': common.unicodePLchar(nextPage.group(2)), 'img': ''}
            prevPage = re.compile('<a rel="prev" href="(.*?)" title="(.*?)"><img src="(.*?)"').search(content)
            if prevPage:
                prev = {'url': urlparse.urljoin(self.BASE_URLS[3], prevPage.group(1)),
                        'title': common.unicodePLchar(prevPage.group(2)), 'img': ''}

        return out, (prev, next)

    def getThreadLinks(self, url):
        content = self.getUrl(url)
        out = []
        codes = re.compile('<div id="post_message_(.*?)</blockquote>', re.DOTALL).findall(content)
        for code in codes:
            links = re.compile('<a href="(http.*?)" target="_blank">(.*?)</a>').findall(code)
            for link in links:
                out.append({'title': urlparse.urlsplit(link[0]).netloc, 'url': link[0]})
        return out


class polsatsport(ExternalBase):
    def getContentDir(self, type='magazyny'):
        if type=='magazyny':
            return self.getMagazines()
        elif type == 'dyscypliny':
            return self.getDisciplines()
        return []

    def getDisciplines(self):
        url='http://www.polsatsport.pl/wideo-lista/'
        content = self.getUrl(url)
        out=[]
        ids = [(a.start(), a.end()) for a in re.finditer('<li class="disciplines-aside-', content)]
        ids.append( (-1,-1) )
        out=[]
        mTittle=['[COLOR blue][B]%s[/B][/COLOR]','[COLOR green][B]%s[/B][/COLOR]']
        sTittle=['   [COLOR lightblue]%s[/COLOR]','   [COLOR lightgreen]%s[/COLOR]']
        for i in range(len(ids[:-1])):
            subset = content[ ids[i][1]:ids[i+1][0] ]
            d = re.compile('<a href="(http://www.polsatsport.pl/wideo-kategoria.*)">(.*)</a>').findall(subset)
            if d:
                maind = d.pop(0)
                t=mTittle[i%2]%common.unicodePLchar(maind[1])
                out.append({'title':t,'url':maind[0],'img':''})
                for one in d:
                        t=sTittle[i%2]%common.unicodePLchar(one[1])
                        out.append({'title':t,'url':one[0],'img':''})
        return out

    def getContent(self, url,type='magazyny'):
        if type == 'magazyny':
            return self.getMagazines()
        return []

    def getContentVideos(self, url):
        content = self.getUrl(url)
        tds = re.compile('<article(.*?)</article>',re.DOTALL).findall(content)
        out=[]
        nextPage=False
        prevPage=False
        for td in tds:
            href = re.compile('<a href="(.*?)"',).findall(td)
            title = re.compile('alt="(.*?)"').findall(td)
            img = re.compile('src="(.*?)"').findall(td)
            if href and title:
                h = href[0]
                t = common.unicodePLchar(title[0].strip())
                i = img[0] if img else ''
                out.append({'url':h,'title':t,'img':i})
        if out:
            nextPage = re.compile('<a href="(.*?)" class="next-page ico"></a>').findall(content)
            nextPage = nextPage[0] if nextPage else False
            prevPage = re.compile('<a href="(.*?)" class="prev-page ico"></a>').findall(content)
            prevPage = prevPage[0] if prevPage else False
        return (out,(prevPage,nextPage))

    def getVideos(self, url):
        content = self.getUrl(url)
        v={'msg':'Video link not found or not supported yet'}
        src = re.compile('<source src="(.*?)" type="video/mp4">').findall(content)
        if src:
            v={'msg':'','url':src[0]}
        return v


    def _searchMagazines(self):
        url='http://www.polsatsport.pl/program/atleci/'
        content = self.getUrl(url)
        out=[]
        magazines = re.compile('<li class="disciplines-aside-item"><a href="(.*)" [^>]*>(.*)</a></li>').findall(content)
        for magazine in magazines:
            tmp=self.getUrl(magazine[0])
            plot = re.compile('<div class="article-preview"(.*?)</div>',re.DOTALL).findall(tmp)
            plot = plot[0] if plot else ''
            if plot:
                plot = re.compile('<p><span>(.*?)</span></p>').findall(plot)
                plot = common.unicodePLchar(plot[0]) if plot else ''
            img=re.compile('<div class="fl-right">\s*<figure>\s*<img src="(.*?)"',re.DOTALL).findall(tmp)
            img = img[0] if img else ''
            out.append({'title':common.unicodePLchar(magazine[1]),'url':magazine[0],'plot':plot,'img':img})
        return out

    def getMagazines(self):
        out=[{'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/p8/p8par25wy336d3ynjs5gcgi4nrbmnqzo.jpg',
                'plot': 'Atleci to program dla wszystkich, kt\xc3\xb3rzy kochaj\xc4\x85 sport - i ogl\xc4\x85da\xc4\x87, i uprawia\xc4\x87, a w nim co tydzie\xc5\x84 rozmowy z gwiazdami lekkiej atletyki, wiadomo\xc5\x9bci ze \xc5\x9bwiata kr\xc3\xb3lowej sportu; poka\xc5\xbcemy tak\xc5\xbce, \xc5\xbce biega\xc4\x87 ka\xc5\xbcdy mo\xc5\xbce.',
                'title': 'Atleci',
                'url': 'http://www.polsatsport.pl/program/atleci/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/nm/nm1vnqzacinsd1rhet1zkdr4wdptch7t.jpg',
                'plot': '',
                'title': 'Cafe Futbol',
                'url': 'http://www.polsatsport.pl/program/cafe-futbol/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/f8/f8rpnhhyf1srvkufno325j4w1adfj2fn.jpg',
                'plot': '',
                'title': 'Fanatyk',
                'url': 'http://www.polsatsport.pl/program/fanatyk/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/rc/rcquncrsj893hhoe92vbp7bo4pn2sam7.jpg',
                'plot': 'Magazyn o pi\xc5\x82ce kopanej realizowany podczas mistrzostw \xc5\x9bwiata Brazylia 2014 przy wsp\xc3\xb3\xc5\x82pracy z redaktorami Wydawnictwa Kopalnia - Markiem Wawrzynowskim i Piotrem \xc5\xbbelaznym. W ka\xc5\xbcdym odcinku wyj\xc4\x85tkowy futbolowy go\xc5\x9b\xc4\x87!',
                'title': 'Kopalnia',
                'url': 'http://www.polsatsport.pl/program/kopalnia/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/ta/ta3iaw7gfyeukidot3cz3rn4vme19v82.jpg',
                'plot': 'Najlepszy w Polsce magazyn sportowy po\xc5\x9bwi\xc4\x99cony pi\xc5\x82ce siatkowej.',
                'title': 'Kr\xc3\xb3tka Pi\xc5\x82ka',
                'url': 'http://www.polsatsport.pl/program/krotka-pilka/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/h9/h9uuvp49kw6zi15udd6tucky3g3sftmr.jpg',
                'plot': 'Roman Ko\xc5\x82to\xc5\x84 rozmawia z wybitnymi postaciami polskiego i \xc5\x9bwiatowego sportu.',
                'title': 'Kulisy Sportu',
                'url': 'http://www.polsatsport.pl/program/kulisy-sportu/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/9n/9n1sh7rrxogqt8dnkzeys5jkoo6sqvyd.jpg',
                'plot': '',
                'title': 'Magazyn Koszykarski',
                'url': 'http://www.polsatsport.pl/program/magazyn-koszykarski/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/hv/hv763sufe8uib61r5vgvidw35u4k37fa.png',
                'plot': 'KSW action to nowy projekt ipla, stworzony wsp\xc3\xb3lnie z federacj\xc4\x85 KSW, ma w swoim za\xc5\x82o\xc5\xbceniu przybli\xc5\xbcy\xc4\x87 widzom niezwykle emocjonuj\xc4\x85c\xc4\x85 i widowiskow\xc4\x85 dyscyplin\xc4\x99, jak\xc4\x85 jest MMA.&nbsp;</span><br /><br /><span>KSW Action to oko\xc5\x82o p\xc3\xb3\xc5\x82godzinna porcja wiadomo\xc5\x9bci ze \xc5\x9bwiata MMA. W ka\xc5\xbcdym odcinku zobaczymy obszerny wywiad, unikalne felietony oraz reporta\xc5\xbce, ca\xc5\x82o\xc5\x9b\xc4\x87 uzupe\xc5\x82nia specjalny przegl\xc4\x85d aktualno\xc5\x9bci zrobiony we wsp\xc3\xb3\xc5\x82pracy z portalem MMA Rocks.',
                'title': 'Magazyn KSW Action',
                'url': 'http://www.polsatsport.pl/program/magazyn-ksw-action/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/1k/1kb4vpx9pgnmetpoi73zyjpzfagxx1hh.jpg',
                'plot': 'Znajdziesz tu przegl\xc4\x85d wydarze\xc5\x84 z polskich rozgrywek ligowych. Dowiesz si\xc4\x99 co wydarzy\xc5\x82o si\xc4\x99 ostatnio w krajowej siatk\xc3\xb3wce, pi\xc5\x82ce r\xc4\x99cznej czy \xc5\xbcu\xc5\xbclu.',
                'title': 'Magazyn Liga',
                'url': 'http://www.polsatsport.pl/program/magazyn-liga/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/y8/y86z94886b3e9xvqn45vmf7rc3a4w77e.jpg',
                'plot': "Wszystko o polskim 'szczypiorniaku', czyli pi\xc5\x82ce r\xc4\x99cznej. Cotygodniowe, podsumowanie kolejek polskiej Superligi kobiet i m\xc4\x99\xc5\xbcczyzn, wyst\xc4\x99p\xc3\xb3w Vive Kielce w Lidze Mistrz\xc3\xb3w i naszych obu reprezentacji. W programie nie zabraknie te\xc5\xbc publicystyki i rozm\xc3\xb3w z trenerami, pi\xc5\x82karzami i ekspertami. Gospodarzami magazynu s\xc4\x85 dziennikarze Polsatu Sport Tomasz W\xc5\x82odarczyk i Marcin Muras.&nbsp;",
                'title': 'Magazyn Pi\xc5\x82ki R\xc4\x99cznej',
                'url': 'http://www.polsatsport.pl/program/magazyn-pilki-recznej/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/an/anu5dgoe4f8vpit4pzfp8t7493acow27.jpg',
                'plot': 'Magazyn SET powsta\xc5\x82 z my\xc5\x9bl\xc4\x85 o kibicach siatk\xc3\xb3wki. Znajdziesz w nim rozmowy z lud\xc5\xbami zwi\xc4\x85zanymi z tym sportem. Gospodarzem programu jest Krzysztof Wanio.',
                'title': 'Magazyn SET',
                'url': 'http://www.polsatsport.pl/program/magazyn-set/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/qr/qrhwg294tqbh9jz2gc7ao12oui7i9i3a.jpg',
                'plot': 'Najlepszy, najtrudniejszy, najwa\xc5\xbcniejszy&hellip; Szablonowe has\xc5\x82a te\xc5\xbc mog\xc4\x85 by\xc4\x87 NAJ, a nawet &bdquo;NAJz&hellip;&rdquo;, je\xc5\x9bli sportowiec chce zmierzy\xc4\x87 si\xc4\x99 ze swoimi decyzjami, wspomnieniami, sukcesami lub pasjami. Tylko w IPLI nowy program, dzi\xc4\x99ki kt\xc3\xb3remu poznasz r\xc3\xb3\xc5\xbcne oblicza NAJlepszych, NAJciekawszych, NAJoryginalniejszych sportowc\xc3\xb3w!',
                'title': 'NAJZ...',
                'url': 'http://www.polsatsport.pl/program/najz/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/rn/rn1k1wiqepbbupk71sw6u4bg9ywvqb9x.jpg',
                'plot': 'Nowy program boksera i zawodnika MMA Przemys\xc5\x82awa Salety oraz komentatora sport\xc3\xb3w walki Jerzego Mielewskiego. W ka\xc5\xbcdym odcinku prowadz\xc4\x85cy zaprezentuj\xc4\x85 sylwetk\xc4\x99 odnosz\xc4\x85cego sukcesy boksera. Widzowie b\xc4\x99d\xc4\x85 mieli okazj\xc4\x99 pozna\xc4\x87 histori\xc4\x99 kariery zawodowej Tomasza Adamka, Krzysztofa &bdquo;Diablo&rdquo; W\xc5\x82odarczyka, Mike&rsquo;a Tysona czy Oskara de la Hoyi.',
                'title': 'Pi\xc4\x99\xc5\x9bciarze',
                'url': 'http://www.polsatsport.pl/program/piesciarze/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/nu/nuua357y1c5ciskg7pq19iutav1mxq8x.jpg',
                'plot': '',
                'title': 'Polska 2016 - Magazyn Pi\xc5\x82ki R\xc4\x99cznej',
                'url': 'http://www.polsatsport.pl/program/polska-2016-magazyn-pilki-recznej/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/3u/3uax93kys2g3uxtuctdzw2vt61bw9fcm.jpg',
                'plot': '&bdquo;Polska Liga Cudzoziemska&rdquo; to propozycja dla kibic\xc3\xb3w, kt\xc3\xb3rzy chcieliby pozna\xc4\x87 kulisy \xc5\xbcycia polskich sportowc\xc3\xb3w, wyst\xc4\x99puj\xc4\x85cych w barwach zagranicznych klub\xc3\xb3w. Odwiedzimy wielu z nich i b\xc4\x99dziemy \xc5\x9bwiadkami jednego dnia z \xc5\xbcycia poszczeg\xc3\xb3lnych os\xc3\xb3b towarzysz\xc4\x85c im w codziennych zaj\xc4\x99ciach domowo-rodzinnych oraz treningach lub wyst\xc4\x99pach w klubie.',
                'title': 'Polska Liga Cudzoziemska',
                'url': 'http://www.polsatsport.pl/program/polska-liga-cudzoziemska/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/2y/2y3ke55pagen5hdae7xv2v9vkzufmebn.jpg',
                'plot': 'Wszystko co powiniene\xc5\x9b wiedzie\xc4\x87 o sportach walki, \xc5\xbceby by\xc4\x87 na bie\xc5\xbc\xc4\x85co. Prowadz\xc4\x85cy Mateusz Borek wraz z zaproszonymi go\xc5\x9b\xc4\x87mi i ekspertami dyskutuj\xc4\x85 nie tylko o boksie zawodowym, ale i amatorskim. Zajmuj\xc4\x85 si\xc4\x99 tak\xc5\xbce tematami zwi\xc4\x85zanymi z MMA.',
                'title': 'Puncher',
                'url': 'http://www.polsatsport.pl/program/puncher/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/x5/x5npvv9qnx6w5853123xjow1iuc84gka.jpg',
                'plot': 'Jak wygl\xc4\x85da \xc5\xbcycie siatkarza na walizkach? Kto ma najwi\xc4\x99ksze poczucie humoru? Co robi\xc4\x85 siatkarze, jak nie graj\xc4\x85 i nie trenuj\xc4\x85? Zobacz koniecznie! Kadziu projekt oraz Ig\xc5\x82\xc4\x85 Szyte.',
                'title': 'Siatkarska Reprezentacja Inaczej',
                'url': 'http://www.polsatsport.pl/program/siatkarska-reprezentacja-inaczej/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/g9/g93drifcgpm58k2u9xk2fz5vbjyanu44.jpg',
                'plot': 'Aktualno\xc5\x9bci, relacje z konferencji, wywiady - to wszystko znajdziecie w sport news. Wiadomo\xc5\x9bci ze \xc5\x9bwiata sportu dla prawdziwych kibic\xc3\xb3w!',
                'title': 'Sport News',
                'url': 'http://www.polsatsport.pl/program/sport-news/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/e4/e42jii77qoowhugr8mhgs1cvmzpre2ea.jpg',
                'plot': 'Autorski program Bo\xc5\xbcydara Iwanowa, jednego z czo\xc5\x82owych komentator\xc3\xb3w mecz\xc3\xb3w pi\xc5\x82karskich, w kt\xc3\xb3rym przybli\xc5\xbca nam sylwetki prawdziwych facet\xc3\xb3w! Sportowcy, biznesmeni... Supermani!',
                'title': 'Superman',
                'url': 'http://www.polsatsport.pl/program/superman/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/4g/4gkhr26sse983xvq8dxwn4qb21i2jkor.jpg',
                'plot': 'Bokserskie pojedynki na s\xc5\x82owa! Szczero\xc5\x9b\xc4\x87, emocje, adrenalina. Oto konfrontacje pi\xc4\x99\xc5\x9bciarzy przed najwa\xc5\xbcniejszymi galami transmitowanymi na antenie Polsatu. Zawodnicy zaproszeni do naro\xc5\xbcnika siadaj\xc4\x85 twarz\xc4\x85 w twarz, mog\xc4\x85 spojrze\xc4\x87 sobie prosto w oczy i stoczy\xc4\x87 s\xc5\x82own\xc4\x85 walk\xc4\x99. Program prowadzi: Mateusz Borek',
                'title': 'W naro\xc5\xbcniku Polsatu',
                'url': 'http://www.polsatsport.pl/program/w-narozniku-polsatu/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/et/et4tryz11hv33duz9zxcbyoe2waee391.jpg',
                'plot': 'Program Przemys\xc5\x82awa Salety, w kt\xc3\xb3rym bokser przybli\xc5\xbcy widzom Polsat Play polsk\xc4\x85 scen\xc4\x99 sport\xc3\xb3w walki, takich jak: MMA, K1, boks, kickboxing. Sporty te, mimo i\xc5\xbc widowiskowe, nie s\xc4\x85 w naszym kraju powszechnie znane.&nbsp;</span><br /><span>W ka\xc5\xbcdym odcinku Przemys\xc5\x82aw Saleta przeprowadzi wywiad ze sportowcem, kt\xc3\xb3ry odnosi sukcesy w jednej z dyscyplin sport\xc3\xb3w walki, m.in. z Paw\xc5\x82em Nastul\xc4\x85, Marcinem R\xc3\xb3\xc5\xbcalskim, Markiem Piotrowskim czy Mamedem Khalidovem.',
                'title': 'Wojownicy',
                'url': 'http://www.polsatsport.pl/program/wojownicy/'},
                {'img': 'http://s.redefine.pl/dcs/o2/redefine/cp/wj/wj2h8s9pumnuc4r5yczso6t22aisntkf.jpg',
                'plot': 'Program, w kt\xc3\xb3rym prowadz\xc4\x85cy w zabawny spos\xc3\xb3b komentuj\xc4\x85 kr\xc3\xb3tkie filmy b\xc4\x99d\xc4\x85ce zapisem spektakularnych, ciekawych, czasem \xc5\x9bmiesznych, ale zazwyczaj nieudanych akcji sportowych ze \xc5\x9bwiata. Nie chc\xc4\x85c ogranicza\xc4\x87 si\xc4\x99 jedynie do pi\xc5\x82ki no\xc5\xbcnej, si\xc4\x99gaj\xc4\x85 po interesuj\xc4\x85ce zapisy dziwnych przypadk\xc3\xb3w w niemal wszystkich dziedzinach sportowych, wybieraj\xc4\x85c jedynie najzabawniejsze i najbardziej zaskakuj\xc4\x85ce z nich.',
                'title': 'Wysportowani',
                'url': 'http://www.polsatsport.pl/program/wysportowani/'}]
        return out


class segos(ExternalBase):
    def scanMainpage(self, url, page=1):
        if 'page=' in url:
            url = re.sub('page=\d+', 'page=%d' % int(page), url)
        else:
            url = url + '&page=%d' % page
        content = self.getUrl(url)

        nextPage = False
        next_url = url.replace(self.BASE_URLS[1], '').replace('page=%d' % page, 'page=%d' % (page + 1))
        if content.find(next_url.split('//')[-1]) > -1:
            nextPage = page + 1

        ids = [(a.start(), a.end()) for a in re.finditer('<div class="col-lg-3 col-md-3 col-sm-6 segos">', content)]
        ids.append((-1, -1))
        out = []
        lenght = len(ids[:-1])
        for i in range(lenght):
            subset = content[ids[i][1]:ids[i + 1][0]]

            href = re.compile('<a href="(.*?view.*?)"').findall(subset)
            title = re.compile('">(\w+.*?)</').findall(subset)

            img = re.compile('<img .*? img-glowna" src="(.*?)"').findall(subset)
            img = img[0] if img else ''
            if img.startswith('http'):
                img = img
            elif img.startswith('../'):
                img = img.replace('..', self.BASE_URLS[1])
            elif img.startswith('obrazki'):
                img = self.BASE_URLS[1] + '/' + img

            if href and title and img:
                info = {}
                if lenght <= 20:
                    info = self.getInfo(self.BASE_URLS[1] + href[0])
                one = {'url': self.BASE_URLS[1] + href[0],
                       'title': common.unicodePLchar(title[0]),
                       'img': img,
                       'code': info.get('code', ''),
                       'info': {'labels': info}
                       }
                out.append(one)

        prevPage = page - 1 if page > 1 else False
        return (out, (prevPage, nextPage))

    def getRecommended(self, type='movies', url='http://segos.es/recomend_list.php'):
        out = []
        content = self.getUrl(url)
        trs = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(content)
        lenght = len(trs)
        for tr in trs:
            href_title = re.compile('<p><a href="(.*?)">(.*?)</a></p>').findall(tr)
            img = re.compile('<img src="(.*?)"').findall(tr)
            if href_title:
                info = {}
                if lenght <= 20:
                    info = self.getInfo(self.BASE_URLS[1] + href_title[0][0])
                one = {'url': self.BASE_URLS[1] + href_title[0][0],
                       'title': common.unicodePLchar(href_title[0][1]),
                       'img': self.BASE_URLS[1] + img[0] if img else '',
                       'code': info.get('code', ''),
                       'info': {'labels': info}
                       }
                if type == 'cartoons' and '/bajki/' in href_title[0][0]:
                    out.append(one)
                if type == 'movies' and '/filmy/' in href_title[0][0]:
                    out.append(one)
        return out

    def getInfo(self, url, infoTab=True):
        info = {}
        if infoTab:
            content = self.getUrl(url)
            infx = content.find('<div id="myTabContent" class="tab-content">')
            if infx:
                subset = content[infx:-1]
                year = re.search('<b>Rok produkcji</b>:(.*?)<', subset, flags=re.MULTILINE | re.I)
                genre = re.search('<b>Gatunek</b>:(.*?)<', subset, flags=re.DOTALL)
                quality = re.search('<b>Jakość</b>:(.*?)<', subset, flags=re.MULTILINE | re.I)
                audio = re.search('<b>Audio</b>:(.*?)<', subset, flags=re.MULTILINE | re.I)
                lang = re.search('<b>Język</b>:(.*?)<', subset, flags=re.MULTILINE | re.I)
                plot = re.search('<b>Opis</b>:(.*?)<', subset, flags=re.MULTILINE | re.I)
                if year:    info['year'] = year.group(1).strip().strip('(').strip(')')
                if genre:   info['genre'] = genre.group(1).strip()
                if quality: info['quality'] = quality.group(1).strip()
                if audio:   info['audio'] = audio.group(1).strip()
                if lang:    info['lang'] = lang.group(1).strip()
                if plot:    info['plot'] = common.unicodePLchar(plot.group(1).strip())
                info['code'] = ','.join([info.get('quality', ''), info.get('lang', ''), info.get('audio', '')])

        return info

    def getVideoLinks(self, url):
        outL = []
        content = self.getUrl(url)
        iframes = re.compile('<iframe(.*?)</iframe>', re.DOTALL).findall(content)
        for iframe in iframes:
            href = re.compile('src="(.*?)"').findall(iframe)
            if href:
                link = href[0]
                host = urlparse.urlparse(link).netloc
                if 'greevid.com' in host:
                    link = self._getGreevid(link)
                    host += ' - ' + urlparse.urlparse(link).netloc
                if 'ebd.cda.pl' in host:
                    link = 'http://www.cda.pl/video/' + link.split('/')[-1]
                    host = urlparse.urlparse(link).netloc
            outL.append({'href': link, 'host': host})
        idx = content.find('Inne jakości')
        if idx:
            items = re.compile(
                '<div class="col-lg-1">(.*?)</div>[ \t\n]*<div class="col-lg-1">(.*?)</div>[ \t\n]*<div class="col-lg-7">(.*?)</div>[ \t\n]*<div class="col-lg-2">(.*?)</div>[ \t\n]*<div class="col-lg-1">(.*?)</div>',
                re.DOTALL).findall(content[idx:-1])
            if len(items) > 1:
                for item in items[1:]:
                    audio = re.compile('title="(.*)"').findall(item[0])
                    audio = '[COLOR green]%s[/COLOR]' % audio[0] if audio else ''
                    dzwiek = ' dźwięk:[B]%s[/B]' % item[1] if len(item[1]) else ''
                    quality = re.compile('\[(.*?)\]').findall(item[2])
                    quality = ' jakść:[B]%s[/B]' % quality[0] if quality else ''
                    link = re.compile('href="(.*?)"').findall(item[2])
                    if link:
                        link = 'http' + link[0].split('http')[-1]
                        if 'greevid.com' in link:
                            link = self._getGreevid(link)
                        host = urlparse.urlparse(link).netloc + '  ' + audio + dzwiek + quality
                        outL.append({'href': link, 'host': host})
        return outL

    def _getGreevid(self, url):
        content = self.getUrl(url)
        iframes = re.compile('<iframe(.*?)</iframe>', re.DOTALL).findall(content)
        if iframes:
            href = re.compile('src="(.*?)"').findall(iframes[0])
            if href:
                href = 'http' + href[0].split('http')[-1]
                return href
        return ''

    def getCategories(self, url='http://segos.es/filmy.php'):
        cat = []
        content = self.getUrl(url)
        idx = content.find('<h4>Kategorie</h4>')
        if idx:
            cat = re.compile('<li><a href="(.*?)">(.*?)</a></li>').findall(content[idx:-1])
            if cat:
                cat = [(self.BASE_URLS[1] + x[0], x[1].strip()) for x in cat]
        return cat

    def search(self, title):
        content = self.getUrl(self.BASE_URLS[1] + '/szukaj.php?title=' + urllib.quote_plus(title))
        ids = [(a.start(), a.end()) for a in re.finditer('<div class="col-lg-12" style="padding:0 0 5px 0;">', content)]
        ids.append((-1, -1))
        out = []
        lenght = len(ids[:-1])
        for i in range(lenght):
            subset = content[ids[i][1]:ids[i + 1][0]]
            href = re.compile('href="(.*?view.*?)"').findall(subset)
            title = re.compile('">(\w+.*?)</').findall(subset)
            img = re.compile('<img src="(.*?)"').findall(subset)
            img = img[0] if img else ''
            if img.startswith('http'):
                img = img
            elif img.startswith('../'):
                img = img.replace('..', self.BASE_URLS[1])
            elif img.startswith('obrazki'):
                img = self.BASE_URLS[1] + '/' + img
            elif img.startswith('/obrazki'):
                img = self.BASE_URLS[1] + img

            info = {}
            if lenght <= 20:
                info = self.getInfo(self.BASE_URLS[1] + href[0])

            if href and title and img:
                one = {'url': self.BASE_URLS[1] + href[0],
                       'title': common.unicodePLchar(title[0]),
                       'plot': '',
                       'img': img,
                       'rating': '',
                       'year': '',
                       'code': info.get('code', ''),
                       'info': {'labels': info}
                       }
                out.append(one)
        return out