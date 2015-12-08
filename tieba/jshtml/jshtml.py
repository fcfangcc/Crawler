#-*- coding: UTF-8 -*-
__author__ = 'fangc'
import os
class Js_Html(object):

    def system_type(self):
        type = os.name
        if type == 'nt':
            return 'windows'
        elif type == 'posix':
            return 'unix'
        else:
            return 'unknow'

    def __set_env(self, path):
        casperjspath = os.path.join(path, 'casperjs\\bin')
        phantomjspath = os.path.join(path, 'phantomjs\\bin')
        system_env = os.getenv('Path')
        os.environ['Path'] = system_env +';'+casperjspath+';'+phantomjspath

    def get_html(self, url):
        mydir = os.path.split(os.path.realpath(__file__))[0]
        templatedir = os.path.join(mydir, 'template.js')
        jsdir = os.path.join(mydir, 'sample.js')

        with open(templatedir, 'r+') as f:
            text = f.readlines()
        text[11] = "var url = '%s';" % url

        with open(jsdir, 'w+') as f:
            f.writelines(text)

        if self.system_type() == 'windows':
            self.__set_env(mydir)
            commend = "casperjs %s" % jsdir
        else:
            # todo:待以后测试linux环境下问题。
            commend = "source /etc/profile && casperjs %s" % jsdir
        # print commend
        result = os.popen(commend)
        return result.read()


# print Js_Html().get_html("http://www.baidu.com")

# with open('E:\\coding\\1.html', 'r') as f:
#     text = f.read()
#
# soup = soupparser.fromstring(text)
# s = soup.xpath('.//*[@id="thread_list"]/li')
# for i in s:
#     try:
#         d = json.loads(i.attrib['data-field'])
#         print d['id']
#     except:
#         pass
