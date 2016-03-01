# -*- coding: utf8 -*-
__author__ = 'fangc'
# 本代码参考了https://github.com/mabin004/wap_weibo
import urllib
import cookielib
import re
import base64
import rsa
import binascii
import requests
from time import sleep, time

requests = requests.session()
requests.cookies = cookielib.LWPCookieJar('cookies.txt')
try:
    requests.cookies.load(ignore_discard=True, ignore_expires=True)
    print u"从cookie文件读取登录信息成功！"
except:
    print u"从cookie文件读取登录信息失败！"
URL_LOGIN = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
GET_MSG_URL = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_='


def getData(url):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "http://3g.sina.com.cn/prog/wapsite/sso/login.php",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0"
    }
    req = requests.get(url=url, headers=headers)
    text = req.content
    return text


def postData(url, data):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "http://3g.sina.com.cn/prog/wapsite/sso/login.php",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0"
    }
    req = requests.post(url=url, data=data, headers=headers,allow_redirects=False, verify=False)
    text = req.content
    return text


def login(mobile, password):
    preLogin = getData(GET_MSG_URL + str(long(time() * 1000)))
    servertime = re.findall('"servertime":([0-9]*),', preLogin)[0]
    pubkey = re.findall('"pubkey":"(.*?)",', preLogin)[0]
    rsakv = re.findall('"rsakv":"(.*?)",', preLogin)[0]
    nonce = re.findall('"nonce":"(.*?)",', preLogin)[0]
    # 帐号加密算法
    su = base64.encodestring(mobile)[:-1]
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
    sp = binascii.b2a_hex(rsa.encrypt(message, key))
    # post数据
    param = {
        "entry": 'weibo',
        "gateway": 1,
        "savestate": 7,
        "from": '',
        "useticket": 1,
        "pagerefer": 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D',
        "vsnf": 1,
        "su": su,
        "service": 'miniblog',
        "servertime": servertime,
        "nonce": nonce,
        "pwencode": 'rsa2',
        "rsakv": rsakv,
        "sp": sp,
        "sr": "1536*864",
        "encoding": 'UTF-8',
        "prelt": 545,
        "url": 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        "returntype": 'META'
    }
    postdata = urllib.urlencode(param)
    s = postData(URL_LOGIN, postdata)
    try:
        login_url = re.findall("location.replace\(\'(.*?)\'\);", s)[0]
        requests.get(login_url)
        requests.cookies.save(ignore_discard=True, ignore_expires=True)
        print "Login success!\nCookie saved!"
    except:
        print 'Login error!'
    sleep(5)


# if __name__ == '__main__':
    # 后面你可以使用getData函数爬取你想要的界面,如爬取某人的首页然后写入文件内
    # text = getData('http://weibo.com/u/2316505592')
    # with open('namei.txt','w') as f:
    #     f.write(text.replace('\\', ''))

