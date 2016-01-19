# tieba.py使用方法:
### 注意:所有方法如果正确执行默认返回True，不会提示成功执行.如果出错返回False同时会有信息输出.
##### 如需使用登录操作，目前仅支持用百度用户名密码登录,手机用户暂不支持!
##### python2.7.10，windows下Pycharm和centos6.7下测试通过，其它平台不确定.(<font color=red>切勿使用windows命令行调用类</font>，在utf-8文件里调用可以)
##### 增加了对js生成的贴吧首页的支持:Tieba().set_html_by_js()函数

主要利用了casperjs将加载完的html内容返回给python,然后利用xpath做解析。

我将[casperjs](http://docs.casperjs.org/en/latest/index.html)和[phantomjs](http://phantomjs.org/)打包在了程序里面，windows环境下下载整个tieba文件夹即可正常使用。

如需要在linux下<font color=red>完美使用</font>，安装完casperjs和phantomjs之后，将他们的(path)/bin<font color=red>加入到/etc/profile里面的path环境变量</font>中，就可以正常使用.

参考的[zhihu-python](https://github.com/egrcc/zhihu-python/blob/master/auth.py)里面的登录函数进行了修改(<font color=red>现已支持手动输入验证码</font>,cookie功能还有问题)

## User类使用方法:

    #如果有中文，在winodws的命令行下会报错，建议使用IDE或者linux环境
    #查看用户信息(如果查看用户开放权限):
    from tieba.py import User, Tiezi
    user = USERNAME
    user = User(user)
    #获取贴吧注册时间（获取其它基本信息函数类似）
    age = user.get_age()
获取关注的贴吧以及等级，返回字典类型{u'\u6d59\u6c5f\u5de5\u5546\u5927\u5b66': 'lv11', u'\u5206\u624b': 'lv11', u'\u8bdb\u4ed9': 'lv11', 'lol': 'lv11'}

    followba = user.get_followba()

get_ifollow,获取我关注的用户,这里type有三个可选参数：all,num,users.

默认type为all，返回类型为列表类型:('我关注的人数',{"关注者ID":"关注者主页地址"})

如果选择num类型，返回INT类型为我关注的人数;users类型返回用户的字典{"关注者ID":"关注者主页地址"}

    ifollow = user.get_ifollow(type=type)
    followme = user.followme(type=type)
    #获取关注我的用户,参数类型和get_ifollow一样
    recently_tie = user.get_recently_tie(num=10)
    #获取最近回复的帖子10个
    #返回类型为字典:{"编号":{回复内容相关信息的字典}}



###### 下面是需要登录的对用户操作:

如现在需要关注/取消关注用户"精英彩虹",操作之后继续关注"pei坏"用户.
    
    user = User("精英彩虹",username=username,password=password)
    user.follow()
    user.unfollow()
    #切换操作对象
    user.set_user('pei坏')
    user.follow()
    #继续进行需要的操作,这样只需要登录一次即可，避免了多次输入验证码

## Tiezi类使用方法:

下载某个帖子的内容,如3926556029:

    from tieba import Tiezi
    tiezi = Tiezi("3926556029")
    #获取楼主的页数(获取其它基本信息类似)
    pagenum = tiezi.getnum()
    
    tiezi.downloadlz(type=type,start=1,end=5)
    #下载帖子从start页到end页的内容.
    #type有两种类型:txt,photo.
    #如果选择txt,将楼主发表的帖子的文本内容下载到一个txt文件中以供阅读(适用于连载的那些).
    #如果选择photo,将楼发表的帖子的图片下载到文件夹中.


###### 下面是需要登录的操作本贴方法:

    tiezi = Tiezi('帖子号码',username=username,password=password)
    tiezi.reply("回复的内容，目前只支持纯文本内容")
    #可以使用这个脚本来刷某个贴吧的经验= =
    #收藏和取消收藏
    tiezi.collection()
    tiezi.uncollection()
    tiezi.set_tiezi('帖子号码')
如果需要回复url信息,请看[issues2](https://github.com/fcfangcc/Crawler/issues/2) 

## Tieba类使用方法:

发现有的贴吧首页变成了js动态生成，添加了对js生成网页的支持。

主要增加内容：贴吧签到,贴吧发表新帖,贴吧一键签到.

其中获取贴吧基本信息的函数和Tiezi,User类基本相同(并且不需要登录),不做介绍.

    from tieba import Tieba
    #如:Tieba("杭州",username="admin",password="123456")
    tieba = Tieba(name, username=username,password=password)
    
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

    #更换贴吧
    tieba.set_tieba("贴吧名字")


关注和取消关注，还在测试中.


