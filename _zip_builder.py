# -*- coding: utf-8 -*-
""" addon pakager """

import os
import re
import shutil
import zipfile

def _generate_zip_package( path="." ):
    output_folder = "zips"
    # addon list each folder that has addon.xml inside
    addons = [os.path.join(path,o) for o in os.listdir(path) if os.path.isdir(os.path.join(path,o)) and os.path.exists(os.path.join(path,o,'addon.xml'))]
    # loop thru each folder that has addon structure
    for addon in addons:
        try:
            # get version
            version = re.compile('<addon.+?version=[\"\']([^\"\']+)[\"\']',re.DOTALL).findall(open(os.path.join(addon,'addon.xml'),'r').read())[0]
            print '\n### ADDON: %s %s ###'%(os.path.split(addon)[-1],version)
            # clean addon
            _clean_modules(addon)
            # check destination folder:
            destination_folder = os.path.join(output_folder,os.path.split(addon)[-1])
            if not os.path.isdir(destination_folder):
                print 'New addon : %s' %os.path.split(addon)[-1]
                yn = raw_input("Add new addon to zips ?: (y/n)")
                if yn=='y' or yn=='Y':
                    print 'Creating folder'
                    os.makedirs(destination_folder)
            # check destination zip:
            destination_zip = os.path.join(destination_folder,'%s-%s'%(os.path.split(addon)[-1],version))
            if os.path.exists(destination_zip+'.zip'):   
                print 'Addon with this version already exists in the folder'
                yn = raw_input("Continue (overwrite file) ? (y/n)")
                if yn=='n' or yn=='N':
                    continue
               
            # create zipfile
            print 'Creating zip file: %s'%destination_zip
            shutil.make_archive(destination_zip, 'zip', root_dir=path,base_dir=addon)
            
            # copy changelog.txt
            print 'copy changelog.txt: %s'%destination_zip
            shutil.copy(os.path.join(addon,'changelog.txt'), os.path.join(destination_folder,'changelog-%s.txt'%version)) 
            imgs = [os.path.join(addon,o) for o in os.listdir(addon) if o.startswith('icon') or o.startswith('fanart')]
            for img in imgs:
                print 'copy img %s'%img
                shutil.copy(img, destination_folder)
        except Exception, e:
            # missing or poorly formatted addon.xml
            print "Excluding %s" % (  str(e), )
            
def _clean_modules(dir):
    """
    remove unwanted files
    """
    def gen_files(dir, pattern):
        for dirname, subdirs, files in os.walk(dir):
            for f in files:
                if f.endswith(pattern):
                    yield os.path.join(dirname, f)

    for f in gen_files(dir, '.pyc'):
        #print f
        os.remove(f)
    for f in gen_files(dir, '.pyo'):
        #print f
        os.remove(f)

_generate_zip_package( path="." )