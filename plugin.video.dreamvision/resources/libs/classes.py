# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin
import urlparse
import urlresolver
import xml.etree.ElementTree as et
import external
import common
import operator
import os

class menuItems:
    items = {}
    handlers = {}

    def addItem(self, name, url, method):
        self.items[name] = url
        self.handlers[url]= method

    def getItems(self):
        return self.items.items()

    def handleChoice(self, url, args):
        if url in self.items.values() and self.handlers.has_key(url):
            obj = eval(self.handlers[url]+'()')
            method = getattr(obj, 'handle')
            method(args.decode('base64') if args is not None else args)


class player:
    menuItems = menuItems()

    def __init__(self):
        self.menuItems.addItem('Telewizja', 'live_tv', 'liveTV')
        self.menuItems.addItem('Filmy', 'movies', 'movies')
        self.menuItems.addItem('Seriale', 'serials', 'serials')
        self.menuItems.addItem('Bajki', 'cartoons', 'cartoons')
        self.menuItems.addItem('Sport', 'sports', 'sports')
        self.menuItems.addItem('Rozrywka', 'fun', 'fun')
        common.addDir('[COLOR red]Z Podziekowaniem dla alien.tv i techmaniachd.pl - Nie kradnij to jest darmowe![/COLOR]', '' , isFolder = False, iconImage=common.getIcon('techmaniachd'))

    def getMenu(self):
        for name, url in self.menuItems.getItems():
            common.addDir(name, '?submenu=' + url, None, True, common.getIcon(url))

    def handleSubMenu(self, menu, args):
        self.menuItems.handleChoice(menu, args)
#
#
#
#
# PROVIDERS
#
#
#
#

class BajkiOnline:
    submenu = None
    bajkionline = None

    def __init__(self, submenu):
        self.bajkionline = external.bajkionline()
        self.submenu = submenu

    def _prepareInfos(self, serial):
        return {'labels':
            {
                'plot': serial.get('plot'),
            }
        }

    def getMovies(self, url, page):
        movies, page = self.bajkionline.getContent(url, page)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=bajkionline&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=self._prepareInfos(movie))
        if page[1]:
            common.addDir('Następna strona >>', '?submenu=' + self.submenu,
                          "provider=bajkionline&category=movies&option=" + str(page[1]) + "&page=" + str(
                              page[1].rpartition('/')[2]),
                          isPlayable=False, isFolder=True)

    def getLinks(self, url):
        link = self.bajkionline.getVideoLink(url)
        if 'cda' in link:
            resolver = external.cdaresolver()
            stream_url = resolver.getVideoUrls(link)
            if type(stream_url) is list:
                qualityList = [x[0] for x in stream_url]
                selection = xbmcgui.Dialog().select("Wybierz jakość", qualityList)
                if selection > -1:
                    stream_url = resolver.getVideoUrls(stream_url[selection][1])
                else:
                    stream_url = ''

        else:
            try:
                stream_url = urlresolver.resolve(link)
            except Exception, e:
                stream_url = ''
                xbmcgui.Dialog().ok(common.addonname, 'Może inny link będzie działał?',
                                    'UTRresolver ERROR: [%s]' % str(e))
        if stream_url:
            xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def getList(self, url):
        items = self.bajkionline.getList(url)
        for item in items:
            common.addDir(item.get('title'), '?submenu=' + self.submenu,
                          "provider=bajkionline&category=movies&option=" + item.get('url') + "&page=1",
                          isPlayable=False, isFolder=True, iconImage=item.get('img'))

    def getCategories(self, type='bpp'):
        if type == 'bpp':
            common.addDir('Główna', '?submenu=' + self.submenu,
                          "provider=bajkionline&category=movies&option=http://bajkipopolsku.com/&page=1",
                          isPlayable=False, isFolder=True)
            common.addDir('Lista', '?submenu=' + self.submenu,
                          "provider=bajkionline&category=list&option=http://bajkipopolsku.com/&page=1",
                          isPlayable=False, isFolder=True)
            common.addDir('Filmy', '?submenu=' + self.submenu,
                          "provider=bajkionline&category=movies&option=http://bajkipopolsku.com/category/fimly/page/1&page=1",
                          isPlayable=False, isFolder=True)
        else:
            common.addDir('Główna', '?submenu=' + self.submenu,
                          "provider=bajkionline&category=movies&option=http://bajkionline.com/&page=1",
                          isPlayable=False, isFolder=True)
            common.addDir('Lista', '?submenu=' + self.submenu,
                          "provider=bajkionline&category=list&option=http://bajkionline.com/&page=1",
                          isPlayable=False, isFolder=True)
            common.addDir('Filmy', '?submenu=' + self.submenu,
                          "provider=bajkionline&category=movies&option=http://bajkionline.com/category/filmy-animowane/&page=1",
                          isPlayable=False, isFolder=True)

    def handle(self, category, option, page):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'list':
            self.getList(option)
        elif category == 'categories':
            self.getCategories(option)



