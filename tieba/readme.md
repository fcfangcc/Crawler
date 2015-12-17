## tieba.py使用方法:
##### 如需使用登录操作，目前仅支持用百度用户名密码登录,手机用户暂不支持!

参考的[zhihu-python](https://github.com/egrcc/zhihu-python/blob/master/auth.py)里面的登录函数进行了修改(现已支持输入验证码)

    #如果有中文，在winodws的命令行下会报错，建议使用IDE或者linux环境
    #查看用户信息(如果查看用户开放权限):
    from tieba.py import User, Tiezi
    username = 'pei坏'
    user = User(username)
    #获取贴吧注册时间
    age = user.get_age()
获取关注的贴吧以及等级，返回字典类型
{u'\u6d59\u6c5f\u5de5\u5546\u5927\u5b66': 'lv11', u'\u5206\u624b': 'lv11', u'\u8bdb\u4ed9': 'lv11', 'lol': 'lv11'}

    followba = user.get_followBA()

get_ifollow,获取我关注的用户,这里type有三个可选参数：all,num,users.

默认type为all，返回类型为列表类型:('我关注的人数',{"关注者ID":"关注者主页地址"})

如果选择num类型，返回INT类型为我关注的人数;users类型返回用户的字典{"关注者ID":"关注者主页地址"}

    ifollow = user.get_ifollow(type=type)
    followme = user.followme(type=type)
    #获取关注我的用户,参数类型和get_ifollow一样
    recently_tie = user.get_recently_tie(num=10)
    #获取最近回复的帖子10个
    #返回类型为字典:{"编号":{回复内容相关信息的字典}}

下载某个帖子的内容,如3926556029:

    tiezi = Tiezi("帖子的编号")
    #获取楼主的页数
    pagenum = tiezi.getnum()
    tiezi.downloadLZ(type=type,start=1,end=5)

下载帖子从start页到end页的内容.

type有两种类型:txt,photo.

如果选择txt,将楼主发表的帖子的文本内容下载到一个txt文件中以供阅读(适用于连载的那些).

如果选择photo,将楼发表的帖子的图片下载到文件夹中.


## 20151119新增回复帖子功能:

使用方法:

    from login import Login
    login = Login(USERNAME,PASSWORD)
    login.login()
    login.reply("回复的内容","帖子编号")
    #如回复http://tieba.baidu.com/p/4168056569，只需要输入4168056569.
    #可以使用这个脚本来刷某个贴吧的经验= =

## 20151130日更新:

发现有的贴吧首页变成了js动态生成，所以之前有的很多函数不能正常使用。

现在貌似百度在某些贴吧测试，估计后面贴吧也会变成js动态生成。

主要增加内容：贴吧签到,贴吧发表新帖,贴吧一键签到

    from tieba import Tieba
    #如:Tieba("杭州","admin","123456")
    tieba = Tieba(name, username,password)
    
    #签到
    tieba.sign()
    #一键签到
    tieba.sign_all()
    
    #发帖测试:tieba.thread("测试","hello,word")
    tieba.thread(title, content)
    
    #获取贴吧首页的帖子,返回一个Tiezi类的生成器
    ties = tieba.get_ties()
    for tie in ties:
        #输出帖子的标题,Tiezi类里面的函数都可以使用
        pirnt tie.get_title()

其它一些简单的关于贴吧基本信息获取函数.

关注和取消关注，还在测试中.

#### 增加了对js生成的贴吧首页的支持:TieBa().set_html_by_js()函数

主要利用了casperjs将加载完的html内容返回给python,然后利用xpath做解析。

我将[casperjs](http://docs.casperjs.org/en/latest/index.html)和[phantomjs](http://phantomjs.org/)打包在了程序里面，windows环境下下载整个tieba文件夹即可使用。

如需要在linux下使用，安装完casperjs和phantomjs之后，将他们的(path)/bin加入到/etc/profile里面的path环境变量中，应该就可以使用.
