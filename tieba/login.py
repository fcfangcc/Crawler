# -*- coding: utf8 -*-
import urllib2
import urllib
import cookielib
import re
import time
from lxml.html import soupparser
import json
from tieba import Tieba
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)
HEADER = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Referer": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"
         }
MAIN_URL = "http://tieba.baidu.com/"


class Login(object):
    def __init__(self, USERNAME, PASSWORD):
        self.username = USERNAME
        self.password = PASSWORD
        self.URL_BAIDU_PINGLUN = 'http://tieba.baidu.com/f/commit/post/add'
        self.URL_BAIDU_SIGN = 'http://tieba.baidu.com/sign/add'

    def login(self):
        """
        https://github.com/NotBadPad/baidulogin/edit/master/src/login.py
        :return:
        """
        URL_BAIDU_INDEX = u'http://www.baidu.com/'
        #https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true 也可以用这个
        URL_BAIDU_TOKEN = 'https://passport.baidu.com/v2/api/?getapi&tpl=pp&apiver=v3&class=login'
        URL_BAIDU_LOGIN = 'https://passport.baidu.com/v2/api/?login'

        #设置cookie，这里cookiejar可自动管理，无需手动指定
        reqReturn = urllib2.urlopen(URL_BAIDU_INDEX)

        #获取token,
        tokenReturn = urllib2.urlopen(URL_BAIDU_TOKEN)
        matchVal = re.search(u'"token" : "(?P<tokenVal>.*?)"',tokenReturn.read())
        tokenVal = matchVal.group('tokenVal')
        #构造登录请求参数，该请求数据是通过抓包获得，对应https://passport.baidu.com/v2/api/?login请求
        postData = {
            'username': self.username,
            'password': self.password,
            'u': 'https://passport.baidu.com/',
            'tpl': 'pp',
            'token': tokenVal,
            'staticpage': 'https://passport.baidu.com/static/passpc-account/html/v3Jump.html',
            'isPhone': 'false',
            'charset': 'UTF-8',
            'callback': 'parent.bd__pcbs__ra48vi'
            }

        postData = urllib.urlencode(postData)

        #发送登录请求
        loginRequest = urllib2.Request(URL_BAIDU_LOGIN,postData)
        loginRequest.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        loginRequest.add_header('Accept-Encoding','gzip,deflate,sdch')
        loginRequest.add_header('Accept-Language','zh-CN,zh;q=0.8')
        loginRequest.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36')
        loginRequest.add_header('Content-Type','application/x-www-form-urlencoded')
        sendPost = urllib2.urlopen(loginRequest)

    def fetch(self, url):
        """
        可以使用此函数来打开需要登录才能看到的页面，如个人首页
        记得先login
        :param url:
        :return:
        """
        #http://tieba.baidu.com/home/main?un=XXXX&fr=index 这个是贴吧个人主页，各项信息都可以在此找到链接
        content = urllib2.urlopen(url).read()
        return content

    def __postdata(self, url, param, headers):
        req = urllib2.Request(url=url, data=param, headers=headers)
        urllib2.urlopen(req).read()
        return True

    def reply(self, response, tie_num):
        """
        回复帖子函数
        :param response: 需要回复的内容
        :param tie_num: 帖子的号码
        :return:
        """
        url = "http://tieba.baidu.com/p/" + str(tie_num) + "/submit"
        msg = self.__get_msg(url)
        print msg
        data = {'ie': 'utf-8',
                'content': response,
                'kw': msg['kw'].encode('utf-8'),
                'fid': msg['fid'],
                "tid": msg['tid'],
                "vcode_md5": "",
                "floor_num": msg['floor_num'],
                "rich_text": 1,
                "tbs": msg['tbs'],
                "files": "[]",
                "sign_id": msg['sign_id'],
                "mouse_pwd": "23,21,16,15,18,20,23,27,42,18,15,19,15,18,15,19,15,18,15,19,15,18,15,19,15,18,15,19,42,18,16,22,26,19,42,18,26,17,19,15,18,19,27,19," + str(int(time.time()*10000)),
                "mouse_pwd_t": msg["mouse_pwd_t"],
                "mouse_pwd_isclick": 0,
                "__type__": "reply"
                }
        postdata = urllib.urlencode(data)
        HEADER['Referer'] = url
        self.__postdata(self.URL_BAIDU_PINGLUN, postdata, HEADER)
        # req = urllib2.Request(url=self.URL_BAIDU_PINGLUN, data=postdata, headers=HEADER)
        # content = urllib2.urlopen(req).read()
        return True

    def __get_msg(self, url):
        """
        获取post数据所需要的各种参数，通过游览器查看得出
        唯一有疑问的是mouse_pwd这个参数，在我电脑上实验这个参数可以顺利评论帖子
        如出现不能post可根据你游览器截获到的参数修改
        :param url:
        :return:
        """
        dictory = {}
        text = self.fetch(url)
        text2 = self.fetch("http://tieba.baidu.com/f/user/sign_list?t=" + str(int(time.time()*10000)))
        soup = soupparser.fromstring(text)
        msg = soup.xpath(".//*[@type='hidden']")[0]
        dictory['kw'] = msg.attrib['value']
        dictory['floor_num'] = re.findall("reply_num:([0-9]*),", text)[0]
        dictory['tid'] = re.findall("thread_id:([0-9]*),", text)[0]
        dictory['fid'] = re.findall('"forum_id":([0-9]*),', text)[0]
        dictory['tbs'] = re.findall('"tbs": "([\w]*)",', text)[0]
        dictory["sign_id"] = json.loads(text2.decode("gbk"))['data']['used_id']
        dictory["mouse_pwd_t"] = int(time.time())
        return dictory

    def sign(self, name):
        """
        对贴吧签到，前提需要loggin()
        如果签到成功或者已经签到，返回True
        如果签到失败返回False
        使用方法:
        login = Login(username,password)
        login.login()
        login.sign("杭州")
        :param name:
        :return:
        """
        tieba = Tieba(name)
        url = tieba.get_tieba_url()
        if self.__issign(url):
            return True
        html = tieba.get_tieba_html()
        try:
            tbs = re.findall("'tbs':'([\w]*)'", html)[0]
        except:
            tbs = re.findall(''''tbs': "([\w]*)"''', html)[0]
        data = {'ie': 'utf-8',
                'kw': name,
                'tbs': tbs,
                }
        postdata = urllib.urlencode(data)
        HEADER['Referer'] = url
        HEADER['Cache-Control'] = 'no-cache'
        self.__postdata(self.URL_BAIDU_SIGN, postdata, HEADER)
        # req = urllib2.Request(url=self.URL_BAIDU_SIGN, data=postdata, headers=HEADER)
        # content = urllib2.urlopen(req).read()
        if self.__issign(url):
            return True
        else:
            return False

    def __issign(self, url):
        content = self.fetch(url)
        soup = soupparser.fromstring(content)
        if soup.xpath('.//*[@class="sign_keep_span"]'):
            return True
        else:
            return False

    # 还在测试中，暂时不开放
    def __follow(self, name):
        """
        关注贴吧，前提需要loggin()
        如果已经关注或者关注成功，返回True
        如果关注失败返回False
        使用方法:
        login = Login(username,password)
        login.login()
        login.follow("杭州")
        :param name:
        :return:
        """
        tieba = Tieba(name)
        url = tieba.get_tieba_url()
        if self.__isfollow(url):
            return True
        html = tieba.get_tieba_html()
        tbs = re.findall("'tbs':'([\w]*)'", html)[0]
        fid = re.findall('"forum_id":([0-9]*),', html)[0]
        data = {'ie': 'gbk',
                'fid': fid,
                'fname': name,
                'uid': self.username,
                'tbs': tbs,
                }
        postdata = urllib.urlencode(data)
        URL_BAIDU_DELETE = 'http://tieba.baidu.com/f/like/commit/add'
        HEADER['Referer'] = url
        HEADER['Cache-Control'] = 'no-cache'
        self.__postdata(URL_BAIDU_DELETE, postdata, HEADER)
        if self.__isfollow(url):
            return True
        else:
            return False

    # 还在测试中，暂时不开放
    def __remove_follow(self, name):
        """
        取消关注贴吧，前提需要loggin()
        如果已经取消关注或者取消关注成功，返回True
        如果取消关注失败返回False
        使用方法:
        login = Login(username,password)
        login.login()
        login.remove_follow("杭州")
        :param name:
        :return:
        """
        tieba = Tieba(name)
        url = tieba.get_tieba_url()
        if not self.__isfollow(url):
            return True
        html = tieba.get_tieba_html()
        try:
            tbs = re.findall("'tbs':'([\w]*)'", html)[0]
        except:
            tbs = re.findall(''''tbs': "([\w]*)"''', html)[0]
        fid = re.findall('"forum_id":([0-9]*),', html)[0]
        data = {'ie': 'utf-8',
                'fid': fid,
                'fname': name,
                'uid': urllib.quote(self.username)+'&ie=utf-8',
                'tbs': tbs,
                }
        postdata = urllib.urlencode(data)
        URL_BAIDU_DELETE = 'http://tieba.baidu.com/f/like/commit/delete'
        HEADER['Referer'] = url
        HEADER['Accept'] = '*/*'
        HEADER['Content-Length'] = len(postdata)
        HEADER['X-Requested-With'] = 'XMLHttpRequest'
        HEADER['host'] = 'tieba.baidu.com'
        HEADER['Cache-Control'] = 'no-cache'
        HEADER['Connection'] = 'Keep-Alive'
        print postdata
        self.__postdata(URL_BAIDU_DELETE, postdata, HEADER)
        if not self.__isfollow(url):
            return True
        else:
            return False

    def __isfollow(self, url):
        content = self.fetch(url)
        soup = soupparser.fromstring(content)
        if soup.xpath('.//*[@class="focus_btn cancel_focus"]'):
            return True
        elif soup.xpath('.//*[@class="focus_btn islike_focus"]'):
            return False
        else:
            raise Exception,u'贴吧版本已更新，此函数以弃用，请通知swjfc22@163.com更新代码，谢谢！'

if __name__ == "__main__":
    # "http://tieba.baidu.com/f?kw=陈法拉&fr=index"
    # then you can do everything
    pass