class Ekabaretypl:
    submenu = None
    eKabaretypl = None

    def __init__(self, submenu):
        self.eKabaretypl = external.ekabaretypl()
        self.submenu = submenu

    def _prepareInfos(self, serial):
        return {'labels':
            {
                'plot': serial.get('plot'),
            }
        }

    def getMovies(self, url):
        movies, page = self.eKabaretypl.getMovies(url)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu='+self.submenu,
                          'provider=ekabarety&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=self._prepareInfos(movie))
        if page[1]:
            common.addDir('Następna strona >>', '?submenu='+self.submenu,
                          "provider=ekabarety&category=movies&option=" + str(page[1]),
                          isPlayable=False, isFolder=True)

    def getLinks(self, url):
        link = self.eKabaretypl.getVideoUrl(url)
        stream_url = ''
        if link:
            if 'tvp.pl' in link:
                stream_url = self.eKabaretypl.tvpResove(link)
            else:
                try:
                    stream_url = urlresolver.resolve(link)
                except Exception, e:
                    stream_url = ''
                    xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', str(e))
        if stream_url:
            xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def getCategories(self, url):
        categories, page = self.eKabaretypl.getCategories(url)
        for category in categories:
            common.addDir(category.get("title"), '?submenu=' + self.submenu,
                          'provider=ekabarety&category=movies&option=' + category.get("url").encode('utf-8') + '',
                          isPlayable=False, isFolder=True, iconImage=category.get('img'), infos=category)
        if page[1]:
            common.addDir('Następna strona >>', '?submenu=' + self.submenu,
                          "provider=ekabarety&category=main&option=" + str(page[1]),
                          isPlayable=False, isFolder=True)

    def getMainCategories(self, type = None):
        if type == 'main':
            common.addDir('Skecze', '?submenu=' + self.submenu,
                          "provider=ekabarety&category=sketch",
                          isPlayable=False, isFolder=True)
            common.addDir('Kategorie', '?submenu=' + self.submenu,
                          "provider=ekabarety&category=categories",
                          isPlayable=False, isFolder=True)
        else:
            common.addDir('Kabarety', '?submenu=' + self.submenu,
                          'provider=ekabarety&category=main&option=http://www.ekabaret.pl/kabarety.html',
                          isPlayable=False, isFolder=True)
            common.addDir('Soliści', '?submenu=' + self.submenu,
                          'provider=ekabarety&category=main&option=http://www.ekabaret.pl/solisci.html',
                          isPlayable=False, isFolder=True)
            common.addDir('Grupy Impro', '?submenu=' + self.submenu,
                          'provider=ekabarety&category=main&option=http://www.ekabaret.pl/impro.html',
                          isPlayable=False, isFolder=True)
            common.addDir('Stand-up', '?submenu=' + self.submenu,
                          'provider=ekabarety&category=main&option=http://www.ekabaret.pl/standup.html',
                          isPlayable=False, isFolder=True)

    def getSkatchCategories(self):
        common.addDir('Top Lista', '?submenu=' + self.submenu,
                      'provider=ekabarety&category=movies&option=http://www.ekabaret.pl/toplista.html',
                      isPlayable=False, isFolder=True)
        common.addDir('Polecane', '?submenu=' + self.submenu,
                      'provider=ekabarety&category=movies&option=http://www.ekabaret.pl/polecane.html',
                      isPlayable=False, isFolder=True)
        common.addDir('Wywiady i relacje', '?submenu=' + self.submenu,
                      'provider=ekabarety&category=movies&option=http://www.ekabaret.pl/wywiady.html',
                      isPlayable=False, isFolder=True)

    def handle(self, category, option):
        if category == 'categories':
            self.getMainCategories(option)
        elif category == 'sketch':
            self.getSkatchCategories()
        elif category == 'main':
            self.getCategories(option)
        elif category == 'movies':
            self.getMovies(option)
        elif category == 'links':
            self.getLinks(option)


class Ekstraklasa:
    submenu = None
    ekstraKlasa = None

    def __init__(self, submenu):
        self.ekstraKlasa = external.ekstraklasa()
        self.submenu = submenu

    def getLinks(self, url):
        linksList = self.ekstraKlasa.getVideoLinks(url)
        stream_url = ''
        if len(linksList):
            if len(linksList) > 1:
                lables = [x.get('label') for x in linksList]
                s = xbmcgui.Dialog().select('Dostępne jakości', lables)
            else:
                s = 0
            stream_url = linksList[s].get('url') if s > -1 else ''
        if stream_url:
            xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def _prepareInfos(self, serial):
        return {'labels':
            {
                'plot': serial.get('plot'),
            }
        }

    def getMovies(self, url, page):
        movies, page = self.ekstraKlasa.getVideos('Ekstraklasa', url, page)
        for movie in movies:
            movie['code'] = movie.get('duration_formatted', '')
            movie['code'] = '[COLOR lightgreen]Nadaje[/COLOR]' if movie.get('onair', False) else movie['code']
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=ekstraklasa&category=links&option=' + movie.get("id"),
                          isPlayable=True, iconImage=movie.get('thumbnail_240_url'), infos={'labels': movie})
        if page[1]:
            common.addDir('Następna strona >>', '?submenu=' + self.submenu,
                          "provider=ekstraklasa&category=movies&option=Ekstraklasa&page=" + str(
                              page[1]),
                          isPlayable=False, isFolder=True)

    def getCategories(self):
        common.addDir('Live', '?submenu=' + self.submenu,
                      "provider=ekstraklasa&category=movies&option=live&page=1",
                      isPlayable=False, isFolder=True, iconImage=common.getIcon('icon'))
        common.addDir('Najnowsze', '?submenu=' + self.submenu,
                      "provider=ekstraklasa&category=movies&option=recent&page=1",
                      isPlayable=False, isFolder=True, iconImage=common.getIcon('icon'))
        common.addDir('Najpopularniejsze', '?submenu=' + self.submenu,
                      "provider=ekstraklasa&category=movies&option=visited&page=1",
                      isPlayable=False, isFolder=True, iconImage=common.getIcon('icon'))

    def handle(self, category, option, page):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'categories':
            self.getCategories()


class Estadios:
    submenu = None
    Estadios = None

    def __init__(self, submenu):
        self.Estadios = external.estadios()
        self.submenu = submenu

    def getLinks(self, url):
        link = self.Estadios.getVideoLinks(url)
        if link:
            if 'extragoals' in link:
                resolver = external.extragoalsresolver()
                stream_url = resolver.getVideoUrls(link)
            else:
                try:
                    stream_url = urlresolver.resolve(link)
                except Exception, e:
                    stream_url = ''
                    xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', str(e))
        if stream_url:
            xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def getMovies(self, url, page):
        movies = self.Estadios.getMatchShorts(url)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=estadios&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=movie)

    def getList(self):
        items = self.Estadios.getLigue()
        if items:
            label = [common.unicodePLchar(x[1].strip()) for x in items]
            value = [x[0].strip() for x in items]
            for t, v in zip(label, value):
                common.addDir(t, '?submenu=' + self.submenu,
                              "provider=estadios&category=movies&option=" + v,
                              isPlayable=False, isFolder=True)

    def getCategories(self):
        common.addDir('Skróty meczów', '?submenu=' + self.submenu,
                      "provider=estadios&category=list",
                      isPlayable=False, isFolder=True)

    def handle(self, category, option, page):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'list':
            self.getList()
        elif category == 'categories':
            self.getCategories()


