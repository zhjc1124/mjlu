import urllib
import urllib.request
import http.cookiejar
import hashlib
import re
import json
import socket


class mjlu(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        # TCP协议
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 目标ip为202.98.18.57，端口为18080
        self.src = ('202.98.18.57', 18080)
        self.s.connect(self.src)
        # headers
        self.headers = 'Host: 202.98.18.57:18080\r\n' \
                       'User-Agent: 数字吉大 2.41 (iPhone; iOS 10.2; zh_CN)\r\n' \
                       'Connection: keep-alive\r\n' \
                       'Accept-Encoding: gzip\r\n' \
                       '\r\n'
        # 登陆cookies用的sessionid
        self.sessionid = self.get_token()


    # 上下文管理器有关
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.close()

    # sar发送接收数据然后返回结果
    def sar(self, data):
        data += self.headers
        self.s.send(data.encode())
        result = []
        while True:
            rec = self.s.recv(1024)
            if rec:
                result.append(rec)
            else:
                break
        return b''.join(result).decode()

    # 获取token
    def get_token(self):
        result = self.sar('GET /webservice/m/api/token/v2 HTTP/1.1\r\n')
        # 返回数据中只有部分是json格式
        j_result = json.loads(result[-233:-6])
        sessionid = j_result['resultValue']['sessionid']
        return sessionid

if  __name__ == '__main__':
    with mjlu(' ', 'password0183') as test:
        print(test.sessionid)
