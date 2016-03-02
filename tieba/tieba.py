# -*- coding: UTF-8 -*-
__author__ = 'fangc'
from lxml.html import soupparser
import urllib
from urlparse import urljoin
import requests
import sys
import os
import shutil
import json
import re
from login import Login2
import time
import cookielib

HEADER = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"
}

HEADERS = {'content-type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

MAIN_URL = "http://tieba.baidu.com/"
URL_BAIDU_SIGN = 'http://tieba.baidu.com/sign/add'
URL_BAIDU_THREAD = 'http://tieba.baidu.com/f/commit/thread/add'
URL_BAIDU_SIGN_ALL = 'http://tieba.baidu.com/tbmall/onekeySignin1'
URL_BAIDU_USER_FOLLOW = 'http://tieba.baidu.com/home/post/follow'
URL_BAIDU_USER_UNFOLLOW = 'http://tieba.baidu.com/home/post/unfollow'
URL_BAIDU_REPLY = 'http://tieba.baidu.com/f/commit/post/add'
URL_BAIDU_COLLECTION = 'http://tieba.baidu.com/i/submit/open_storethread'
URL_BAIDU_UNCOLLECTION = 'http://tieba.baidu.com/i/submit/cancel_storethread'
requests.packages.urllib3.disable_warnings()
requests = requests.session()
requests.cookies = cookielib.LWPCookieJar('cookies.txt')
# 代表登录状态
LOGIN_STATUS = False


def islogin():
    """
    判断是否已经成功登陆的函数
    :return: True or False
    """
    header = HEADER
    header['Accept-Encoding'] = 'gzip, deflate, sdch'
    header['Referer'] = 'https://www.baidu.com/'
    url = "http://i.baidu.com/"
    r = requests.get(url, headers=header, allow_redirects=False, verify=False)
    status_code = int(r.status_code)
    if status_code == 302:
        return False
    elif status_code == 200:
        return True
    else:
        raise Exception, u'网络故障'


try:
    requests.cookies.load(ignore_discard=True, ignore_expires=True)
    if islogin():
        print(u"从cookie文件加载配置成功!")
        LOGIN_STATUS = True
    else:
        LOGIN_STATUS = False
except:
    print(u"未检测到cookie文件")
    LOGIN_STATUS = False


def user_main(name):
    """
    修改用户名编码的函数
    :param name:
    :return:
    """
    name = name.decode('UTF-8').encode('gbk')
    url = "http://tieba.baidu.com/home/main?un=" + repr(name) + "&fr=ihome"
    url = url.replace("\'", "").replace("\\x", "%")
    return url


def is_login(func):
    """
    需要登录才能操作的方法加的装饰器,如果没登录则登录
    :param func:
    :return:
    """

    def _func(*args, **kwargs):
        global LOGIN_STATUS
        if LOGIN_STATUS:
            func(*args, **kwargs)
        else:
            login = Login2()
            login.login_choice()
            time.sleep(1)
            try:
                requests.cookies.load(ignore_discard=True, ignore_expires=True)
                LOGIN_STATUS = True
                func(*args, **kwargs)
            except Exception as e:
                print e

    return _func


class InputErrorStr(Exception):
    pass


class TieziError(Exception):
    pass


class TiebaError(Exception):
    pass


class UserError(Exception):
    pass


class User(object):
    """用户操作类.
    对于需要登录才能操作的方法，需要提供用户名密码或者有cookie文件。
    """

    def __init__(self, user):
        self.set_user(user)

    def get_followba(self):
        """
        返回用户关注的贴吧
        :return:
        """
        followBa = self.userHtml.findall('.//*[@id="forum_group_wrap"]/a/span')
        j = 0
        dictionary = {}
        key = ''
        for i in followBa:
            if j % 2 == 0:
                key = i.text
                dictionary[key] = 0
            else:
                dictionary[key] = i.attrib['class'].split(' ')[1]
            j += 1
        return dictionary

    def get_num_tiezi(self):
        """
        返回总的发帖数
        :return:
        """
        num = self.userHtml.find('.//*[@id="userinfo_wrap"]/div[2]/div[3]/div/span[4]')
        return num.text

    def get_age(self):
        """
        获取用户吧龄
        :return:
        """
        age = self.userHtml.find('.//*[@id="userinfo_wrap"]/div[2]/div[3]/div/span[2]')
        return age.text

    def get_sex(self):
        """
        返回用户性别
        :return:
        """
        sex = self.userHtml.find('.//*[@id="userinfo_wrap"]/div[2]/div[3]/div/span[1]')
        return sex.attrib['class']

    def get_followme(self, type='all'):
        """
        根据输入的type来返回对应的值：
        "all":{关注我的数量,{用户：主页地址...}}
        "num":关注我的数量
        "users":{用户：主页地址...}
        :param
        :return:
        """
        if self.userHtml.find('.//*[@id="container"]/div[2]/div[4]/h1/span'):
            followme_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[4]/h1/span')
        elif self.userHtml.find('.//*[@id="container"]/div[2]/div[3]/h1/span') is not None and \
                        self.userHtml.find('.//*[@id="container"]/div[2]/div[3]')[0].text in [u"关注他的人", u"关注她的人"]:
            followme_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[3]/h1/span')
        elif self.userHtml.find('.//*[@id="container"]/div[2]/div[2]/h1/span') is not None and \
                        self.userHtml.find('.//*[@id="container"]/div[2]/div[2]')[0].text in [u"关注他的人", u"关注她的人"]:
            followme_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[2]/h1/span')
        else:
            return u"没有人关注此用户"
        followmesurl = urljoin(MAIN_URL, followme_url.attrib['href'])
        soup = soupparser.fromstring(requests.get(followmesurl, verify=False).content)
        page_next = soup.xpath('.//*[@class="next"]')
        names = soup.xpath('.//*[@id="search_list"]/div/div[2]/span[1]/a')
        if type == 'num':
            return followme_url.text
        else:
            usermsg = dict([(name.text, urljoin(MAIN_URL, name.attrib['href'])) for name in names])
            while page_next:
                url_next = urljoin(MAIN_URL, page_next[0].attrib['href'])
                soup_next = soupparser.fromstring(requests.get(url_next, verify=False).content)
                names = soup_next.xpath('.//*[@id="search_list"]/div/div[2]/span[1]/a')
                for name in names:
                    usermsg[name.text] = urljoin(MAIN_URL, name.attrib['href'])
                page_next = soup_next.xpath('.//*[@class="next"]')
            if type == 'all':
                return followme_url.text, usermsg
            elif type == 'users':
                return usermsg
            else:
                raise InputErrorStr, 'STR ERROR ,it can only input num,all,users!'

    def get_ifollow(self, type='all'):
        """
        根据输入的type来返回对应的值：
        "all":{我关注的数量,{用户：主页地址...}}
        "num":我关注的数量
        "users":{用户：主页地址...}
        :param type:
        :return:
        """
        if self.userHtml.find('.//*[@id="container"]/div[2]/div[3]/h1/span') is not None and \
                        self.userHtml.find('.//*[@id="container"]/div[2]/div[3]')[0].text in [u"他关注的人", u"她关注的人"]:
            ifollow_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[3]/h1/span')
        elif self.userHtml.find('.//*[@id="container"]/div[2]/div[2]/h1/span') is not None and \
                        self.userHtml.find('.//*[@id="container"]/div[2]/div[2]')[0].text in [u"他关注的人", u"她关注的人"]:
            ifollow_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[2]/h1/span')
        else:
            return u"此用户未关注任何人"
        ifollowurl = urljoin(MAIN_URL, ifollow_url.attrib['href'])
        soup = soupparser.fromstring(requests.get(ifollowurl, verify=False).content)
        page_next = soup.xpath('.//*[@class="next"]')
        names = soup.xpath('.//*[@id="search_list"]/div/div[2]/span[1]/a')
        if type == 'num':
            return ifollow_url.text
        else:
            usermsg = dict([(name.text, urljoin(MAIN_URL, name.attrib['href'])) for name in names])
            while page_next:
                url_next = urljoin(MAIN_URL, page_next[0].attrib['href'])
                soup_next = soupparser.fromstring(requests.get(url_next, verify=False).content)
                names = soup_next.xpath('.//*[@id="search_list"]/div/div[2]/span[1]/a')
                for name in names:
                    usermsg[name.text] = urljoin(MAIN_URL, name.attrib['href'])
                page_next = soup_next.xpath('.//*[@class="next"]')
            if type == 'all':
                return ifollow_url.text, usermsg
            elif type == 'users':
                return usermsg
            else:
                raise InputErrorStr, 'STR ERROR ,it can only input num,all,users!'

    def get_recently_tie(self, num=10):
        """
        返回用户最近的回帖信息
        :param num:
        :return:
        """
        self.__hide_status()
        if self.userHtml.find('.//*[@id="container"]/div[1]/div/div[3]').text:
            return u"该用户已隐藏个人动态"
        times = self.userHtml.findall('.//*[@id="container"]/div[1]/div/div[3]/ul/div/div[1]')
        replys = self.userHtml.findall('.//*[@id="container"]/div[1]/div/div[3]/ul/div/div[3]/div[1]/div/')
        titles = self.userHtml.findall('.//*[@id="container"]/div[1]/div/div[3]/ul/div/div[3]/div[2]/a[1]')
        names = self.userHtml.findall('.//*[@id="container"]/div[1]/div/div[3]/ul/div/div[3]/div[2]/a[2]')
        num = len(replys) if num > len(replys) else num
        replydict = dict([(i, dict(
            [('reply', replys[i].text), ('title', titles[i].text), ('name', names[i].text), ('time', times[i].text)]))
                          for i in xrange(num)])
        return replydict

    def __hide_status(self):
        if 'his_thread_blank' in self.req.content:
            raise UserError, u'用户已经隐藏个人状态,无法获取该信息.'
        else:
            return False

    def set_user(self, user):
        """
        更改目标用户昵称,继续进行挖掘数据.
        :param user:
        :return:
        """
        self.user = user
        self.url = user_main(user)
        self.req = requests.get(self.url, headers=HEADERS, allow_redirects=False, verify=False)
        if int(self.req.status_code) != 200:
            raise UserError, u"用户不存在"
        self.userHtml = soupparser.fromstring(self.req.content)

    def __follow_templates(self, post_url):
        """
        关注/取消关注数据
        :return:
        """
        t = requests.get(url=self.url, allow_redirects=False, verify=False).content
        tbs = re.findall("'tbs':'([\w]*)'", t)[0]
        un = self.user
        data = {
            'ie': 'utf-8',
            'un': un,
            'tbs': tbs,
        }
        postdata = urllib.urlencode(data)
        headers = HEADER
        headers['Content-Length'] = len(postdata)
        headers['Referer'] = self.url
        r = requests.post(url=post_url, data=postdata, headers=headers, verify=False)
        # print r.status_code
        # print r.headers
        return int(r.status_code)

    @is_login
    def unfollow(self):
        """
        关注此用户
        :return: True or False
        """
        status = self.__follow_templates(URL_BAIDU_USER_UNFOLLOW)
        if status == 200:
            return True
        else:
            print(u"取消关注用户:'%s'失败!请登录后重试或者联系作者!" % self.user)
            return False

    @is_login
    def follow(self):
        """
        取消关注此用户
        :return: True or False
        """
        status = self.__follow_templates(URL_BAIDU_USER_FOLLOW)
        if status == 200:
            return True
        else:
            print(u"关注用户:'%s'失败!请登录后重试或者联系作者!" % self.user)
            return False


class Tiezi(object):
    """帖子操作类.
    对于需要登录才能操作的方法，需要提供用户名密码或者有cookie文件。
    """

    def __init__(self, num):
        self.set_tiezi(num)

    def __del__(self):
        pass

    def downloadlz(self, type='txt', start=1, end=5):
        """
        type:txt or photo
        默认下载前5页的内容
        :param :
        :return:
        """
        self.__mkdirfile(self.tienum)
        num = int(self.getnum())
        print u'本帖子楼主共有%d页发表!' % num
        if start > end:
            print u"结束页超过起始页，请检查参数!\n"
            sys.exit()
        elif start > num:
            print u"起始页面超过上限!本帖子一共有 %d 页\n" % num
            sys.exit()
        num = num if num < end else end
        for i in xrange(start - 1, num):
            soup = soupparser.fromstring(requests.get(self.url + str(i + 1), verify=False).content)
            if type == "txt":
                self.__get_lz_txt(i + 1, soup)
            elif type == "photo":
                self.__get_lz_jpg(i + 1, soup)
            else:
                print u"输入的参数有误，只能输入'txt'或者'photo'"

    def __get_lz_txt(self, page, soup):
        """
        下载帖子的只看楼主的所有楼主文字内容
        :param page:
        :param soup:
        :return:
        """
        print u'正在下载第 %d 页内容，请等待......\n' % page
        txts = soup.xpath('.//div[@class="d_post_content j_d_post_content "]/text()')
        if not txts:
            txts = soup.xpath('.//div[@class="d_post_content j_d_post_content  clearfix"]/text()')
        with open("%s/text.txt" % self.tienum, "a+") as f:
            f.writelines(''.join(txts).encode('utf8'))
        f.close()

    def __get_lz_jpg(self, page, soup):
        """
        下载帖子的只看楼主的所有的发布图片
        :param page:
        :param soup:
        :return:
        """
        photos = soup.xpath('//img[@class="BDE_Image"]')
        if len(photos) == 0:
            print u"第%d页没有检测到有楼主发布的图片" % page
            return False
        i = 0
        print u'正在下载第%d页内容，请等待......\n' % page
        from progressbar import ProgressBar
        pbar = ProgressBar(maxval=len(photos)).start()
        for photo in photos:
            pbar.update(i)
            jpgurl = photo.attrib['src']
            self.__download_jpg(jpgurl, '%s/%d_%d.jpg' % (self.tienum, page, i))
            i += 1
        pbar.finish()

    def __mkdirfile(self, path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path, True)
        os.makedirs(path)

    def __download_jpg(self, src, path):
        """
        图片下载函数
        :param src:
        :param path:
        :return:
        """
        try:
            urllib.urlretrieve(src, path)
        except Exception as e:
            print e
            print u"下载图片失败!"

    def getnum(self):
        """
        获取楼主发表的页面数
        :return:
        """
        num = self.soup.xpath('.//*[@id="thread_theme_5"]/div[1]/ul/li[2]/span[2]')
        return num[0].text

    def get_title(self):
        """
        获取帖子标题
        :return:
        """
        title = self.soup.xpath('.//html/head/title')
        return title[0].text

    def get_author(self):
        """
        获取帖子作者
        :return:
        """
        title = re.findall('author: "(.*?)"', self.text)
        return title[0]

    def get_reply_num(self):
        """
        获取帖子总回复数
        :return:
        """
        reply_num = re.findall('reply_num:([0-9]*),', self.text)
        return reply_num[0]

    def get_url(self):
        return self.url

    @is_login
    def reply(self, response):
        """
        回复本贴,只支持文本格式的内容
        :param response:
        :return:
        """
        url = "http://tieba.baidu.com/p/" + str(self.tienum) + "/submit"
        msg = self.__get_msg_reply(url)
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
                "mouse_pwd": "23,21,16,15,18,20,23,27,42,18,15,19,15,18,15,19,15,18,15,19,15,18,15,19,15,18,15,19,42,18,16,22,26,19,42,18,26,17,19,15,18,19,27,19," + str(
                    int(time.time() * 10000)),
                "mouse_pwd_t": msg["mouse_pwd_t"],
                "mouse_pwd_isclick": 0,
                "__type__": "reply"
                }
        postdata = urllib.urlencode(data)
        headers = HEADER
        headers['Referer'] = url
        r = requests.post(url=URL_BAIDU_REPLY, data=postdata, headers=headers, verify=False)
        if int(r.status_code) == 200:
            return True
        else:
            print(u"回复评论失败！请登录后重试或联系作者修改")

    def __get_msg_reply(self, url):
        """
        获取post数据所需要的各种参数，通过游览器查看得出
        唯一有疑问的是mouse_pwd这个参数，在我电脑上实验这个参数可以顺利评论帖子
        如出现不能post可根据你游览器截获到的参数修改
        :param url:
        :return:
        """
        dictory = {}
        text = requests.get(url=url, allow_redirects=False, verify=False).content
        text2 = requests.get(url="http://tieba.baidu.com/f/user/sign_list?t=" + str(int(time.time() * 10000)),
                             allow_redirects=False, verify=False).content
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

    def __collection_templates(self, post_url):
        """
        收藏本贴
        :return:
        """
        tid = self.tienum
        url = MAIN_URL + "p/" + str(self.tienum)
        t = requests.get(url=url, allow_redirects=False, verify=False).content
        tbs = re.findall("'tbs':'([\w]*)'", t)[0]
        data = {
            'tid': tid,
            'type': 0,
            'datatype': 'json',
            'ie': 'utf-8',
            'tbs': tbs,
        }
        postdata = urllib.urlencode(data)
        headers = HEADER
        headers['Referer'] = url
        headers['Content-Length'] = len(postdata)
        r = requests.post(url=post_url, data=postdata, headers=headers, verify=False)
        return int(r.status_code)

    @is_login
    def collection(self):
        """
        收藏本帖
        :return: True or False
        """
        status = self.__collection_templates(URL_BAIDU_COLLECTION)
        if status == 200:
            return True
        else:
            print(u"收藏失败,请登录后重试或者联系作者")
            return False

    @is_login
    def uncollection(self):
        """
        取消收藏本帖
        :return: True or False
        """
        status = self.__collection_templates(URL_BAIDU_USER_UNFOLLOW)
        if status == 200:
            return True
        else:
            print(u"取消收藏失败,请登录后重试或者联系作者")
            return False

    def set_tiezi(self, num):
        """
        修改需要操作的贴吧
        :param num: 帖子号
        :return: None
        """
        self.url = MAIN_URL + "p/" + str(num) + "?see_lz=1&pn="
        req = requests.get(self.url + '1', headers=HEADERS, allow_redirects=False, verify=False)
        if int(req.status_code) != 200:
            raise TieziError, u'输入的帖子错误或者已经被删除'
        self.text = req.content
        self.soup = soupparser.fromstring(self.text)
        self.tienum = num