class Footballorgin:
    submenu = None
    footballorgin = None

    def __init__(self, submenu):
        self.footballorgin = external.footballorgin()
        self.submenu = submenu

    def getLinks(self, url):
        streams = self.footballorgin.getVideos(url)
        if isinstance(streams, list):
            if len(streams) > 1:
                label = [x.get('title') for x in streams]
                s = xbmcgui.Dialog().select('Wybierz plik', label)
                link = streams[s].get('url') if s > -1 else ''
                msg = streams[s].get('msg', '')
            else:
                try:
                    link = streams[0].get('url')
                    msg = streams[0].get('msg', '')
                except:
                    link = ''
                    msg = 'Link not found at\n' + url
        else:
            msg = streams.get('msg', '')
            link = streams.get('url', '')
        if link:
            try:
                stream_url = urlresolver.resolve(link)
            except Exception, e:
                stream_url = ''
                xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', str(e))
            if stream_url:
                xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
            else:
                xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))
        else:
            xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', msg)
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def getMovies(self, url, page):
        movies, page = self.footballorgin.getContent(url, page)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=footballorgin&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=movie)
        if page[1]:
            common.addDir('Następna strona >>', '?submenu=' + self.submenu,
                          "provider=footballorgin&category=movies&option=" + str(
                              page[1].get('urlp', '') + "&page=" + str(page[1].get('page'))),
                          isPlayable=False, isFolder=True)

    def getList(self):
        items = self.footballorgin.getMain()
        for item in items:
            common.addDir(item.get('title'), '?submenu=' + self.submenu,
                          "provider=footballorgin&category=movies&option=" + item.get('url'),
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('footballorgin'))

    def handle(self, category, option, page):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'list':
            self.getList()


class Goalsarena:
    submenu = None
    goalsarena = None

    def __init__(self, submenu):
        self.goalsarena = external.goalsarena()
        self.submenu = submenu

    def getLinks(self, url):
        streams = self.goalsarena.getVideos(url)
        if isinstance(streams, list):
            if len(streams) > 1:
                label = [x.get('title') for x in streams]
                s = xbmcgui.Dialog().select('Wybierz plik', label)
                link = streams[s].get('url') if s > -1 else ''
                msg = streams[s].get('msg', '')
            else:
                try:
                    link = streams[0].get('url')
                    msg = streams[0].get('msg', '')
                except:
                    link = ''
                    msg = 'Link not found at\n' + url
        else:
            msg = streams.get('msg', '')
            link = streams.get('url', '')
        if link:
            try:
                stream_url = urlresolver.resolve(link)
            except Exception, e:
                stream_url = ''
                xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', str(e))
            if stream_url:
                xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
            else:
                xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))
        else:
            xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', msg)
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def getMovies(self, url, page):
        movies, page = self.goalsarena.getContent(url)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=goalsarena&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=movie)
        if page[1]:
            common.addDir('Następna strona >>', '?submenu=' + self.submenu,
                          "provider=goalsarena&category=movies&option=" + str(page[1].get('urlp', '')),
                          isPlayable=False, isFolder=True)

    def getList(self):
        items = self.goalsarena.getMain()
        for item in items:
            common.addDir(item.get('title'), '?submenu=' + self.submenu,
                          "provider=goalsarena&category=movies&option=" + item.get('url'),
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('goalsarena'))

    def handle(self, category, option, page):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'list':
            self.getList()



class Iitv:
    iitv = None
    submenu = None

    def __init__(self, submenu):
        self.iitv = external.Iitv()
        self.submenu = submenu

    def _prepareInfos(self, serial):
        return {'labels':
            {
                'plot': serial.get('plot'),
                'genre': str(time.ctime(float(serial.get('data'))))
            }
        }

    def getLatest(self, url):
        serials, page = self.iitv.getSerials(url)
        for serial in serials:
            common.addDir(serial.get("title").encode('utf-8'), '?submenu=' + self.submenu,
                          'provider=iitv&category=links&option=' + serial.get("url").encode('utf-8') + '',
                          isPlayable=True,
                          iconImage=serial.get('img'), infos=self._prepareInfos(serial))
        if page[1]:
            common.addDir('Następna strona >>', '?submenu=' + self.submenu,
                          "provider=iitv&category=latest&option=" + str(page[1]),
                          isPlayable=False, isFolder=True)

    def getSerials(self, category):
        if category == 'list':
            serials = self.iitv.getList()
        else:
            serials = self.iitv.getPopular()
        for serial in serials:
            common.addDir(serial.get('title'), '?submenu=serials',
                          'provider=iitv&category=episodes&option=' + serial.get("url").encode('utf-8'), isPlayable=False,
                          isFolder=True)

    def getEpisodes(self, url):
        episodes = self.iitv.getEpisodes(url)
        for f in episodes:
            common.addDir(f.get('title'), '?submenu=serials',
                          'provider=iitv&category=links&option=' + f.get("url").encode('utf-8'),
                          isPlayable=True)

    def getLinks(self, url):
        linksList = self.iitv.getLinks(url)
        stream_url = ''
        if len(linksList):
            lables = [x.get('title') for x in linksList]
            s = xbmcgui.Dialog().select('Linki', lables)
            link = linksList[s].get('url') if s > -1 else ''
            if link:
                link = self.iitv.getHostUrl(link)
                try:
                    stream_url = urlresolver.resolve(link)
                except Exception, e:
                    stream_url = ''
                    xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', str(e))
        if stream_url:
            xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def getCategories(self):
        common.addDir("Ostatnio dodane", '?submenu=' + self.submenu,
                      "provider=iitv&category=latest&option=1", isFolder=True)
        common.addDir("Popularne", '?submenu=' + self.submenu,
                      "provider=iitv&category=serials&soption=popular", isFolder=True)
        common.addDir("Wszystkie", '?submenu=' + self.submenu,
                      "provider=iitv&category=serials&option=list", isFolder=True)

    def handle(self, category, option):
        if category == 'latest':
            self.getLatest(option)
        elif category == 'serials':
            self.getSerials(option)
        elif category == 'episodes':
            self.getEpisodes(option)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'categories':
            self.getCategories()


class Laczynaspilka:
    submenu = None
    laczynaspilka = None

    def __init__(self, submenu):
        self.laczynaspilka = external.laczynaspilka()
        self.submenu = submenu

    def getLinks(self, url):
        streams = self.laczynaspilka.getVideos(url)
        if isinstance(streams,list):
            if len(streams)>1:
                label = [x.get('title') for x in streams]
                s = xbmcgui.Dialog().select('Wybierz plik',label)
                link = streams[s].get('url') if s>-1 else ''
                msg = streams[s].get('msg','')
            else:
                try:
                    link = streams[0].get('url')
                    msg = streams[0].get('msg','')
                except:
                    link = ''
                    msg = 'Link not found at\n'+url
        else:
            msg = streams.get('msg','')
            link = streams.get('url','')
        if link:
            try:
                stream_url = urlresolver.resolve(link)
            except Exception,e:
                stream_url=''
                xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]',str(e))
            if stream_url: xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
            else: xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))
        else:
            xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]',msg)
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))


    def getMovies(self, url, page):
        movies, page = self.laczynaspilka.getContent(url)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=laczynaspilka&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=movie)
        if page[1]:
            common.addDir('Następna strona >>', '?submenu='+self.submenu,
                          "provider=laczynaspilka&category=movies&option=" + str(page[1].get('urlp','')),
                          isPlayable=False, isFolder=True)

    def getList(self):
        items = self.laczynaspilka.getMain()
        for item in items:
            common.addDir(item.get('title'), '?submenu=' + self.submenu,
                          "provider=laczynaspilka&category=movies&option=" + item.get('url'),
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('laczynaspilka'))

    def handle(self, category, option, page):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'list':
            self.getList()


