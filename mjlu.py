import urllib
import urllib.request
import http.cookiejar
import hashlib
import json


headers = {
    'Host': '202.98.18.57:18080',
    'Accept-Encoding': 'gzip',
    'User-Agent': '数字吉大 2.41 (iPhone; iOS 10.1.1; zh_CN)'.encode().decode('latin-1'),
    'Connection': 'keep-alive',
}
get_url = 'http://202.98.18.57:18080/webservice/m/api/token/v2'
# cookie = http.cookiejar.MozillaCookieJar()
# opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
# request = urllib.request.Request(get_url,headers = headers)
# result = opener.open(request)
# # result = urllib.request.urlopen(request)
# print(list(cookie)[0].value)

# base_url = 'http://202.98.18.57:18080/webservice/m/api/login/v2?apptype='
# get_url = base_url+ '&username=' + username + '&password='+ password + \
#           '&user_ip=192.168.0.101&login_type=ios&from_szhxy=1&token= '
request = urllib.request.Request(get_url,headers = headers)
result = urllib.request.urlopen(request)
print(result.read().decode())
# print(result)
