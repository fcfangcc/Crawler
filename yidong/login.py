# -*- coding: utf8 -*-
# 模拟登录中国移动网上营业厅
_author__ = 'fangc'
import urllib2
import urllib
import cookielib

cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
urllib2.install_opener(opener)
URL_LOGIN = 'https://zj.ac.10086.cn/login'
URL_IMG = 'https://zj.ac.10086.cn/ImgDisp'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0"}
params = {
    "service": 'my',
    "continue": '/my/login/loginSuccess.do',
    "failurl": 'https://zj.ac.10086.cn/login',
    "style": 1,
    "pwdType": 2,
    "SMSpwdType": 0,
    "billID": '',
    "mima": 'fuwumima',
    "passwd1": "%CD%FC%BC%C7%C3%DC%C2%EB%A3%BF%BF%C9%D3%C3%B6%CC%D0%C5%D1%E9%D6%A4%C2%EB%B5%C7%C2%BC",
    "passwd": '',
    "validCodeId1": '5%B8%F6%D7%D6%B7%FB',
    "validCode": '',
}

def login(tel, passwd):
    img_msg = urllib2.urlopen('https://zj.ac.10086.cn/ImgDisp').read()
    with open('a.png', 'wb') as f:
        f.write(img_msg)
    img = raw_input("请输入验证码:")
    params["billID"] = tel
    params["validCode"] = img
    params["passwd"] = passwd
    postdata = urllib.urlencode(params)
    req = urllib2.Request(url=URL_LOGIN, data=postdata, headers=headers)
    page = urllib2.urlopen(req)
    return page.read()


if __name__ == '__main__':
    login('****', '****')
