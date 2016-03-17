# -*- coding: utf-8 -*-

import re,os
from datetime import datetime
import json as json
import urllib2,urllib
import filmwebapi as fa
import cdapl as cda

# Functions
      
#jdata=readJsonFile(jfilename)

def readJsonFile(jfilename):
    jdata=cda.ReadJsonFile(jfilename)
    jdata=rename_key(jdata,old_key='_filmweb',new_key='filmweb')
    for one in jdata:
        filmweb=one.get('filmweb','')
        if not filmweb: 
            img=one.get('img',' ') 
            if img and img.startswith('http://1.fwcdn.pl/'):
                one['filmweb']=img.split('/')[-2]
    return jdata

def writeJsonFile(jdata,jfilename):
    jdata=rename_key(jdata,old_key='filmweb',new_key='_filmweb')
    with open(jfilename, 'w') as outfile:
       json.dump(jdata, outfile, indent=2, sort_keys=True)

 
#jdata=readJsonFiles(files) 
def readJsonFiles(files):
    jdata=[]
    jfilename=files[1]
    for jfilename in files:
        jdata_one=readJsonFile(jfilename)
        jdata.extend(jdata_one)
    return jdata

# url='http://www.cda.pl/video/show/cale_filmy_or_caly_film_fps_lektor_pl_dubbing/p1?duration=dlugie&section=&quality=720p&section=&s=date&section=' # film polski
# a=GET_newMovies(url,t_patter='')
def GET_newMovies(url,t_patter=''):
    items=[]
    if not url.startswith('http://www.cda.pl/'):
        return items
    if '/video/show/' in url:
        items,next=cda.searchCDA(url)    # get items
    elif '/folder/' in url:
        items,folders = cda.get_UserFolder_content(url)

    for one in items:
        title = one.get('title')
        print '#'*5
        one['dirtytitle']=title
        if t_patter:
            title = re.sub(t_patter,'',title)
        title, year, label = cda.cleanTitle(title)
        one['title']=title.strip()
        if year:
            one['title'] += ' (%s)' % year
        one['label']=label
        one['year']=year
        one=filmweb_updateItemInfo(one)
    return items

def filmweb_updateItemInfo(one):
    found=False
    title=one.get('title')
    filmweb=one.get('filmweb','')
    if filmweb:
        print 'Szukam:%s'%(str(filmweb))
        found = fa.getFilmInfoFull(str(filmweb))
    elif title:
        print 'Szukam:%s'%(title)
        dane=[ x.split(')')[0].strip() for x in title.split('(')]
        tytul=dane[0]
        rok='' if len(dane)==1 else dane[1];
        found = fa.searchFilmweb(tytul,rok)

    if found:
        one['img'] = found.get('img','')
        one['plot'] = found.get('plot',one.get('plot','')) 
        one['trailer'] =  found.get('trailer','')
        one['year'] =u'%s'%found.get('year','')
        one['rating'] =found.get('rating','')
        one['duration'] = found.get('duration','')
        one['genre']=found.get('genre','')
        one['filmweb']=found.get('filmweb','')
        one['title']=u'%s (%d)' %(found.get('title'),found.get('year',''))
        one['studio']=found.get('studio','')
        return one
    else:
        print '\tBrak rezultatu dla :%s'%(title)
    return one

def jdata_pick_better(new,old):
    if 'dubbing' in new.get('label','') and 'dubbing' not in old.get('label',''):
        print '\tNew dubbing', new.get('title')
        return new
    if 'lektor' in new.get('label','') and 'napis' in old.get('label',''):
        print '\tNew lektor', new.get('title')
        return new
    if len(new.get('code','')) > len(old.get('code','')):
        print '\tNew',new.get('code'), new.get('title')
        return new
    else:
        return old
    
