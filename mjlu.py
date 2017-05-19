from AES256Crypter import AES256Crypter
import requests
import json
import re

class mjlu(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.sessionid, self.name = self.__get_token()
        self.__login()


    # 获取token
    def __get_token(self):
        token_url = 'http://202.98.18.57:18080/webservice/m/api/token/v2'
        result = self.session.get(token_url).content.decode()
        result = json.loads(result)
        sessionid = result['resultValue']['sessionid']
        name = result['resultValue']['name']
        return sessionid, name

    def __login(self):
        # 获取登陆cookies用的sessionid，和加密用的name
        # AES/ECB/PKCS7Padding加密
        key = bytes.fromhex(self.name)
        crypter = AES256Crypter(key)

        params = {
            'apptype': '',
            'username': crypter.encrypt(self.username),
            'password': crypter.encrypt(self.password),
            'user_ip': '192.168.0.119',
            'login_type': 'ios',
            'from_szhxy': '1',
            'token': ''
        }
        login_url = 'http://202.98.18.57:18080/webservice/m/api/login/v2?'

        result = self.session.get(login_url,params=params).content.decode()
        result = json.loads(result)
        feedback = result['resultStatus']['message']

        if feedback == "the account " + self.username + " does not exist.":
            raise UserError("此邮箱账号" + self.username + "不存在")
        elif feedback == "用户名或密码错误。":
            raise UserError(feedback)

    def get_info(self, show=False):
        info_url = 'http://202.98.18.57:18080/webservice/m/api/proxy'
        postdata = 'link=http%3A%2F%2Fip.jlu.edu.cn%2Fpay%2Finterface_mobile.php%3Fmenu%3Dget_mail_info%26mail%3D' \
                        + self.username
        postdata = postdata.encode()
        headers = {
                'Cookie': 'JSESSIONID=' + self.sessionid,
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'User-Agent': 'mjida/2.41 CFNetwork/808.2.16 Darwin/16.3.0',
                'Content-Type': 'application/x-www-form-urlencoded'
        }

        result = self.session.post(info_url, postdata, headers=headers).content.decode()
        result = json.loads(result)
        stu_info = result['resultValue']['content']
        # 避免错误的json格式
        pattern = re.compile(r'"[^,:]*?"[^,:]*?"[^,:]*?"')
        _ = pattern.findall(stu_info)
        if _:
            _ = list(_[0])
            for index, i in enumerate(_[1:-1]):
                if i == '"':
                    _[index + 1] = '\\"'
            _ = ''.join(_)
            stu_info = pattern.sub(_, stu_info)
        stu_info = json.loads(stu_info)
        if show:
            # 简单的排除一些错误
            ip = stu_info.get('ip', [''])
            if not ip:
                ip = ''
            if type(ip) == list:
                ip = ip[0]
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
        score_url = 'http://202.98.18.57:18080/webservice/m/api/getScoreInfo?' \
                    'email=' + self.username + \
                    '&termId=' + termid
        result = self.session.get(score_url).content.decode()
        result = json.loads(result)
        scores = result["resultValue"]

        # 打印相关
        if show:
            if scores:
                def form(key, header):
                    _ = [score[key] for score in scores]
                    _.insert(0, header)
                    return _
                scoreNames = form("scoreName", "学科")
                length = [max(map(len, scoreNames))+3, 6, 4, 7, 7, 7]
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
        course_url = 'http://202.98.18.57:18080//webservice/m/api/getCourseInfo?' \
                     'email=' + self.username
        result = self.session.get(course_url, headers={'Cookie': 'JSESSIONID=' + self.sessionid}).content.decode()
        result = json.loads(result)

        courses = result["resultValue"]
        return courses



class UserError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


if __name__ == '__main__':
    # test = mjlu('zhangjc2015','')
    # test.get_info(show=True)
    sample_user = input("请输入用户名：")
    sample_pwd = input("请输入密码：")
    test = mjlu(sample_user, sample_pwd)
    infos = test.get_info(show=False)
    scores = test.get_score(3, show=True)
    courses = test.get_course()

