# -*- coding: utf8 -*-
__author__ = 'fangc'
import requests
import re
import platform, os
import cookielib
import json
import time
import sys
import copy
from urllib import urlencode
from requests.packages.urllib3.exceptions import InsecureRequestWarning, InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)


# todo:修改windows命令行下登录失败的问题,还未定位到问题原因
def get_tt():
    return str(int(time.time() * 1000))


requests = requests.session()
requests.cookies = cookielib.LWPCookieJar('cookies.txt')

try:
    requests.cookies.load(ignore_discard=True, ignore_expires=True)
    print u"从cookie文件读取登录信息"
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
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Login2(object):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.URL_BAIDU_SIGN = 'http://tieba.baidu.com/sign/add'

    def login_choice(self):
        """选择登录的方式.
        1:帐号密码登录.2:扫描二维码登录
        :return:
        """
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
        """帐号密码登录.
        :return: True or False
        """
        if self.islogin():
            print u"已从cookie加载配置，登录成功!"
            return True
        if not (self.username and self.password):
            print u"从cookie文件加载配置失败，请提供用户名密码!"
            return False
        URL_BAIDU_TOKEN = 'https://passport.baidu.com/v2/api/?getapi&tpl=pp&apiver=v3&class=login'
        URL_BAIDU_LOGIN = 'https://passport.baidu.com/v2/api/?login'
        headers = copy.deepcopy(HEADER)
        requests.get(URL_BAIDU_TOKEN, verify=False, headers=headers)  # 先连接一下获取到cookie，不然会获取不到token
        time.sleep(1)
        tokenReturn = requests.get(URL_BAIDU_TOKEN, verify=False, headers=headers).content
        matchVal = re.search(u'"token" : "(?P<tokenVal>.*?)"', tokenReturn)
        self.tokenVal = matchVal.group('tokenVal')
        params = {
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
        # 据说这里顺序不能变化
        # postdata = urllib.urlencode(params)
        header = HEADER
        header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        header['Accept-Encoding'] = 'gzip,deflate,sdch'
        header['Accept-Language'] = 'zh-CN,zh;q=0.8'
        header[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36'
        header['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(URL_BAIDU_LOGIN, params=params, headers=header, verify=False)
        self.baidu_change_cap = "https://passport.baidu.com/v2/?reggetcodestr&token=" + self.tokenVal + \
                                '&tpl=mn&apiver=v3&tt=' + get_tt() + '&fr=login'

        if int(r.status_code) != 200:
            raise NetworkError(u'表单上传失败')

        if not self.islogin():
            params['verifycode'], params['codestring'] = self.__download_captcha()
            # 这里使用params=params会报错，无法登录，原因未知！
            postdata = urlencode(params)
            r = requests.post(URL_BAIDU_LOGIN, data=postdata, headers=header, verify=False)
            if not self.islogin():
                raise NetworkError(u"发生未知错误!")
            print u"登录成功"
        else:
            print u"登录成功"
            return True

    def login_qrcode(self):
        """通过扫描二维码登录百度.
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
            raise NetworkError(u"可能百度修改了接口！")
        sign_id = re.findall('"sign":"([\w]*)"', req.text)[0]  # 获取sign_id
        BdQrGetUrl += sign_id
        r = requests.get(url=BdQrGetUrl, headers=HEADER, verify=False)  # 获取二维码
        if int(r.status_code) != 200:
            raise NetworkError(u"二维码请求失败!")
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
        # 再进行登录操作,通过v获取bduss
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
        if req.status_code == 200:
            requests.cookies.save(ignore_discard=True, ignore_expires=True)
            print(u"登录成功！")
            return True
        else:
            print u"未知错误！可能百度修改了接口!"

    def islogin(self):
        """判断是否已经成功登录.
        :return: True or False
        """
        header = copy.deepcopy(HEADER)
        header['Accept-Encoding'] = 'gzip, deflate, sdch'
        header['Host'] = 'i.baidu.com'
        url = "http://i.baidu.com/"
        r = requests.get(url, headers=header, allow_redirects=False, verify=False)
        status_code = int(r.status_code)
        # print status_code
        if status_code == 302:
            return False
        elif status_code == 200:
            # ignore_discard: save even cookies set to be discarded.
            # ignore_expires: save even cookies that have expiredThe file is overwritten if it already exists
            requests.cookies.save(ignore_discard=True, ignore_expires=True)
            return True
        else:
            raise NetworkError(u'网络故障')

    def __change_cap_url(self):
        """获取百度登录验证码编号.
        :return: 百度验证码verifyStr
        """
        r = requests.get(self.baidu_change_cap, headers=HEADER, verify=False)
        status_code = int(r.status_code)
        if status_code == 200:
            msg = json.loads(r.content)
            return msg["data"]["verifyStr"]

    def __download_captcha(self):
        """下载验证码.
        :return: (verifycode, codeString)
        """
        codeString = self.__change_cap_url()
        url = BAIDU_CAT_URL_MAIN + codeString
        r = requests.get(url, headers=HEADER, verify=False, allow_redirects=False)
        if int(r.status_code) == 503:
            print u"获取验证码失败，正在重新获取......"
            self.__download_captcha()
        elif int(r.status_code) != 200:
            raise NetworkError(u"验证码请求失败")
        else:
            pass
        image_name = u"verify." + r.headers['content-type'].split("/")[1]
        if "html" in image_name:
            raise NetworkError(u"百度验证码服务器发生错误，请重试。或使用扫描二维码登录")
        else:
            open(image_name, "wb").write(r.content)
            self.open_img(image_name)
        verifycode = raw_input(u"Please enter the captcha:")
        return self.__check_captcha(verifycode, codeString)

    def __check_captcha(self, verifycode, codeString):
        """查询验证码正确与否.
        :param verifycode: 验证码
        :param codeString: 验证码编号
        :return: 如果验证码正确返回(verifycode, codeString)
        """
        check_url = "https://passport.baidu.com/v2/?checkvcode&token=" \
                    + self.tokenVal + "&tpl=mn&apiver=v3&tt=" + get_tt() + "&verifycode=" + verifycode + "&codestring=" + codeString + \
                    "&callback=bd__cbs__r4gm19"
        r = requests.get(check_url, headers=HEADER, verify=False)
        if "success" not in r.content:
            print "---------------------------------------------------"
            print u"验证输入错误，请重新输入!\n" \
                  u"或者帐号密码错误,请确认!"
            self.__download_captcha()
        else:
            return verifycode, codeString

    @staticmethod
    def create_gid():
        """创建随机的gid，获取bduss需要用到.
        :return:
        """
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
        """打开图片验证码和二维码方法.
        :param image_name: 图片地址
        :return:
        """
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