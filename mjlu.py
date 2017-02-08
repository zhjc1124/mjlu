import re
import json
import socket
from AES256Crypter import AES256Crypter


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
                       'Connection: keep-alive\r\n' \
                       'Accept-Encoding: gzip\r\n' \
                       'User-Agent: 数字吉大 2.41 (iPhone; iOS 10.2; zh_CN)\r\n'

        # 获取登陆cookies用的sessionid，和加密用的name
        self.sessionid, self.name = self.get_token()

        # AES/ECB/PKCS7Padding
        self.key = bytes.fromhex(self.name)
        self.crypter = AES256Crypter(self.key)

        # 登陆
        self.login()

    # 上下文管理器有关
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.close()

    # sar发送接收数据然后返回结果
    def communicate(self, data):
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
        data = 'GET /webservice/m/api/token/v2 HTTP/1.1\r\n' + self.headers + '\r\n'
        result = self.communicate(data)
        # re匹配json数据
        pattern = re.compile(r'e2\r\n({.*})\r\n0', re.DOTALL)
        match = pattern.search(result)
        json_data = match.group(1)

        j_result = json.loads(json_data)
        sessionid = j_result['resultValue']['sessionid']
        name = j_result['resultValue']['name']
        return sessionid, name

    def login(self):
        # 在headers中重复Connection反爬虫?
        data = 'GET /webservice/m/api/login/v2?apptype=' + \
               '&username=' + self.crypter.encrypt(self.username) + \
               '&password=' + self.crypter.encrypt(self.password) + \
               '&user_ip=192.168.0.119&login_type=ios&from_szhxy=1&token= HTTP/1.1\r\n' + \
               self.headers + \
               'Connection: keep-alive\r\nCookie: JSESSIONID=' + self.sessionid + '\r\n\r\n'
        self.communicate(data)
        data = 'POST /webservice/m/api/proxy HTTP/1.1\r\n' \
               'Host: 202.98.18.57:18080\r\n' \
               'Connection: keep-alive\r\n' \
               'Accept-Encoding: gzip, deflate\r\n' \
               'Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n' \
               'Cookie: JSESSIONID=' + self.sessionid + '\r\n' + \
               'Content-Length: 104\r\n' \
               'Accept-Language: zh-cn\r\n' \
               'Accept: */*\r\nConnection: keep-alive\r\n' \
               'User-Agent: mjida/2.41 CFNetwork/808.2.16 Darwin/16.3.0\r\n\r\n' \
               'link=http%3A%2F%2Fip.jlu.edu.cn%2Fpay%2Finterface_mobile.php%3Fmenu%3Dget_mail_info%26mail%3D' + self.username
        result = self.communicate(data)
        print(result)

if __name__ == '__main__':
    with mjlu('zhangjc2015', 'zhang1124171X') as test:
        pass