class Lechtv:
    submenu = None
    lechtv = None

    def __init__(self, submenu):
        self.lechtv = external.lechtv()
        self.submenu = submenu

    def getLinks(self, url):
        stream_url = self.lechtv.getVideos(url)
        stream_url=stream_url.get('url',False)
        if stream_url: xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else: xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))


    def getMovies(self, url, type, page):
        isPlayable = True
        if url=='table':
            movies = self.lechtv.getExtraclassTable()
            isPlayable = False
        else:
            movies, page = self.lechtv.getContent(url, page, type)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=lechtv&category=links&option=' + movie.get("url",'') + '',
                          isPlayable=isPlayable, iconImage=movie.get('img'), infos=movie)
        if isinstance(page, list):
            common.addDir('Następna strona >>', '?submenu='+self.submenu,
                          "provider=lechtv&category=movies&option=" + str(page[1]),
                          isPlayable=False, isFolder=True)

    def getCategories(self):
        common.addDir('TABELA EKSTRAKLASY', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=table",
                      isPlayable=False, isFolder=True)
        common.addDir('Nowe', '?submenu='+self.submenu,
                          "provider=lechtv&category=movies&option=newest",
                          isPlayable=False, isFolder=True)
        common.addDir('Popularne', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=popular",
                      isPlayable=False, isFolder=True)
        common.addDir('Pierwsza Drużyna', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=category&type=3",
                      isPlayable=False, isFolder=True)
        common.addDir('Skróty Meczów', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=category&type=7",
                      isPlayable=False, isFolder=True)
        common.addDir('Wywiady', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=category&type=1",
                      isPlayable=False, isFolder=True)
        common.addDir('Konferencje Prasowe', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=category&type=2",
                      isPlayable=False, isFolder=True)
        common.addDir('Rezerwy', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=category&type=4",
                      isPlayable=False, isFolder=True)
        common.addDir('Akademia', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=category&type=5",
                      isPlayable=False, isFolder=True)
        common.addDir('Oldboje', '?submenu=' + self.submenu,
                      "provider=lechtv&category=movies&option=category&type=6",
                      isPlayable=False, isFolder=True)

    def handle(self, category, option, page, type):
        if category == 'movies':
            self.getMovies(option, type, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'categories':
            self.getCategories()



class Livefootballol:
    submenu = None
    livefootballol = None

    def __init__(self, submenu):
        self.livefootballol = external.livefootballol()
        self.submenu = submenu

    def getLinks(self, url):
        streams = self.livefootballol.getVideos(url)
        if isinstance(streams,list):
            if len(streams)>1:
                label = [x.get('title') for x in streams]
                s = xbmcgui.Dialog().select('Wybierz plik',label)
                link = streams[s].get('url') if s>-1 else ''
                msg = streams[s].get('msg','')
            else:
                try:
                    link = streams[0].get('url')
                    msg = streams[0].get('msg','')
                except:
                    link = ''
                    msg = 'Link not found at\n'+url
        else:
            msg = streams.get('msg','')
            link = streams.get('url','')
        if link:
            try:
                stream_url = urlresolver.resolve(link)
            except Exception,e:
                stream_url=''
                xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]',str(e))
            if stream_url: xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
            else: xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))
        else:
            xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]',msg)
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))


    def getMovies(self, url, page):
        movies, page = self.livefootballol.getContent(url)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=livefootballol&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=movie)
        if page[1]:
            common.addDir('Następna strona >>', '?submenu='+self.submenu,
                          "provider=livefootballol&category=movies&option=" + str(page[1].get('urlp','')),
                          isPlayable=False, isFolder=True)

    def getList(self):
        items = self.livefootballol.getMain()
        for item in items:
            common.addDir(item.get('title'), '?submenu=' + self.submenu,
                          "provider=livefootballol&category=movies&option=" + item.get('url'),
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('livefootballol'))

    def handle(self, category, option, page):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'list':
            self.getList()



