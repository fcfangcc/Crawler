# -*- coding: utf8 -*-
import requests
import re
import platform, os
import cookielib
import json
import urllib
import time
requests.packages.urllib3.disable_warnings()
# todo:修改windows命令行下登录失败的问题,还未定位到问题原因
def get_tt():
    return str(int(time.time()*1000))

requests = requests.session()
requests.cookies = cookielib.LWPCookieJar('cookies.txt')

try:
    requests.cookies.load(ignore_discard=True)
    # print requests.cookies
except:
    print u"还未登录百度"

HEADER = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"
         }

MAIN_URL = "http://tieba.baidu.com/"

BAIDU_CAT_URL_MAIN = "http://passport.baidu.com/cgi-bin/genimage?"

class NetworkError(Exception):
    pass

class Login2(object):
    def __init__(self, USERNAME=None, PASSWORD=None):
        self.username = USERNAME
        self.password = PASSWORD
        self.URL_BAIDU_SIGN = 'http://tieba.baidu.com/sign/add'

    def login(self):
        URL_BAIDU_TOKEN = 'https://passport.baidu.com/v2/api/?getapi&tpl=pp&apiver=v3&class=login'
        URL_BAIDU_LOGIN = 'https://passport.baidu.com/v2/api/?login'

        tokenReturn = requests.get(URL_BAIDU_TOKEN, verify=False).content
        matchVal = re.search(u'"token" : "(?P<tokenVal>.*?)"', tokenReturn)
        self.tokenVal = matchVal.group('tokenVal')


        postData = {
            'username': self.username,
            'password': self.password,
            'u': 'https://passport.baidu.com/',
            'tpl': 'pp',
            'token': self.tokenVal,
            'staticpage': 'https://passport.baidu.com/static/passpc-account/html/v3Jump.html',
            'isPhone': 'false',
            'charset': 'UTF-8',
            'callback': 'parent.bd__pcbs__ra48vi'
            }

        params = urllib.urlencode(postData)
        header = HEADER
        header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        header['Accept-Encoding'] = 'gzip,deflate,sdch'
        header['Accept-Language'] = 'zh-CN,zh;q=0.8'
        header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36'
        header['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(URL_BAIDU_LOGIN, data=params, headers=header, verify=False)
        self.BAIDU_CHANGE_CAP = "https://passport.baidu.com/v2/?reggetcodestr&token=" + self.tokenVal + \
            '&tpl=mn&apiver=v3&tt=' + get_tt() + '&fr=login'
        if int(r.status_code) != 200:
            raise NetworkError, u'表单上传失败'

        if not self.islogin():
            postData['verifycode'], postData['codestring'] = self.__download_captcha()
            params = urllib.urlencode(postData)
            r = requests.post(URL_BAIDU_LOGIN, data=params, headers=header, verify=False)
        if self.islogin():
        # requests.cookies.save()
            print u"登录成功"
            return True
        else:
            raise NetworkError, u"Username or Password error! Please check!"


    def fetch(self, url):
        r = requests.get(url, allow_redirects=False, verify=False)
        return r.content

    def islogin(self):
        header = HEADER
        header['Accept-Encoding'] = 'gzip, deflate, sdch'
        header['Referer'] = 'https://www.baidu.com/'

        url = "http://i.baidu.com/"
        r = requests.get(url, headers=header, allow_redirects=False, verify=False)
        status_code = int(r.status_code)
        if status_code == 302:
            return False
        elif status_code == 200:
            requests.cookies.save()
            return True
        else:
            raise NetworkError, u'网络故障'

    def __change_cap_url(self):
        """
        获取百度登录验证码地址
        :return:
        """
        r = requests.get(self.BAIDU_CHANGE_CAP, headers=HEADER, verify=False)
        status_code = int(r.status_code)
        # print r.content
        if status_code == 200:
            msg = json.loads(r.content)
            return msg["data"]["verifyStr"]

    def __download_captcha(self):
        """
        下载验证码
        :return:
        """
        codeString = self.__change_cap_url()
        url = BAIDU_CAT_URL_MAIN + codeString
        r = requests.get(url, headers=HEADER, verify=False)
        if int(r.status_code) != 200:
            raise NetworkError(), u"验证码请求失败"
        image_name = u"verify." + r.headers['content-type'].split("/")[1]
        open(image_name,"wb").write(r.content)

        print u"正在调用外部程序渲染验证码...\n" \
              u"或者手动打开代码目录下verify.*文件查看并填写验证码!"
        if platform.system() == "Linux":
            print u"Command: xdg-open %s &" % image_name
            os.system("xdg-open %s &" % image_name)
        elif platform.system() == "Darwin":
            print u"Command: open %s &" % image_name
            os.system("open %s &" % image_name)
        elif platform.system() == "SunOS":
            os.system("open %s &" % image_name)
        elif platform.system() == "FreeBSD":
            os.system("open %s &" % image_name)
        elif platform.system() == "Unix":
            os.system("open %s &" % image_name)
        elif platform.system() == "OpenBSD":
            os.system("open %s &" % image_name)
        elif platform.system() == "NetBSD":
            os.system("open %s &" % image_name)
        elif platform.system() == "Windows":
            os.system("%s" % image_name)
        else:
            print u"我们无法探测你的作业系统，请自行打开验证码 %s 文件，并输入验证码:" % os.path.join(os.getcwd(), image_name)
        verifycode = raw_input(u"Please enter the captcha:")
        return self.__check_captcha(verifycode, codeString)

    def __check_captcha(self,verifycode, codeString):
        """
        查询验证码正确与否
        :param verifycode:
        :param codeString:
        :return:
        """
        check_url = "https://passport.baidu.com/v2/?checkvcode&token=" \
                    + self.tokenVal + "&tpl=mn&apiver=v3&tt="+get_tt()+"&verifycode="+verifycode+"&codestring="+ codeString + \
                    "&callback=bd__cbs__r4gm19"
        r = requests.get(check_url, headers=HEADER, verify=False)
        # print r.content
        # print check_url
        if "success" not in r.content:
            print u"验证输入错误，请重新输入!\n"
            self.__download_captcha()
        else:
            return verifycode, codeString

    def postdata(self, url, param, headers):
        req = requests.post(url, data=param, headers=headers, verify=False)
        return req


if __name__ == '__main__':
    pass
