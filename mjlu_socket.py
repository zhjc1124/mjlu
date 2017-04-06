import re
import json
import socket
import time
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
        self.s.setblocking(0)  # 非阻塞模式

        # headers
        self.headers = 'Host: 202.98.18.57:18080\r\n'
        self.sessionid, self.name = self.__get_token()
        # self.__login()

    # 发送data并接受处理数据
    def __communicate(self, data):
        self.s.send(data.encode())
        time.sleep(1)
        result = []
        while True:
            try:
                buf = self.s.recv(1024)
            except BlockingIOError:
                break
            time.sleep(0.1)
            result.append(buf)
        result = b''.join(result).decode()
        # 匹配字符串中json格式处理后返回
        pattern = re.compile(r'\r\n\S{2,4}\r\n({.*?})\r\n0', re.DOTALL)
        match = pattern.findall(result)
        j_result = [json.loads(json_data) for json_data in match]
        return j_result[0]

    # 获取token
    def __get_token(self):
        data = 'GET /webservice/m/api/token/v2 HTTP/1.1\r\n' + self.headers + '\r\n'
        result = self.__communicate(data)
        sessionid = result['resultValue']['sessionid']
        name = result['resultValue']['name']
        return sessionid, name

    def __login(self):
        # 获取登陆cookies用的sessionid，和加密用的name
        self.sessionid, name = self.__get_token()
        # AES/ECB/PKCS7Padding加密
        key = bytes.fromhex(name)
        crypter = AES256Crypter(key)

        data = 'GET /webservice/m/api/login/v2?apptype=' + \
               '&username=' + crypter.encrypt(self.username) + \
               '&password=' + crypter.encrypt(self.password) + \
               '&user_ip=192.168.0.119&login_type=ios&from_szhxy=1&token= HTTP/1.1\r\n' + \
               self.headers + \
               'Cookie: JSESSIONID=' + self.sessionid + '\r\n\r\n'
        result = self.__communicate(data)
        feedback = result['resultStatus']['message']

        if feedback == "the account " + self.username + " does not exist.":
            raise UserError("此邮箱账号" + self.username + "不存在")
        elif feedback == "用户名或密码错误。":
            raise UserError(feedback)

    def get_info(self, show=False):
        data = 'POST /webservice/m/api/proxy HTTP/1.1\r\n' \
               'Host: 202.98.18.57:18080\r\n' \
               'Accept-Encoding: gzip, deflate\r\n' \
               'Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n' \
               'Cookie: JSESSIONID=' + self.sessionid + '\r\n' + \
               'Content-Length: ' + str(93+len(self.username)) + '\r\n' \
               'Accept: */*\r\nUser-Agent: mjida/2.41 CFNetwork/808.2.16 Darwin/16.3.0\r\n\r\n' \
               'link=http%3A%2F%2Fip.jlu.edu.cn%2Fpay%2Finterface_mobile.php%3Fmenu%3Dget_mail_info%26mail%3D' \
               + self.username
        result = self.__communicate(data)
        stu_info = result['resultValue']['content']
        stu_info = json.loads(stu_info)
        if show:
            print('邮箱账号:', stu_info['mail'])
            print('姓名:', stu_info['name'])
            print('身份证号:', stu_info['zhengjianhaoma'])
            print('学院:', stu_info['class'])
            ip = stu_info['ip'][0]
            print('ip地址:', ip)
            ip_info = stu_info['ip_info'][ip]
            print('校园卡号:', ip_info['id_name'])
            print('校区:', ip_info['campus'])
            print('所在区域:', ip_info['net_area'])
            print('宿舍号:', ip_info['home_addr'])
            print('电话号:', ip_info['phone'])
            print('mac地址:', ip_info['mac'])
        return stu_info

    def get_score(self, term, show=False):
        # 计算公式2*(入学年份-1951)+学期数
        # 131对应2016-2017第一个学期，以2015级学生为例，131 = 2*(2015-1951)+3
        termid = str(2*(int('20'+self.username[-2:])-1951)+term)
        data = 'GET /webservice/m/api/getScoreInfo?' \
               'email=' + self.username + \
               '&termId=' + termid + \
               ' HTTP/1.1\r\n' + self.headers + \
               'Cookie: JSESSIONID=' + self.sessionid + '\r\n\r\n'
        result = self.__communicate(data)
        scores = result["resultValue"]

        # 打印相关
        if show:
            if scores:
                def form(key, header):
                    _ = [score[key] for score in scores]
                    _.insert(0, header)
                    return _
                scoreNames = form("scoreName", "学科")
                length = [max(map(len, scoreNames)) + 3, 6, 4, 7, 7, 7]
                values = [[score["scoreName"], score["scoreProperty"],
                           score["score"], score["scorePoint"],
                           score["scoreFalg"], score["scoreCredit"]
                           ] for score in scores
                          ]
                values.insert(0, ["学科", "类型", "分数", "绩点", "重修", "学分"])

                # 半角转全角函数，有利于对齐
                def strB2Q(ustring):
                    rstring = ""
                    for uchar in ustring:
                        inside_code = ord(uchar)
                        if inside_code == 32:  # 半角空格直接转化
                            inside_code = 12288
                        elif 32 <= inside_code <= 126:  # 半角字符（除空格）根据关系转化
                            inside_code += 65248
                        rstring += chr(inside_code)
                    return rstring
                for value in values:
                    for i in range(6):
                        print(strB2Q(value[i].center(length[i], u'　')),
                              end='')
                    print('')
            else:
                print('无此学期成绩')
        return scores

    def get_course(self):
        data = 'GET /webservice/m/api/getCourseInfo?' \
               'email=' + self.username + \
               ' HTTP/1.1\r\n' + self.headers + \
               'Cookie: JSESSIONID=' + self.sessionid + '\r\n\r\n'
        result = self.__communicate(data)
        courses = result["resultValue"]
        return courses

    # 上下文管理器相关
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.close()

    def close(self):
        self.s.close()


class UserError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


if __name__ == '__main__':
    sample_user = input("请输入用户名：")
    sample_pwd = input("请输入密码：")
    with mjlu(sample_user, sample_pwd) as test:
        infos = test.get_info(show=True)
        scores = test.get_score(3, show=True)
        courses = test.get_course()