class KinoHd:
    dataFile = common.moviesDataFilePath
    contents = None
    objects = []
    movies = {}
    submenu = None

    def __init__(self, submenu):
        self.submenu = submenu

    def _loadFile(self):
        common.checkMoviesDataFile()
        if os.path.isfile(self.dataFile):
            self.contents = et.fromstring(common.decryptFile(self.dataFile))
            return True
        xbmc.log('failed to load data file')
        return False

    def _sortChildrenBy(self, parent, attr):
        parent[:] = sorted(parent, key=lambda child: child.get(attr))
        return parent

    def _sortMovies(self, tag):
        if tag == 'year':
            self.objects.sort(reverse=True)
        else:
            self.objects.sort()

        if tag == 'title':
            self.movies = sorted(self.movies.items(), key=operator.itemgetter(0))
        else:
            for movie in self.movies:
                items = []
                items.append(sorted(self.movies[movie], key=operator.itemgetter('title')))
                self.movies[movie] = items

    def _parseFolderInfos(self, folder):
        return [{
            'title': folder.get('title'),
            'img': folder.get('poster'),
            'infos': {
                'labels': {
                    'year': folder.get('premiered'),
                    'plor': folder.get('plot'),
                    'genre': folder.get('genre'),
                    'rating': folder.get('rating')
                }
            }
            }
        ]

    def _decodeUrl(self, url):
        return eval(url) if '[' in url else eval(('5' + url).decode('hex'))

    def _parseSerialsDir(self, main = None, subcat = None, type='serials'):
        if self.contents is None:
            self._loadFile()
        folders = self.contents.find(type)
        folders = self._sortChildrenBy(folders, 'title')
        if main is None or main == '':
            for folder in folders.findall('folder'):
                if folder.get('name') is not None:
                    common.addDir(folder.get('title'), '?submenu=' + self.submenu,
                                  "provider=kinohd&category="+type+"&option=" + folder.get('name').encode('utf-8'), isFolder=True,
                                  iconImage=folder.get('poster'), infos=self._parseFolderInfos(folder))
                else:
                    common.addDir(folder.get('title'), '?submenu=' + self.submenu,
                                  "provider=kinohd&category="+type+"&option=" + folder.get(
                                      'title').encode('utf-8'), isFolder=True,
                                  infos=self._parseFolderInfos(folder))
        elif main is not None and main != '':
            for folder in folders.findall('folder'):
                if folder.get('name') is not None:
                    if folder.get('name').encode('utf-8') == main:
                        if subcat is None or subcat == '':
                            for subDir in folder.findall('folder'):
                                common.addDir(subDir.get('title'), '?submenu=' + self.submenu,
                                              "provider=kinohd&category="+type+"&option=" + folder.get(
                                                  'name') + '&subcat=' + subDir.get('title'), isFolder=True,
                                              infos=self._parseFolderInfos(folder))
                        else:
                            for subDir in folder.findall('folder'):
                                if subDir.get('title').encode('utf-8') == subcat:
                                    self.contents = subDir
                                    self.getMovies('title', '')
                                    break

                        break
                elif folder.get('title').encode('utf-8') == main:
                    self.contents = folder
                    self.getMovies('title', '')
                    break

    def _parseObjects(self, tag):
        if self.contents is None:
            self._loadFile()
            contents = self.contents.find('movies')
            if tag == 'title':
                series = self.contents.find('series')
                folders=series.findall('folder')
                for folder in folders:
                    contents.extend(folder)
            self.contents = contents
        if self.contents is not None:
            for movie in self.contents.findall('movie'):
                if tag == 'title':
                    objects = [movie.get(tag)]
                else:
                    objects = movie.get(tag).split(',')
                for obj in objects:
                    obj = obj.encode('utf-8')
                    if obj == '':
                        obj = 'Brak tagu'

                    if tag == 'title':
                        obj.strip()
                    if obj not in self.objects:
                        self.objects.append(obj)
                        self.movies[obj] = []
                    self.movies[obj].append({
                        'title': movie.get('title').strip(),
                        'img': movie.get('img'),
                        'urls': movie.get('links'),
                        'infos': {
                            'trailer': movie.get('trailer'),
                            'labels': {
                                'year': movie.get('year'),
                                'studio': movie.get('studio'),
                                'plot': movie.get('plot'),
                                'code': movie.get('code'),
                                'duration': movie.get('duration'),
                                'filmweb': movie.get('filmweb'),
                                'genre': movie.get('genre'),
                                'rating': movie.get('rating')
                            }
                        }})
            self._sortMovies(tag)

    def getMovies(self, tag, subcat, page = 1):
        page = int(page)
        next = page + 1
        begin = (page - 1) * 30
        end = page * 30

        if len(self.objects) == 0:
            self._parseObjects(tag)

        if subcat == '':
            mainDB = db = self.movies
            end = len(db)
        else:
            mainDB = self.movies[subcat][0]
            db = mainDB[begin:end]
        for movie in db:
            if subcat == '':
                lnk = movie[1][0]
            else:
                lnk = movie
            common.addDir(lnk['title'], '?submenu='+self.submenu, "provider=kinohd&category=play&option=" + lnk['urls'], False,
                          lnk['img'],
                          isPlayable=True, infos=lnk['infos'])
        if len(mainDB)-end > 1:
            common.addDir('Następna strona >>', '?submenu='+self.submenu, "provider=kinohd&category=movies&option="+tag+"&subcat="+subcat+"&page=" + str(next),
                          isPlayable=False, isFolder=True)

    def getMoviesSubCategories(self, tag):
        if len(self.objects) == 0:
            self._parseObjects(tag)
        common.addDir("[COLOR yellow]=> SZUKAJ <=[/COLOR]", '?submenu=' + self.submenu,
                      "provider=kinohd&category=search",
                      isFolder=True)
        for obj in self.objects:
            common.addDir(obj, '?submenu='+self.submenu, "provider=kinohd&category=movies&option=" + tag + "&subcat="+obj, True)

    def getUrl(self, url):
        links = self._decodeUrl(url)
        stream_url = common.resolveURL(links)
        if stream_url:
            xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def getSearchMovies(self, found, title, page):
        page = int(page)
        next = page + 1
        begin = (page-1) * 30
        end = page * 30
        for movie in found[begin:end]:
            common.addDir(movie['title'], '?submenu='+self.submenu, "provider=kinohd&category=play&option=" + movie['urls'], False,
                          movie['img'],
                          isPlayable=True, infos=movie['infos'])
        if len(found)-end > 1:
            common.addDir('Następna strona >>', '?submenu='+self.submenu, "provider=kinohd&category=search&option="+title+"&page=" + str(next),
                          isPlayable=False, isFolder=True)

    def search(self, title, page):
        if title == '':
            title = xbmcgui.Dialog().input(common.addonname+':: Podaj tytuł', type=xbmcgui.INPUT_ALPHANUM)
        if len(self.objects) == 0:
            self._parseObjects('title')
        found = []
        for movie in self.movies:
            movieTitleLower = movie[0].lower()
            titleLower = title.lower()
            if titleLower in movieTitleLower or titleLower == movieTitleLower:
                found.append(movie[1][0])
        if(len(found) > 0):
            self.getSearchMovies(found, title, page)

    def getMoviesCategories(self):
        common.addDir("[COLOR yellow]=> SZUKAJ <=[/COLOR]", '?submenu=' + self.submenu,
                      "provider=kinohd&category=search",
                      isFolder=True)
        common.addDir('Gatunki', '?submenu=' + self.submenu,
                      "provider=kinohd&category=subcategories&option=genre",
                      isPlayable=False, isFolder=True)
        common.addDir('Rok', '?submenu=' + self.submenu,
                      "provider=kinohd&category=subcategories&option=year",
                      isPlayable=False, isFolder=True)
        common.addDir('Serie', '?submenu=' + self.submenu,
                      "provider=kinohd&category=series",
                      isPlayable=False, isFolder=True)
        common.addDir('Wszystkie', '?submenu=' + self.submenu,
                      "provider=kinohd&category=movies&option=title",
                      isPlayable=False, isFolder=True)

    def getMainCategories(self):
        common.addDir('Filmy', '?submenu=' + self.submenu,
                      "provider=kinohd&category=moviesCategories",
                      isPlayable=False, isFolder=True)
        common.addDir('Seriale', '?submenu=' + self.submenu,
                      "provider=kinohd&category=serials",
                      isPlayable=False, isFolder=True)

    def handle(self, category, option, page, subcat):
        if category == 'movies':
            self.getMovies(option, subcat, page)
        elif category == 'moviesCategories':
            self.getMoviesCategories()
        elif category == 'main':
            self.getMainCategories()
        elif category == 'subcategories':
            self.getMoviesSubCategories(option)
        elif category == 'play':
            self.getUrl(option)
        elif category == 'search':
            self.search(option, page)
        elif category == 'serials':
            self._parseSerialsDir(option, subcat)
        elif category == 'series':
            self._parseSerialsDir(option, subcat, 'series')



