# -*- coding: UTF-8 -*-
__author__ = 'fangc'
import os
import sys


class Js_Html(object):
    def system_type(self):
        type = os.name
        if type == 'nt':
            return 'windows'
        elif type == 'posix':
            return 'unix'
        else:
            return 'unknow'

    def get_html(self, url):
        mydir = os.path.split(os.path.realpath(__file__))[0]
        templatedir = os.path.join(mydir, 'template.js')
        jsdir = os.path.join(mydir, 'sample.js')

        with open(templatedir, 'r+') as f:
            text = f.readlines()
        text[11] = "var url = '%s';" % url

        with open(jsdir, 'w+') as f:
            f.writelines(text)
        # 设置casperjs和phantomjs的环境变量
        if self.system_type() == 'windows':
            casperjspath = os.path.join(mydir, 'casperjs\\bin')
            phantomjspath = os.path.join(mydir, 'phantomjs\\bin')
            system_env = os.getenv('Path')
            os.environ['Path'] = system_env + ';' + casperjspath + ';' + phantomjspath
            commend = "casperjs %s" % jsdir
        else:
            casperjspath = os.path.join(mydir, 'casperjs/bin')
            phantomjspath = os.path.join(mydir, 'phantomjs/bin')
            os.environ["PATH"] += ":{0}:{1}".format(casperjspath, phantomjspath)
            commend = "source /etc/profile && casperjs %s" % jsdir
        result = os.popen(commend).read()
        if not result:
            print("casperjs和phantomjs权限错误或者环境变量错误!\n请执行以下语句:")
            print("chmod +x {0}").format(casperjspath + "/casperjs")
            print("chmod +x {0}").format(phantomjspath + "/phantomjs")
            sys.exit()
        return result

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