def jdata_filter_in(jdata,key='studio',value='Polska'):
    filter_list=[]
    to_remove=[]
    for i,one in enumerate(jdata):
        if value in one.get(key,''):
            filter_list.append(one)
            to_remove.append(i)
    print 'Filterd %d items' % len(filter_list)
    for i in reversed(to_remove): # start at the end to avoid recomputing offsets
        del jdata[i]
    return filter_list
    
def jdata_remove_duplicates(items,by1='filmweb',by2='code'):
    newlist=[]
    duplicates=[]
    mylist = sorted(items, key=lambda k: ( k.get(by1,''), k.get(by1,'') ))
    
    for one in mylist:
        if one.get(by1):
            if one.get(by1) not in [x.get('filmweb','') for x in newlist]:
                newlist.append(one)
                #print one.get('filmweb',''),one.get('code',''),one.get('title','')
            else:
                duplicates.append(one)
    return newlist,duplicates

def jdata_separate_duplicates(existing_items):
    filmweb_db = [i.get('filmweb') for i in existing_items if i.get('filmweb')]
    duplicates =  (len(filmweb_db)-len(set(filmweb_db)))
    duplicated_items=[]
    if duplicates:
        indices = [(x,i) for i, x in enumerate(filmweb_db) if filmweb_db.count(x)>1]
        indices.sort(key=lambda tup: tup[0])    # sort by filmweb_id
        to_remove=[]
        for i in range(len(indices)-1):
            one_f,one_idx=indices[i] 
            two_f,two_idx=indices[i+1]
            if one_f == two_f:  # matching filmwelbs
                one = existing_items[one_idx]
                two = existing_items[two_idx]
                if one.get('part','')!=two.get('part',''):
                    continue    # different file
                better = jdata_pick_better(one,two)
                if two==better:
                    to_remove.append(one_idx)
                else:
                    to_remove.append(two_idx)
            
        # to remove
        #for i in to_remove: one = existing_items[i];print one.get('title'),one.get('label');
        # doubbled intems
        #for one_f,i in indices: one = existing_items[i];print one.get('title'),one.get('label')
        print 'Found  %d dupliates' %len(to_remove)
        for i in reversed(to_remove):
            duplicated_items.append(existing_items[i])
            del existing_items[i]
            
    return duplicated_items

def jdata_validate_cda_links(jdata):
    #one=jdata[0]
    count = 0
    N=len(jdata)
    inactive_items=[]
    for i,one in enumerate(jdata):
        title=one.get('title')
        url=one.get('url')
        msg=one.get('msg')

        if url.startswith('http://www.cda.pl/video/'):
            response=getUrlResponse(url)
            if response != 'OK':
                count += 1
                one['msg'] = u' [COLOR red]Materiał został usunięty! %s[/COLOR] ' % response
                inactive_items.append(i)
            else:
                one['msg'] = u''
        else:
            print '\tNOT CDA [%s] %s'%(title,url)
           
        print '%03d/%03d : %s\t%s ' %(i,N,response, title)
    print '\nSummary: %d linki wydaja sie nieaktywne' % count
    return jdata,inactive_items

        
## Functions     
def getUrlResponse(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36')
    response = 'NotChecked'
    try: 
        resp = urllib2.urlopen(req)
        response='OK'
    except urllib2.HTTPError, e:
        response = 'HTTPError = ' + str(e.code)
    except urllib2.URLError, e:
        response =  'URLError = ' + str(e.reason)
    except httplib.HTTPException, e:
        response = 'HTTPException'
    return response
    
def rename_key(existing_items,old_key,new_key):
    for one in existing_items:
        if one.has_key(old_key):
             one[new_key] = one.pop(old_key)
    return existing_items
    
def get_file_info(jfilename):
    count = '(%d)' % len(cda.ReadJsonFile(jfilename))
    dt = os.path.getmtime(jfilename)
    update = datetime.fromtimestamp(os.path.getmtime(jfilename)).strftime('%Y-%m-%d') # %H:%M:%S')
    return count,update
        
        
  