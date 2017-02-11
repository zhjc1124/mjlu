# mjlu

模拟数字吉大的app查成绩和课表，数字吉大客户端下载:app.jlu.edu.cn

模拟机型:iPhone 5S,iOS 10.2

AES256Crypter.py实现get方法中用的AES/ECB/PKCS7Padding加密

由于需要建立一个tcp连接，在shell中建立连接后长时间无操作可能会使连接断开，
故请使用with...as...语句一步操作完成

>>> from mjlu import mjlu
>>> with mjlu("username", "password") as test:
...     test.login()                           # 使用前先使用login方法登陆
...     infos = test.get_info(show=1)          # 返回信息字典，参数show默认为0，为1时同时按格式打印结果
...     scores = test.get_score(1, show=1)     # 返回成绩字典，第一个参数term是第几个学期，第二个参数show默认为0，为1时同时按格式打印成绩(需要库tabulate来支持输出表格)
...     courses = test.get_course()            # 返回课表字典，无参数