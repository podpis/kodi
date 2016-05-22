# -*- coding: utf-8 -*-

import urllib2,urllib
import re
import time
import base64


UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

def fixForEPG(one):
    return one
    
def getUrl(url,data=None,header={}):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=5)
        link = response.read()
        response.close()
    except:
        link=''
    return link
    
    
url='http://pierwsza.tv/player/watch/53'
content = getUrl(url)

idx=content.find('window.connectToLive')

idx1=content.find('window.endpoints')
idx2=content[idx1:].find('}";')

ep= content[idx1+20:idx1+idx2+1]
print ep
ep=ep.replace('\\','')
data = json.loads(ep)
base64.b64decode(data['ct'])
##
http://pierwsza.tv/player/watch/122
 'http://91.240.87.72:8035' , 'f49e780a80fd7f788ba014713cf62c17b812a0849a8489b60c5c6a09608bf5b9' );
 
 
 
token:f9b6e8441a240e3f37ae4714382cdea33e8101ad96706fc9540e9f2b4bd5809412266a7d1f88a12741ee
server:8
source:122
cs:7f027b80d12aeed0344d24e15b27940e67d7e7d5263bea912b152889cb6c4c02


answer:
    ÿ0{"sid":"9ULr32XCmTykXY9tABPI","upgrades":["websocket"],"pingInterval":25000,"pingTimeout":60000}

#get token
http://109.236.84.47:8004/socket.io/?EIO=3&transport=polling&t=LIptjfh&sid=9ULr32XCmTykXY9tABPI
0:"authStatus"
1:status:"ok"
    stoken:"94ee3f2f47f3b9ff1d8f54894dc1eb4b1782fcffedaade5864a3e854243539cb0f0ace26a8bc9a3553ba"


#requrest
http://pierwsza.tv/player/request-stream?token=f9b6e8441a240e3f37ae4714382cdea33e8101ad96706fc9540e9f2b4bd5809412266a7d1f88a12741ee&server=8&source=122&cs=7f027b80d12aeed0344d24e15b27940e67d7e7d5263bea912b152889cb6c4c02
#answer:
    id:"10b98f0b003674cc75bbf4ac8d2e6dbc07ea2375734b4e41adb9efdcbd5469147e"
    message:"Dla tworcow pluginow i osob chetnych na integracje z serwisem zapraszamy do formularza kontaktowego celem przedyskutowania dedykowanego API."
    status:"ok"

# stream final
http://109.236.84.47:8001/20cfda19bae90eca42ca7f88ea6528f52d99174fbeb4bbc3a0ef55b2e8e21b3c/stream.m3u8?token=94ee3f2f47f3b9ff1d8f54894dc1eb4b1782fcffedaade5864a3e854243539cb0f0ace26a8bc9a3553ba