class NaszeKino:
    naszeKino = None
    submenu = None
    paginationUrl = None

    def __init__(self, submenu, paginationUrl):
        self.naszeKino = external.naszekino()
        self.submenu = submenu
        self.paginationUrl = paginationUrl

    def _prepareInfos(self, serial):
        return {'labels':
            {
                'plot': serial.get('plot'),
            }
        }

    def getMovies(self, type='main', url=None):
        category = 'links'
        isFolder = False
        isPlayable = True
        if type == 'thread':
            movies, page = self.naszeKino.getForumEntry(url)
        else:
            movies, page = self.naszeKino.getForum()
            if url is not None and isinstance(int(url), int):
                movies, page = self.naszeKino.getForumEntry(movies[int(url)].get('url'))
            else:
                type = 'thread'
                category = 'movies'
                isFolder = True
                isPlayable = False
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=naszekino&category=' + category + '&option=' + movie.get("url") + "&type=" + type,
                          isPlayable=isPlayable, isFolder=isFolder, iconImage=movie.get('img'),
                          infos=self._prepareInfos(movie))
        if page[1]:
            common.addDir('Następna strona >>', '?submenu=' + self.submenu,
                          "provider=naszekino&category=movies&option=" + self.paginationUrl + str(
                              page[1].get('url', '')) + "&type=thread",
                          isPlayable=False, isFolder=True)

    def getThreadLinks(self, url):
        items = self.naszeKino.getThreadLinks(url)
        links = [x.get('title') for x in items]
        selection = xbmcgui.Dialog().select("Wybierz link", links)
        if selection > -1:
            link = items[selection].get('url')
            self.getLinks(link)

    def getLinks(self, url):
        if 'cda' in url:
            resolver = external.cdaresolver()
            stream_url = resolver.getVideoUrls(url)
            if type(stream_url) is list:
                qualityList = [x[0] for x in stream_url]
                selection = xbmcgui.Dialog().select("Wybierz jakość", qualityList)
                if selection > -1:
                    stream_url = resolver.getVideoUrls(stream_url[selection][1])
                else:
                    stream_url = ''
        else:
            try:
                stream_url = urlresolver.resolve(url)
            except:
                stream_url = ''
                xbmcgui.Dialog().ok(common.addonname, 'Nie odnaleziono pliku.','Może inny link będzie działał?')
        if stream_url:
            xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def handle(self, category, option, type):
        if category == 'movies':
            self.getMovies(type, option)
        elif category == 'links':
            self.getThreadLinks(option)


class Polsatsport:
    submenu = None
    polsatsport = None

    def __init__(self, submenu):
        self.polsatsport = external.polsatsport()
        self.submenu = submenu

    def getLinks(self, url):
        stream_url = self.polsatsport.getVideos(url)
        stream_url=stream_url.get('url',False)
        if stream_url: xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else: xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))


    def getMovies(self, url, page):
        movies, page = self.polsatsport.getContentVideos(url)
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=polsatsport&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=movie)
        if page[1]:
            common.addDir('Następna strona >>', '?submenu='+self.submenu,
                          "provider=polsatsport&category=movies&option=" + str(page[1]),
                          isPlayable=False, isFolder=True)

    def getList(self, type):
        items = self.polsatsport.getContentDir(type)
        for item in items:
            common.addDir(item.get('title'), '?submenu=' + self.submenu,
                          "provider=polsatsport&category=movies&option=" + item.get('url'),
                          isPlayable=False, isFolder=True, iconImage=item.get('img'))

    def getCategories(self):
        common.addDir('Magazyny', '?submenu='+self.submenu,
                          "provider=polsatsport&category=list&option=magazyny",
                          isPlayable=False, isFolder=True)
        common.addDir('Dyscypliny', '?submenu='+self.submenu,
                          "provider=polsatsport&category=list&option=dyscypliny",
                          isPlayable=False, isFolder=True)

    def handle(self, category, option, page):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'list':
            self.getList(option)
        elif category == 'categories':
            self.getCategories()



