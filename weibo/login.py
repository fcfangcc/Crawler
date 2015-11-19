# -*- coding: utf8 -*-
__author__ = 'fangc'
# 本代码参考了https://github.com/mabin004/wap_weibo
import urllib2
import urllib
import cookielib
import re
import base64
import rsa
import binascii
from time import sleep
cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
urllib2.install_opener(opener)
URL_LOGIN = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
GET_MSG_URL = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1446098770656'
def getData(url):
    headers={
        "Content-Type":"application/x-www-form-urlencoded",
        "Referer":"http://3g.sina.com.cn/prog/wapsite/sso/login.php",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0"
         }
    request = urllib2.Request(url=url, headers=headers)
    page = urllib2.urlopen(request)
    text = page.read()
    return text

def postData(url, data):
    headers = {
        "Content-Type":"application/x-www-form-urlencoded",
        "Referer":"http://3g.sina.com.cn/prog/wapsite/sso/login.php",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0"
         }
    req = urllib2.Request(url=url, data=data, headers=headers)
    page = urllib2.urlopen(req)
    return page.read()

def login(mobile, password):
    preLogin = getData(GET_MSG_URL+str(mobile))
    servertime = re.findall('"servertime":([0-9]*),', preLogin)[0]
    pubkey = re.findall('"pubkey":"(.*?)",', preLogin)[0]
    rsakv = re.findall('"rsakv":"(.*?)",', preLogin)[0]
    nonce = re.findall('"nonce":"(.*?)",', preLogin)[0]
    # 帐号加密算法
    su = base64.encodestring('帐号(手机号)')[:-1]
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
        urllib2.urlopen(login_url)
        print "Login success!"
    except:
        print 'Login error!'
    sleep(5)

if __name__ == '__main__':
    login('', '')
    # 后面你可以使用getData函数爬取你想要的界面,如爬取某人的首页然后写入文件内
    text = getData('http://weibo.com/u/2316505592')
    with open('namei.txt','w') as f:
        f.write(text.replace('\\', ''))