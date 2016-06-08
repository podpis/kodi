import urlparse,cookielib,urllib2,urllib
import time,re,os

url='http://www.efilmy.tv//filmy.php?cmd=show_player&id=88657'
cj= cookielib.LWPCookieJar()
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

def createCookie(url,cj=None,agent=UA):
    urlData=''
    try:
        class NoRedirection(urllib2.HTTPErrorProcessor):    
            def http_response(self, request, response):
                return response

        def parseJSString(s):
            try:
                offset=1 if s[0]=='+' else 0
                val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
                return val
            except:
                pass

        #agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'
        if cj==None:
            cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', agent)]
        response = opener.open(url)
        result=urlData = response.read()
        response.close()
#        print result
#        print response.headers
        jschl = re.compile('name="jschl_vc" value="(.+?)"/>').findall(result)[0]

        init = re.compile('setTimeout\(function\(\){\s*.*?.*:(.*?)};').findall(result)[0]
        builder = re.compile(r"challenge-form\'\);\s*(.*)a.v").findall(result)[0]
        decryptVal = parseJSString(init)
        lines = builder.split(';')

        for line in lines:
            if len(line)>0 and '=' in line:
                sections=line.split('=')

                line_val = parseJSString(sections[1])
                decryptVal = int(eval(str(decryptVal)+sections[0][-1]+str(line_val)))

#        print urlparse.urlparse(url).netloc
        answer = decryptVal + len(urlparse.urlparse(url).netloc)

        u='/'.join(url.split('/')[:-1])
        query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (u, jschl, answer)

        if 'type="hidden" name="pass"' in result:
            passval=re.compile('name="pass" value="(.*?)"').findall(result)[0]
            query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (u,urllib.quote_plus(passval), jschl, answer)
            time.sleep(5)
        
        response = opener.open(query)
        response.close()
            
 #       print query
#        import urllib2
        opener = urllib2.build_opener(NoRedirection,urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', agent)]
        response = opener.open(url)
        response.close()
        #print opener.headers

 #       print response.headers
        #cookie = str(response.headers.get('Set-Cookie'))
        #response = opener.open(url)
        #print cj
#        print response.read()

        return cj
    except:
        return None

def cookieString(COOKIEFILE):
    sc=''
    if os.path.isfile(COOKIEFILE):
        cj = cookielib.LWPCookieJar()
        cj.load(COOKIEFILE)
        for c in cj:
            sc+='%s=%s;'%(c.name, c.value)
    return sc

    
