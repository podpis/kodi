# -*- coding: utf-8 -*-

import os
import re
import json


def get_strings_py(): 
    language_path = os.path.join(os.getcwd(),'..','language')
    language_dir = os.listdir(language_path)
    
    string_dicts=[]
    
    for l_dir in language_dir:
        with open(os.path.join(language_path,l_dir,'strings.po'),'r') as f:
            data = f.read()
        ss = re.compile('msgctxt "#(\d{5})"[ \t\n]*msgid "(.*?)"').findall(data)
        string_dicts.append(dict([(x[1],int(x[0])) for x in ss]))
    
    ok=False
    if len(string_dicts)>1:
        for sd in string_dicts:
            ok = True if string_dicts[0] == sd else False
    if ok:
        txt ='# -*- coding: utf-8 -*-\n\n'
        txt+='STRINGS='+json.dumps(string_dicts[0],indent=2)
        with open('strings.py','w') as f:
            f.write(txt)
            
            
        
        

            
                