class Segos:
    segos = None
    submenu = None
    paginationUrl = None

    def __init__(self, submenu, paginationUrl):
        self.segos = external.segos()
        self.submenu = submenu
        self.paginationUrl = paginationUrl

    def getMovies(self, url, page, recommended = False, type = 'movies'):
        if recommended:
            movies = self.segos.getRecommended(type)
        else:
            movies, page = self.segos.scanMainpage(url, int(page))
        for movie in movies:
            common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                          'provider=segos&category=links&option=' + movie.get("url").encode('utf-8') + '',
                          isPlayable=True, iconImage=movie.get('img'), infos=movie.get('info'))
        if isinstance(page, list):
            common.addDir('Następna strona >>', '?submenu=' + self.submenu,
                          "provider=segos&category=movies&option=" + self.paginationUrl + str(page[1]) + "&page=" + str(
                              page[1]),
                          isPlayable=False, isFolder=True)

    def getCategories(self, type = None):
        common.addDir("[COLOR yellow]=> SZUKAJ <=[/COLOR]", '?submenu=' + self.submenu,
                      "provider=segos&category=search",
                      isFolder=True)
        if type == 'cartoons':
            common.addDir("Główna", '?submenu='+self.submenu,
                          "provider=segos&category=movies&option=http://segos.es/bajki.php?page=1&page=1",
                          isPlayable=False, isFolder=True)
            common.addDir("Polecane", '?submenu='+self.submenu,
                          "provider=segos&category=recommended&option=http://segos.es/bajki.php?page=1&page=1",
                          isPlayable=False, isFolder=True)

        elif type == 'movies':
            common.addDir("Główna", '?submenu='+self.submenu,
                          "provider=segos&category=movies&option=http://segos.es/filmy.php?page=1&page=1",
                          isFolder=True)
            common.addDir("Kategorie", '?submenu='+self.submenu,
                          "provider=segos&category=categories&option=http://segos.es/filmy.php?page=1&page=1",
                          isFolder=True)
            common.addDir("Polecane", '?submenu=' + self.submenu,
                          "provider=segos&category=recommended&option=http://segos.es/filmy.php?page=1&page=1",
                          isFolder=True)
        else:
            categories = self.segos.getCategories()
            for url, name in categories:
                common.addDir(name, '?submenu=' + self.submenu,
                              'provider=segos&category=movies&option=' + url + '',
                              isPlayable=False, isFolder=True)


    def getLinks(self, url):
        linksList = self.segos.getVideoLinks(url)
        stream_url = ''
        if len(linksList):
            if len(linksList) > 1:
                lables = [x.get('host') for x in linksList]
                s = xbmcgui.Dialog().select('Wybierz host', lables)
            else:
                s = 0

            link = linksList[s].get('href') if s > -1 else ''
            host = linksList[s].get('host') if s > -1 else ''
            if 'cda' in host:
                resolver = external.cdaresolver()
                stream_url = resolver.getVideoUrls(link)
                if type(stream_url) is list:
                    qualityList = [x[0] for x in stream_url]
                    selection = xbmcgui.Dialog().select("Wybierz jakość", qualityList)
                    if selection > -1:
                        stream_url = resolver.getVideoUrls(stream_url[selection][1])
                    else:
                        stream_url = ''
            elif 'rapidvideo' in host:
                resolver = external.rapidvideresolver()
                stream_url = resolver.getVideoUrls(link)
                if type(stream_url) is list:
                    if len(stream_url) == 1:
                        stream_url = stream_url[0][1]
                    else:
                        qualityList = [x[0] for x in stream_url]
                        selection = xbmcgui.Dialog().select("Wybierz jakość", qualityList)
                        if selection > -1:
                            stream_url = stream_url[selection][1]
                        else:
                            try:
                                stream_url = urlresolver.resolve(link)
                            except:
                                stream_url = ''

            elif link:
                try:
                    stream_url = urlresolver.resolve(link)
                except Exception, e:
                    stream_url = ''
                    xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', str(e))
        if stream_url:
            xbmcplugin.setResolvedUrl(common.addon_handle, True, xbmcgui.ListItem(path=stream_url))
        else:
            xbmcplugin.setResolvedUrl(common.addon_handle, False, xbmcgui.ListItem(path=''))

    def search(self):
        title = xbmcgui.Dialog().input(common.addonname+':: Podaj tytuł', type=xbmcgui.INPUT_ALPHANUM)
        if title:
            movies = self.segos.search(title)
            for movie in movies:
                common.addDir(movie.get("title"), '?submenu=' + self.submenu,
                              'provider=segos&category=links&option=' + movie.get("url").encode('utf-8') + '',
                              isPlayable=True, iconImage=movie.get('img'), infos=movie.get('info'))

    def handle(self, category, option, page, type):
        if category == 'movies':
            self.getMovies(option, page)
        elif category == 'recommended':
            self.getMovies(option, page, True, type)
        elif category == 'links':
            self.getLinks(option)
        elif category == 'categories':
            self.getCategories(option)
        elif category == 'search':
            self.search()

#
#
#
#
#   HANDLERS
#
#
#
#


class cartoons:
    submenu = 'cartoons'
    bajkionline = None
    segos = None
    naszeKino = None

    def __init__(self):
        self.bajkionline = BajkiOnline(self.submenu)
        self.segos = Segos(self.submenu, 'http://segos.es/bajki.php?page=')
        self.naszeKino = NaszeKino(self.submenu, '')

    def handle(self, args):
        xbmcplugin.setContent(common.addon_handle, 'movies')
        provider = None
        if args is not None:
            args = urlparse.parse_qs(args)
            provider = args.get('provider')
            category = args.get('category')
            option = args.get('option', [''])[0]
            page = args.get('page', [1])[0]

        if provider is None:
            common.addDir("BAJKI PO POLSKU", '?submenu=' + self.submenu,
                          "provider=bajkionline&category=categories&option=bpp",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('bajkionline'))
            common.addDir("BAJKI ONLINE", '?submenu=' + self.submenu,
                          "provider=bajkionline&category=categories&option=bo",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('bajkionline'))
            common.addDir("SEGOS", '?submenu=' + self.submenu,
                          "provider=segos&category=categories&option=cartoons",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('segos'))
            common.addDir("NASZE KINO", '?submenu='+self.submenu,
                          "provider=naszekino&category=movies&option=4&type=main",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('naszekino'))
        elif provider[0] == 'bajkionline':
            self.bajkionline.handle(category[0], option, page)
        elif provider[0] == 'segos':
            self.segos.handle(category[0], option, page, 'cartoons')
        elif provider[0] == 'naszekino':
            type = args.get('type')
            self.naszeKino.handle(category[0], option, type[0])

        xbmcplugin.endOfDirectory(common.addon_handle)


class fun:
    submenu = 'fun'
    naszeKino = None
    ekabarety = None

    def __init__(self):
        self.naszeKino = NaszeKino(self.submenu, '')
        self.ekabarety = Ekabaretypl(self.submenu)

    def handle(self, args):
        xbmcplugin.setContent(common.addon_handle, 'movies')
        provider = None
        if args is not None:
            args = urlparse.parse_qs(args)
            provider = args.get('provider')
            category = args.get('category')
            option = args.get('option', [''])[0]
            page = args.get('page', [1])[0]

        if provider is None:
            common.addDir("EKABARET", '?submenu=' + self.submenu,
                          "provider=ekabarety&category=categories&option=main",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('ekabaret'))
            common.addDir("NASZE KINO", '?submenu='+self.submenu,
                          "provider=naszekino&category=movies&option=2&type=main",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('naszekino'))
        elif provider[0] == 'naszekino':
            type = args.get('type')
            self.naszeKino.handle(category[0], option, type[0])
        elif provider[0] == 'ekabarety':
            self.ekabarety.handle(category[0], option)

        xbmcplugin.endOfDirectory(common.addon_handle)