class Tieba(object):
    """贴吧操作类.
    对于js生成的贴吧，将会调用casperjs来得到html信息，然后通过lxml解析。
    对于需要登录才能操作的方法，需要提供用户名密码或者有cookie文件。
    """

    def __init__(self, name):
        self.set_tieba(name)

    def get_follownum(self):
        """
        获取总关注数
        :return:
        """
        try:
            num = self.soup.xpath('.//*[@class="card_menNum"]')
            return num[0].text
        except:
            num = re.findall("'memberNumber': '([0-9]*)'", self.html)
            return num[0]

    def get_tienum(self):
        """
        获取总的帖子数
        :return:
        """
        try:
            num = self.soup.xpath('.//*[@class="card_infoNum"]')
            return num[0].text
        except:
            num = re.findall('class="red_text">([0-9]*)</span>', self.html)
            return num[0]

    def get_catalog(self):
        """
        获取贴吧标签目录
        :return:list
        """
        try:
            catalogs = self.soup.xpath('.//*[@class="card_info"]/ul/li/a')
            return [i.text for i in catalogs]
        except:
            return u"此帖吧为js动态生成，暂不支持"

    def get_ties(self):
        """
        返回一个生成器，内容是本贴吧首页的帖子的类
        for循环时可以直接调用Tiezi里面类的函数，如：
        ties = Tieba('angela').get_ties()
        for tie in ties:
            print tie.get_title()
        :return:
        """
        x = self.soup.xpath('.//*[@id="thread_list"]/li')
        if not x:
            # raise TiebaError, u"此帖吧为js动态生成，暂不支持此函数"
            self.set_html_by_js()
            x = self.soup.xpath('.//*[@id="thread_list"]/li')
        ids = []
        for i in x:
            try:
                d = json.loads(i.attrib['data-field'])
                # del d['vid']
                # del d['is_good']
                # del d['is_top']
                # del d['is_protal']
                # del d['is_bakan']
                ids.append(d['id'])
            except:
                pass
        for i in ids:
            yield Tiezi(i)

    @is_login
    def sign_all(self):
        """
        一键签到
        :return:
        """
        url = "http://tieba.baidu.com/home/main?un=" + self.name + "&fr=ibaidu&ie=utf-8"
        t = requests.get(url=url, allow_redirects=False, verify=False).content
        tbs = re.findall("'tbs':'([\w]*)'", t)[0]
        date = {
            'ie': 'utf-8',
            'tbs': tbs,
        }
        postdata = urllib.urlencode(date)
        headers = HEADER
        headers['Referer'] = 'http://tieba.baidu.com/'
        headers['Content-Length'] = len(postdata)
        r = requests.post(url=URL_BAIDU_SIGN_ALL, data=postdata, headers=headers, verify=False)
        if int(r.status_code) == 200:
            return True
        else:
            print u"一键签到失败,登录后重试或者联系作者!"
            return False

    @is_login
    def sign(self):
        """
        签到函数
        20151217通过测试
        :return:
        """
        if self.__issign(self.url):
            return True
        try:
            tbs = re.findall("'tbs':'([\w]*)'", self.html)[0]
        except:
            tbs = re.findall(''''tbs': "([\w]*)"''', self.html)[0]
        data = {'ie': 'utf-8',
                'kw': self.name,
                'tbs': tbs,
                }
        postdata = urllib.urlencode(data)
        headers = HEADER
        headers['Referer'] = self.url
        headers['Cache-Control'] = 'no-cache'
        r = requests.post(url=URL_BAIDU_SIGN, data=postdata, headers=headers, verify=False)
        if int(r.status_code) == 200:
            return True
        else:
            return False

    def __issign(self, url):
        content = requests.get(url=url, allow_redirects=False, verify=False).content
        if re.findall('class="sign_keep_span"', content):
            return True
        else:
            return False

    @is_login
    def follow(self):
        """
        关注函数
        还在测试
        :return:
        """
        # todo(@fcfangcc):未来添加
        pass

    @is_login
    def remove_follow(self):
        """
        取消关注函数
        还在测试
        :return:
        """
        # todo(@fcfangcc):未来添加
        pass

    @is_login
    def thread(self, title, content):
        """
        发帖函数,暂时只支持纯文本内容
        20151217通过测试
        :param title: 标题
        :param content: 内容
        :return:
        """
        msg = self.__get_msg_tieba(self.url)
        data = {'ie': 'utf-8',
                'kw': self.name,
                'fid': msg['fid'],
                "tid": 0,
                "vcode_md5": "",
                "floor_num": 0,
                "rich_text": 1,
                "tbs": msg['tbs'],
                "content": content,
                "title": title,
                "prefix": "",
                "files": "[]",
                "mouse_pwd": "1,15,10,22,15,1,1,1,0,15,15,1,10,1,14,0,15,20,0,12,10,8,22,15,9,1,15,10,14,13,14,10,13,49,9,20,8,20,9,20,8,20,9,20,8,20,9,20,8,20,9,20,8,49,9,8,10,11,10,10,49,9,13,11,14,20,0,14,12," + str(
                    int(time.time() * 10000)),
                "mouse_pwd_t": msg["mouse_pwd_t"],
                "mouse_pwd_isclick": 0,
                "__type__": "thread"
                }
        postdata = urllib.urlencode(data)
        headers = HEADER
        headers['Referer'] = self.url
        headers['Accept-Language'] = 'zh-CN'
        headers['Host'] = 'tieba.baidu.com'
        headers['Content-Length'] = len(postdata)
        headers['X-Requested-With'] = 'XMLHttpRequest'
        r = requests.post(url=URL_BAIDU_THREAD, data=postdata, headers=headers, verify=False)
        if int(r.status_code) == 200:
            print u"发帖成功"
            # todo:未来增加返回新发的贴的地址功能
            return True
        else:
            print u"发帖失败"
            return False

    def __get_msg_tieba(self, url):
        dictory = {}
        html = requests.get(url=url, allow_redirects=False, verify=False).content
        try:
            dictory['tbs'] = re.findall("'tbs':'([\w]*)'", html)[0]
        except:
            dictory['tbs'] = re.findall(''''tbs': "([\w]*)"''', html)[0]
        dictory['fid'] = re.findall('"forum_id":([0-9]*),', html)[0]
        dictory["mouse_pwd_t"] = int(time.time()) * 1000
        return dictory

    def __exist(self):
        """
        判断贴吧是否存在
        :return:
        """
        if re.findall('class="sign_today_date">', self.html):
            return True
        else:
            return False

    def save_html(self, path=''):
        """
        保存贴吧首页的html文件
        :param path:
        :return:
        """
        path = "%s.html" % self.name if path else path + "%s.html" % self.name
        with open(path, 'w') as f:
            f.write(self.html)
        print "html save succeed!"

    def get_html(self):
        """
        返回贴吧首页的html内容。
        如果是js生成的，建议先执行set_html_by_js()之后在获取，可以得到正确的html
        :return:
        """
        return self.html

    def get_tieba_url(self):
        """
        获取贴吧首页url
        :return: url
        """
        return self.url

    def get_tieba_html(self):
        """
        获取贴吧html代码
        :return: html
        """
        return self.html

    def set_html_by_js(self):
        """
        利用casperjs来加载贴吧首页，并获得解析之后的HTML内容
        :return:
        """
        print(u"正在启用casperjs和phantomjs进行解析,请等待......")
        try:
            from jshtml.jshtml import Js_Html
        except Exception:
            print(u"请下载程序中的jshtml文件夹的内容，否则无法使用TieBa类")
        self.html = Js_Html().get_html(self.url)
        self.soup = soupparser.fromstring(self.html)

    def set_tieba(self, name):
        """
        修改正在操作的贴吧名字
        :param name: 贴吧名
        :return:
        """
        self.name = name
        url_items = [MAIN_URL, "f?kw=", name, "&fr=home"]
        self.url = ''.join(url_items)
        req = requests.get(self.url, headers=HEADERS, allow_redirects=False, verify=False)

        if int(req.status_code) != 200:
            raise TiebaError, 'The tieba: "%s" have not exist!' % self.name

        self.html = req.content
        try:
            self.soup = soupparser.fromstring(self.html)
        except ValueError:
            self.set_html_by_js()

# if __name__ == '__main__':
#     a = User("黑曼巴来了92")
#     a.follow()
