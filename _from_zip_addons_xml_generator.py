# -*- coding: utf-8 -*-
""" addons.xml generator """

import re
import os
import zipfile
import StringIO
import datetime
from hashlib import md5

class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """
    def __init__( self ):
        # generate files
        self.myaddons=[]
        self._generate_addons_file("zips")
        self._generate_md5_file()
        if self.myaddons:
            self._generate_readme()
        # notify user
        print "Finished updating addons xml and md5 files"

    def _generate_addons_file( self,path="zips" ):
        # addon list
        addons = os.listdir( path )
        # final addons text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
        # loop thru and add each addons addon.xml file
        #addon = addons[2]
        for addon in addons:
            try:
                # skip any file or .git folder or .svn folder
                if ( addon.startswith('_') or not os.path.isdir( os.path.join(path,addon) ) or addon == ".git" or addon == ".svn" ): continue

                # get zip files
                _zip = os.listdir( os.path.join(path,addon) )

                _zip = [ i for i in _zip if i.startswith( addon ) and i.endswith( ".zip" ) ]
                # get sort files
                _zip = [ (int(''.join(re.compile('\d+').findall(i))), i) for i in _zip ]
                _zip.sort()
                _zip = [ i[1] for i in _zip ]
                # select zip file
                _zip = os.path.join( path, addon, _zip[-1] )
                # get creating time of 'addon.xml'
                _zip_timestamp = os.path.getctime(_zip)
                _zip_timestamp_date = datetime.datetime.fromtimestamp(_zip_timestamp).strftime('%Y-%m-%d')
                # read zip file
                zip = zipfile.ZipFile( open( _zip, 'rb' ) )
                # get xml file
                xml_file = zip.namelist()
                xml_file = [i for i in xml_file if i.endswith( "addon.xml" )][0]
                # read xml file
                xml_file = zip.read( xml_file )
                # close zip file
                zip.close()
                # split lines for stripping
                xml_lines = xml_file.splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find( "<?xml" ) >= 0 ): continue
                    # add line
                    addon_xml += unicode( line.rstrip() + "\n", "UTF-8" )
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
                version = re.search('version="(.*?)"',addon_xml).group(1)
                name = re.search('name="(.*?)"',addon_xml).group(1)
                print 'ADDON: %s version: %s name:%s'%(addon,version,name)
                self.myaddons.append({'name':name,'version':version,'addon':addon,'date':_zip_timestamp_date,'timetamp':_zip_timestamp})
            except Exception, e:
                # missing or poorly formatted addon.xml
                print "Excluding %s for %s" % ( _path, e, )
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        # save file
        self._save_file( addons_xml.encode( "UTF-8" ), file="addons.xml" )

    def _generate_md5_file( self ):
        try:
            # create a new md5 hash
            m = md5( open( "addons.xml" ).read() ).hexdigest()
            # save file
            self._save_file( m, file="addons.xml.md5" )
        except Exception, e:
            # oops
            print "An error occurred creating addons.xml.md5 file!\n%s" % ( e, )

    def _save_file( self, data, file ):
        try:
            # write data to the file
            open( file, "w" ).write( data )
        except Exception, e:
            # oops
            print "An error occurred saving %s file!\n%s" % ( file, e, )
    
    def _generate_readme(self,file="README.md"):
        try:
            txt = u"# Ramic Kodi Addons Repository\n"
            txt +=u"Repozytorium wtyczke dla programu KODI\n"
            txt +=u"[repository.ramic.zip](https://github.com/ramicspa/kodi/raw/master/repository.ramic.zip)\n"

            listaddons=sorted( self.myaddons, key=lambda k: k['timetamp'], reverse=True) 
            header = u'## Zawartość repozytoium\n|Wtyczka|Nazwa|Wersja|Aktualizacja|\n|---|---|---|---|\n'
            src='<img src="https://offshoregit.com/ramicspa/kodi/zips/%s/icon.png" width="48">'
            line = ['|%s|%s|%s|%s'%(src%x.get('addon',''),x.get('name',''),x.get('version',''),x.get('date','')) for x in listaddons]
            txt +=header+'\n'.join(line)
            self._save_file( txt.encode('utf-8'), file=file )
        except Exception, e:
            # oops
            print "An error occurred creating Readme.md file!\n%s" % ( e, )

if ( __name__ == "__main__" ):
    # start
    g=Generator()
   

    
    