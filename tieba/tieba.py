#-*- coding: UTF-8 -*-
from lxml import etree
from lxml.html import soupparser
import urllib2
import urllib
from urlparse import urljoin
import requests
import sys
import os
import shutil
import time

HEADERS = {'content-type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

MAIN_URL = "http://tieba.baidu.com/"

def user_main(name):
    name = name.decode('UTF-8').encode('gbk')
    url ="http://tieba.baidu.com/home/main?un="+repr(name)+"&fr=ihome"
    url = url.replace("\'", "").replace("\\x", "%")
    return url


class InputErrorStr(Exception):
    pass

class TieziError(Exception):
    pass

class UserError(Exception):
    pass


class User(object):
    def __init__(self, username):
        url = user_main(username)
        req = urllib2.Request(url, headers=HEADERS)
        try:
            resp = urllib2.urlopen(req)
        except urllib2.URLError:
            print u"打开个人网页失败!请检查网络"
            sys.exit()
        self.userHtml = etree.HTML(resp.read())
        if self.userHtml.find('.//title').text == u"贴吧404":
            print u"用户不存在,请确认"
            sys.exit()

    def get_followBa(self):
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
        age = self.userHtml.find('.//*[@id="userinfo_wrap"]/div[2]/div[3]/div/span[2]')
        return age.text

    def get_sex(self):
        sex = self.userHtml.find('.//*[@id="userinfo_wrap"]/div[2]/div[3]/div/span[1]')
        return sex.attrib['class']

    def get_followme(self,type='all'):
        """
        根据输入的type来返回对应的值：
        "all":{关注我的数量,{用户：主页地址...}}
        "num":关注我的数量
        "users":{用户：主页地址...}
        :param type:
        :return:
        """
        if self.userHtml.find('.//*[@id="container"]/div[2]/div[4]/h1/span'):
            followme_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[4]/h1/span')
        elif self.userHtml.find('.//*[@id="container"]/div[2]/div[3]/h1/span') is not None and self.userHtml.find('.//*[@id="container"]/div[2]/div[3]')[0].text in [u"关注他的人", u"关注她的人"]:
            followme_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[3]/h1/span')
        elif self.userHtml.find('.//*[@id="container"]/div[2]/div[2]/h1/span') is not None and self.userHtml.find('.//*[@id="container"]/div[2]/div[2]')[0].text in [u"关注他的人", u"关注她的人"]:
            followme_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[2]/h1/span')
        else:
            return u"没有人关注此用户"
        followmesurl = urljoin(MAIN_URL, followme_url.attrib['href'])
        soup = soupparser.fromstring(requests.get(followmesurl).content)
        page_next = soup.xpath('.//*[@class="next"]')
        names = soup.xpath('.//*[@id="search_list"]/div/div[2]/span[1]/a')
        if type == 'num':
            return followme_url.text
        else:
            usermsg = dict([(name.text, urljoin(MAIN_URL, name.attrib['href'])) for name in names])
            while page_next:
                url_next = urljoin(MAIN_URL, page_next[0].attrib['href'])
                soup_next = soupparser.fromstring(requests.get(url_next).content)
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
        if self.userHtml.find('.//*[@id="container"]/div[2]/div[3]/h1/span') is not None and self.userHtml.find('.//*[@id="container"]/div[2]/div[3]')[0].text in [u"他关注的人",u"她关注的人"]:
            ifollow_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[3]/h1/span')
        elif self.userHtml.find('.//*[@id="container"]/div[2]/div[2]/h1/span') is not None and self.userHtml.find('.//*[@id="container"]/div[2]/div[2]')[0].text in [u"他关注的人",u"她关注的人"]:
            ifollow_url, = self.userHtml.find('.//*[@id="container"]/div[2]/div[2]/h1/span')
        else:
            return u"此用户未关注任何人"
        ifollowurl = urljoin(MAIN_URL, ifollow_url.attrib['href'])
        soup = soupparser.fromstring(requests.get(ifollowurl).content)
        page_next = soup.xpath('.//*[@class="next"]')
        names = soup.xpath('.//*[@id="search_list"]/div/div[2]/span[1]/a')
        if type == 'num':
            return ifollow_url.text
        else:
            usermsg = dict([(name.text, urljoin(MAIN_URL, name.attrib['href'])) for name in names])
            while page_next:
                url_next = urljoin(MAIN_URL, page_next[0].attrib['href'])
                soup_next = soupparser.fromstring(requests.get(url_next).content)
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
        if self.userHtml.find('.//*[@id="container"]/div[1]/div/div[3]').text:
            return u"该用户已隐藏个人动态"
        times = self.userHtml.findall('.//*[@id="container"]/div[1]/div/div[3]/ul/div/div[1]')
        replys = self.userHtml.findall('.//*[@id="container"]/div[1]/div/div[3]/ul/div/div[3]/div[1]/div/')
        titles = self.userHtml.findall('.//*[@id="container"]/div[1]/div/div[3]/ul/div/div[3]/div[2]/a[1]')
        names = self.userHtml.findall('.//*[@id="container"]/div[1]/div/div[3]/ul/div/div[3]/div[2]/a[2]')
        num = len(replys) if num > len(replys) else num
        replydict = dict([(i, dict([('reply', replys[i].text), ('title', titles[i].text), ('name', names[i].text), ('time',times[i].text)])) for i in xrange(num)])
        return replydict


class Tiezi(object):
    def __init__(self, num):
        self.url = MAIN_URL + "p/" + num +"?see_lz=1&pn="
        self.soup = soupparser.fromstring(requests.get(self.url+'1', headers=HEADERS).content)
        if self._is404():
            raise TieziError, u'输入的帖子错误或者已经被删除'
        self.teinum = num

    def __del__(self):
        pass

    def downloadLZ(self, type='txt', start=1, end=5):
        """
        type:txt or photo
        默认下载前5页的内容
        :param n:
        :return:
        """
        self.__mkdirfile(self.teinum)
        num = int(self.getnum())
        print u'本帖子楼主共有%d页发表!' % num
        if start > end:
            print u"结束页超过起始页，请检查参数!\n"
            sys.exit()
        elif start > num:
            print u"起始页面超过上限!本帖子一共有 %d 页\n" % num
            sys.exit()
        num = num if num < end else end
        for i in xrange(start-1, num):
            soup = soupparser.fromstring(requests.get(self.url+str(i+1)).content)
            if type == "txt":
                self.__get_lz_txt(i+1, soup)
            elif type == "photo":
                self.__get_lz_jpg(i+1, soup)
            else:
                print u"输入的参数有误，只能输入'txt'或者'photo'"

    def __get_lz_txt(self, page, soup):
        print u'正在下载第 %d 页内容，请等待......\n' % page
        txts = soup.xpath('.//div[@class="d_post_content j_d_post_content "]/text()')
        if not txts:
            txts = soup.xpath('.//div[@class="d_post_content j_d_post_content  clearfix"]/text()')
        with open("%s/text.txt" % self.teinum, "a+") as f:
            f.writelines(''.join(txts).encode('utf8'))
        f.close()

    def __get_lz_jpg(self, page, soup):
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
            self.__download_jpg(jpgurl, '%s/%d_%d.jpg' % (self.teinum, page, i))
            i += 1
        pbar.finish()

    def __mkdirfile(self, path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path, True)
        os.makedirs(path)

    def __download_jpg(self, src, path):
        try:
            urllib.urlretrieve(src, path)
        except Exception as e:
            print e
            print u"下载图片失败!"

    def getnum(self):
        num = self.soup.xpath('.//*[@id="thread_theme_5"]/div[1]/ul/li[2]/span[2]')
        return num[0].text

    def _is404(self):
        if self.soup.xpath('.//*[@class="page404"]'):
            return True
        else:
            return False


if __name__ == '__main__':
    # name = ["pacin坑","尹大大与萧小小","pei坏"]
    # n = ["4079508183", "4045828597", "3926556029"]
    # c = Tiezi(n[0])
    # print c.getnum()
    pass

