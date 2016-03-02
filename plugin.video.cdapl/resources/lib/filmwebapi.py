# -*- coding: utf-8 -*-

# https://bitbucket.org/varabi/filmweb-api/src/2fcd07d7c4b874f4605eab9ecd530077f253ea32/src/test/java/info/talacha/filmweb/api/FilmwebApiTest.java?at=master&fileviewer=file-view-default
# https://github.com/nSolutionsPL/filmweb-api/tree/master/src/nSolutions/Filmweb/nSolutions/API/Methods
# http://pydoc.net/Python/filmwebpy/0.1.2.0/filmweb.parser.PersonParser/

import urllib
import urllib2
import hashlib
import json

# Global Settings
API_SERVER = "https://ssl.filmweb.pl/api?";
KEY = "qjcGhW2JnvGT9dfCt3uT_jozR3s";
WWW = "http://www.filmweb.pl";
VERSION = "2.2";
APPID = "android";


LIVE_SEARCH_URL = "http://www.filmweb.pl/search/live?q=";
LIVE_SEARCH_FIELD_SPACER = "\\c";	
LIVE_SEARCH_ROW_SPACER = "\\a";
IMG_POSTER_URL = "http://1.fwcdn.pl/po"


def _getUrl(url):
    """
    Get Url contnetnt
    return: string
    """
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Linux; Android 4.1.1; Galaxy Nexus Build/JRO03C) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19')
    response = urllib2.urlopen(req,timeout=5)
    link = response.read()
    response.close()
    return link
    

def _prepareSignature(method):
    signature = method + "\n" + APPID + KEY;
    signature = VERSION + "," + hashlib.md5(signature).hexdigest();
    return signature;
    
def _prepareParams(method):
    signature = _prepareSignature(method);
    method += "\n";
    qs={    'methods':method,
            'signature':signature,
            'version':VERSION,
            'appId':APPID}
    return urllib.urlencode(qs)

def _processResponse(response,_response_keys):
    _response = response.split(' t:')[0].split('\n')
    status = _response[0]
    data = _response[1]
    out={}
    if data=='null': 
        pass
    else:
        j_data=json.loads(data)
        for k,v in _response_keys.iteritems():
            out[v]=j_data[k]
    return out


def getFilmInfoFull(filmID='1'):
    method = 'getFilmInfoFull [' + filmID + ']'
    _response_keys ={
        0 :  'title',
        1 :  'originaltitle',
        2 :  'rating',
        3 :  'votes',
        4 :  'genre',
        5 :  'year',
        6 :  'duration',
        7 :  'commentsCount',
        8 :  'forumUrl',
        9 :  'hasReview', 
        10 :  'hasDescription',
        11 :  'img',
        12 :  'video',
        13 :  'premiereWorld',
        14 :  'premiered',
        15 :  'filmType',
        16 :  'seasonsCount',
        17 :  'episodesCount',
        18 :  'countriesString',
        19 :  'plotoutline'
    }
    response = _getUrl( API_SERVER + _prepareParams(method))
    out = {}
    if response[:2]=='ok':  
        out =_processResponse(response,_response_keys)
        if out.get('video'):
            out['trailer']=out.get('video')[-1]
        if out.get('img'):
            out['img']=IMG_POSTER_URL + out.get('img').replace('.2.','.3.')
    return out


def getFilmsInfoShort(filmID='594357'):
    method = 'getFilmsInfoShort [[' + filmID + ']]'
    _response_keys = {
        0 :  'title',
        1 :  'year',
        2 :  'rating',
        3 :  '_',
        4 :  'duration',
        5 :  'img',
        6 :  'id'}
    response = _getUrl( API_SERVER + _prepareParams(method))
    out = {}
    if response[:2]=='ok':
        out =_processResponse(response.replace('[[','[').replace(']]',']'),_response_keys)
    return out

#persons = getFilmPersons('594357','producers')
def getFilmPersons(filmID='594357', t='directors'):
    array_type = { 'directors': '1', 'scenarists': '2', 'musics': '3', 'photos': '4', 'actors': '6', 'producers': '9' }
    tableNames = ['id', 'role', 'role_type', 'name', 'img']
    dictPers = {}
    if t in array_type.keys():
        method = 'getFilmPersons [' + str(filmID) + ', ' + array_type[t] + ', 0, 50]'
        response = _getUrl( API_SERVER + _prepareParams(method))
        matches = re.search('(\[.*\])', response)
        infoResponse = json.loads(matches.group(1))
        for data in infoResponse:
            dictPers[data[0]] = {}
            for i in range(0, len(tableNames)):
                if tableNames[i] == 'img':
                    dictPers[data[0]][tableNames[i]] = '' if data[i] == None else 'http://1.fwcdn.pl/p' + data[i].encode('utf-8').replace('.1.jpg', '.3.jpg')
                else:
                    dictPers[data[0]][tableNames[i]] = data[i].encode('utf-8') if type(data[i]) == unicode else data[i]
    return dictPers
        

def getFilmDescription(filmID='1'):
    method = 'getFilmDescription [' + filmID + ']'
    _response_keys = {0 :  'description'}
    response = _getUrl( API_SERVER + _prepareParams(method))
    out = {}
    if response[:2]=='ok':
        out =_processResponse(response,_response_keys)
    return out

# %%%%%%%%%%%%%%%%%%%%%
# Search
# %%%%%%%%%%%%%%%%%%%%%

def _prepareResultList(result):
    elementList = result.split(LIVE_SEARCH_ROW_SPACER);
    print len(elementList)
    element=elementList[0]
    results=[]
    for element in elementList:
        one=_prepareResult(element)
        if one: results.append(one)
    return results
    

def _prepareResult(element):
    elementData = element.split(LIVE_SEARCH_FIELD_SPACER);
    type = elementData[0]
    if type == 'f' or type == 's':
        result = _FilmSearchResult(elementData);
    elif type == 'p':
        result=None
    else :
        result=None
    return result

def _FilmSearchResult(elementData):
    item={}
    if len(elementData):
        item['type'] = elementData[0]
        item['id'] = elementData[1]
        item['img'] = IMG_POSTER_URL + elementData[2]
        item['title_f'] = elementData[3]
        item['title_p'] = elementData[4]
        item['title_e'] = elementData[5]
        item['year'] = elementData[6]
        item['cast'] = elementData[7]
    return item
    
def serachItem(param=u'Strażnicy+Galaktyki'):
    result = _getUrl( LIVE_SEARCH_URL + urllib.quote_plus(param.encode('utf-8')) )
    out = _prepareResultList(result)
    return out

def searchFilmweb(title='',year='',itemType='f'):
    """
    Szuka informacji o filmie
    itemType = 'f' - Film
    itemType = 's' - Serial
    """
    search = u'%s' % title.strip()
    search += u' %s' % year if year else ''
    out= serachItem(search)
    if out:
        if len(out)==1:    #Found exactly one item
            found = out[0]
        else:
            for one in sorted(out, key=lambda k: k['year'],reverse=True) :
                if one.get('type') == itemType:
                    found = one
                    break
        return getFilmInfoFull(found.get('id',''))
    else:
        return {}

if __name__=="__main__":
    pass
    # out = getFilmInfoFull(filmID='594357')
    # out = getFilmDescription('594357')
    
    # title='Grawitacja (2013)'
    # title='Terminator 2 1991'
    # title='Potop '
    # filminfo = searchFilmweb(title,year='2014',itemType='f')
    # filminfo.get('img')
    # filminfo.get('trailer')