class movies:
    submenu = 'movies'
    segos = None
    naszeKino = None
    kinoHd = None

    def __init__(self):
        self.segos = Segos(self.submenu, 'http://segos.es/filmy.php?page=')
        self.naszeKino = NaszeKino(self.submenu, '')
        self.kinoHd = KinoHd(self.submenu)

    def handle(self, args):
        xbmcplugin.setContent(common.addon_handle, 'movies')
        provider = None

        if args is not None:
            args = urlparse.parse_qs(args)
            provider = args.get('provider')
            category = args.get('category', None)
            option = args.get('option', [''])[0]
            page = args.get('page', [1])[0]

        if provider is None:
            common.addDir("SEGOS", '?submenu=' + self.submenu,
                          "provider=segos&category=categories&option=movies", isFolder=True, iconImage=common.getIcon('segos'))
            common.addDir("NASZE KINO", '?submenu='+self.submenu,
                          "provider=naszekino&category=movies&option=0&type=main", isFolder=True, iconImage=common.getIcon('naszekino'))
            common.addDir("KINO HD", '?submenu='+self.submenu,
                          "provider=kinohd&category=moviesCategories", isFolder=True, iconImage=common.getIcon('kinohd'))
        elif provider[0] == 'segos':
            self.segos.handle(category[0], option, page, 'movies')
        elif provider[0] == 'naszekino':
            type = args.get('type')
            self.naszeKino.handle(category[0], option, type[0])
        elif provider[0] == 'kinohd':
            subcat = args.get('subcat', [''])[0]
            self.kinoHd.handle(category[0], option, page, subcat)

        xbmcplugin.endOfDirectory(common.addon_handle)


class serials:
    submenu = 'serials'
    iitv = None
    naszeKino = None
    segos = None
    kinoHd = None

    def __init__(self):
        self.iitv = Iitv(self.submenu)
        self.segos = Segos(self.submenu, 'http://segos.es/bajki.php?page=')
        self.naszeKino = NaszeKino(self.submenu, '')
        self.kinoHd = KinoHd(self.submenu)

    def handle(self, args):
        xbmcplugin.setContent(common.addon_handle, 'movies')
        provider = None

        if args is not None:
            args = urlparse.parse_qs(args)
            provider = args.get('provider')
            category = args.get('category', None)
            option = args.get('option', [''])[0]
            page = args.get('page', [1])[0]

        if provider is None:
            common.addDir("IITV", '?submenu=' + self.submenu,
                          "provider=iitv&category=categories", isFolder=True, iconImage=common.getIcon('iitv'))
            common.addDir("NASZE KINO", '?submenu='+self.submenu,
                          "provider=naszekino&category=movies&option=1&type=main", isFolder=True, iconImage=common.getIcon('naszekino'))
            common.addDir("KINO HD", '?submenu=' + self.submenu,
                          "provider=kinohd&category=serials", isFolder=True, iconImage=common.getIcon('kinohd'))
        elif provider[0] == 'iitv':
            self.iitv.handle(category[0], option)
        elif provider[0] == 'naszekino':
            type = args.get('type')
            self.naszeKino.handle(category[0], option, type[0])
        elif provider[0] == 'kinohd':
            subcat = args.get('subcat',[''])[0]
            self.kinoHd.handle(category[0], option, page, subcat)
        xbmcplugin.endOfDirectory(common.addon_handle)


class sports:
    submenu = 'sports'
    naszeKino = None
    ekstraKlasa = None
    Estadios = None
    Livefootballol = None
    Footballorgin = None
    Goalsarena = None
    Laczynaspilka = None
    Polsatsport = None
    Lechtv = None

    def __init__(self):
        self.naszeKino = NaszeKino(self.submenu, '')
        self.ekstraKlasa = Ekstraklasa(self.submenu)
        self.Estadios = Estadios(self.submenu)
        self.Livefootballol = Livefootballol(self.submenu)
        self.Footballorgin = Footballorgin(self.submenu)
        self.Goalsarena = Goalsarena(self.submenu)
        self.Laczynaspilka = Laczynaspilka(self.submenu)
        self.Polsatsport = Polsatsport(self.submenu)
        self.Lechtv = Lechtv(self.submenu)

    def handle(self, args):
        xbmcplugin.setContent(common.addon_handle, 'movies')
        provider = None
        if args is not None:
            args = urlparse.parse_qs(args)
            provider = args.get('provider')
            category = args.get('category')
            option = args.get('option', [''])[0]
            page = args.get('page', [1])[0]
            type = args.get('type',[''])

        if provider is None:
            common.addDir("EKSTRAKLASA", '?submenu=' + self.submenu,
                          "provider=ekstraklasa&category=categories",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('ekstraklasa'))
            common.addDir("ESTADIOS", '?submenu=' + self.submenu,
                          "provider=estadios&category=categories",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('estadios'))
            common.addDir("LIVE FOOTBALL", '?submenu=' + self.submenu,
                          "provider=livefootballol&category=list",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('livefootballol'))
            common.addDir("FOOTBALL ORIGIN", '?submenu=' + self.submenu,
                          "provider=footballorgin&category=list",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('footballorgin'))
            common.addDir("GOALS ARENA", '?submenu=' + self.submenu,
                          "provider=goalsarena&category=list",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('goalsarena'))
            common.addDir("ŁĄCZY NAS PIŁKA", '?submenu=' + self.submenu,
                          "provider=laczynaspilka&category=movies",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('laczynaspilka'))
            common.addDir("POLSAT SPORT", '?submenu=' + self.submenu,
                          "provider=polsatsport&category=categories",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('polsatsport'))
            common.addDir("LECH TV", '?submenu=' + self.submenu,
                          "provider=lechtv&category=categories",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('lechtv'))
            common.addDir("NASZE KINO", '?submenu='+self.submenu,
                          "provider=naszekino&category=movies&option=3&type=main",
                          isPlayable=False, isFolder=True, iconImage=common.getIcon('naszekino'))
        elif provider[0] == 'ekstraklasa':
            self.ekstraKlasa.handle(category[0], option, page)
        elif provider[0] == 'estadios':
            self.Estadios.handle(category[0], option, page)
        elif provider[0] == 'livefootballol':
            self.Livefootballol.handle(category[0], option, page)
        elif provider[0] == 'footballorgin':
            self.Footballorgin.handle(category[0], option, page)
        elif provider[0] == 'goalsarena':
            self.Goalsarena.handle(category[0], option, page)
        elif provider[0] == 'laczynaspilka':
            self.Laczynaspilka.handle(category[0], option, page)
        elif provider[0] == 'polsatsport':
            self.Polsatsport.handle(category[0], option, page)
        elif provider[0] == 'lechtv':
            self.Lechtv.handle(category[0], option, page, type[0])
        elif provider[0] == 'naszekino':
            self.naszeKino.handle(category[0], option, type[0])

        xbmcplugin.endOfDirectory(common.addon_handle)


class liveTV:

    def handle(self, args):
        xbmcgui.Dialog().ok(common.addonname,
                            '[I]Oryginalny tekst na zacheta zakupu darmowego pluginu:[/I]',
                            'Aby uzyskać dostęp do Telewizji pobierz pełną wersję DreamTV! Po więcej informacji wejdź na stronę https://alientv.pro')
        xbmc.executebuiltin("Back")