# -*- coding: utf8 -*-
import requests
import re
import platform, os
import cookielib
import json
import urllib
import time
import sys

requests.packages.urllib3.disable_warnings()


# todo:修改windows命令行下登录失败的问题,还未定位到问题原因
def get_tt():
    return str(int(time.time() * 1000))


requests = requests.session()
requests.cookies = cookielib.LWPCookieJar('cookies.txt')

try:
    requests.cookies.load(ignore_discard=True, ignore_expires=True)
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
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.URL_BAIDU_SIGN = 'http://tieba.baidu.com/sign/add'

    def login_choice(self):
        print(u"请选择登录方式:\n"
                  u"1:帐号密码登录(不支持手机号登录).\n"
                  u"2:手机百度扫描二维码登录.\n"
                  u"请输入号码:")
        login_type = int(raw_input())
        if login_type == 1:
            print(u"请输入帐号:")
            self.username = raw_input()
            print(u"请输入密码:")
            self.password = raw_input()
            self.login()
        elif login_type == 2:
            self.login_qrcode()
        else:
            print(u"输入错误信息！程序将退出")
            sys.exit()

    def login(self):
        if self.islogin():
            print u"已从cookie加载配置，登录成功!"
            return True
        if not (self.username and self.password):
            print u"从cookie文件加载配置失败，请提供用户名密码!"
            return False
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
        header[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36'
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

    def login_qrcode(self):
        """
        通过扫描二维码登录百度
        :return: True or False
        """
        if self.islogin():
            print u"已从cookie加载配置，登录成功!"
            return True
        else:
            print u"请用手机百度扫描二维码登录!"
        global gid
        global bduss
        gid = self.create_gid()
        params = {
            "lp": "pc",
            "gid": gid,
            "apiver": "v3",
            "tt": get_tt(),
            "callback": "bd__cbs__zh5cgp",
        }
        BdQrUrl = "https://passport.baidu.com/v2/api/getqrcode"
        BdQrGetUrl = "http://passport.baidu.com/v2/api/qrcode?sign="
        headers = HEADER
        req = requests.get(url=BdQrUrl, params=params, headers=headers, allow_redirects=False, verify=False)
        if req.status_code != 200:
            raise NetworkError(), u"发生未知错误!"
        sign_id = re.findall('"sign":"([\w]*)"', req.text)[0]
        BdQrGetUrl += sign_id
        r = requests.get(url=BdQrGetUrl, headers=HEADER, verify=False)
        if int(r.status_code) != 200:
            raise NetworkError(), u"二维码请求失败!"
        image_name = u"qrcode." + r.headers['content-type'].split("/")[1]
        open(image_name, "wb").write(r.content)
        self.open_img(image_name)
        # 下面判断是否已经扫码并登录
        params = {
            "channel_id": sign_id,
            "tpl": "mn",
            "gid": gid,
            "apiver": "v3",
            "callback": "bd__cbs__j7a2vw",
            "tt": get_tt(),
        }
        BdQrExist = "https://passport.baidu.com/channel/unicast"
        status = 1
        while status == 1:
            try:
                # 返回0是表示已经扫描，返回1表示还未扫描
                text = requests.get(url=BdQrExist, params=params, headers=headers, allow_redirects=False,
                                    verify=False).content
                status = int(re.findall('"errno":([0-1]*)', text)[0])
                print u"请按手机的提示操作!"
            except Exception as e:
                print e
        # 下面判断是否点击登录，并获取得到bduss的v
        while status == 0:
            try:
                text = requests.get(url=BdQrExist, params=params, headers=headers, allow_redirects=False,
                                    verify=False).content
                v = re.findall(r'\\"v\\":\\"([\w]*)\\"', text)[0]
                print(u"获取关键参数V成功!")
                status = 1
            except Exception as e:
                print e
        # 再进行登录操作,通过v获取budss
        params = {
            "u": "https://www.baidu.com/",
            "bduss": v,
            "tpl": "mn",
            "gid": gid,
            "apiver": "v3",
            "callback": "bd__cbs__551o7a",
            "tt": get_tt(),
        }
        BdLoginUrl = "https://passport.baidu.com/v2/api/bdusslogin"
        req = requests.get(url=BdLoginUrl, params=params, headers=headers, allow_redirects=False)
        # print req.cookies['BDUSS']
        if req.status_code == 200:
            requests.cookies.save(ignore_discard=True, ignore_expires=True)
            print(u"登录成功！")
            return True
        else:
            print u"未知错误！可能百度修改了接口!"

    def fetch(self, url):
        r = requests.get(url, allow_redirects=False, verify=False).content
        return r

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
            # ignore_discard: save even cookies set to be discarded.
            # ignore_expires: save even cookies that have expiredThe file is overwritten if it already exists
            requests.cookies.save(ignore_discard=True, ignore_expires=True)
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
        open(image_name, "wb").write(r.content)

        self.open_img(image_name)
        verifycode = raw_input(u"Please enter the captcha:")
        return self.__check_captcha(verifycode, codeString)

    def __check_captcha(self, verifycode, codeString):
        """
        查询验证码正确与否
        :param verifycode:
        :param codeString:
        :return:
        """
        check_url = "https://passport.baidu.com/v2/?checkvcode&token=" \
                    + self.tokenVal + "&tpl=mn&apiver=v3&tt=" + get_tt() + "&verifycode=" + verifycode + "&codestring=" + codeString + \
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

    @staticmethod
    def create_gid():
        from random import random
        key = ''
        for i in xrange(7):
            key += hex(int(random() * 16))[2:]
        key += '-'
        for i in xrange(4):
            key += hex(int(random() * 16))[2:]
        key += '-4'
        for i in xrange(3):
            key += hex(int(random() * 16))[2:]
        key += '-'
        for i in xrange(4):
            key += hex(int(random() * 16))[2:]
        key += '-'
        for i in xrange(12):
            key += hex(int(random() * 16))[2:]
        return key.upper()

    @staticmethod
    def open_img(image_name):
        print u"正在调用外部程序渲染验证码...\n" \
              u"或者手动打开代码目录下'{}'文件查看并填写验证码!".format(image_name)
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
            os.startfile(image_name)
        else:
            print u"我们无法探测你的作业系统，请自行打开验证码 %s 文件，并输入验证码:" % os.path.join(os.getcwd(), image_name)

# if __name__ == '__main__':
#     pass
