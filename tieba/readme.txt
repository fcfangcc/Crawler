tieba.py使用方法:

from tieba.py import User, Tiezi

查看用户信息(如果查看用户开放权限):

username = 'pei坏'

#如果有中文，在winodws的命令行下会报错，建议使用IDE或者linux环境

user = User(username)

age = user.get_age() //获取贴吧注册时间

followba = user.get_followBA() //获取关注的贴吧以及等级，返回字典类型

#{u'\u6d59\u6c5f\u5de5\u5546\u5927\u5b66': 'lv11', u'\u5206\u624b': 'lv11', u'\u8bdb\u4ed9': 'lv11', 'lol': 'lv11'}

ifollow = user.get_ifollow(type=type) //获取我关注的用户,这里type有三个可选参数：all,num,users

#默认type为all，返回类型为列表类型:('我关注的人数',{"关注者ID":"关注者主页地址"})

#如果选择num类型，返回INT类型为我关注的人数;users类型返回用户的字典{"关注者ID":"关注者主页地址"}

followme = user.followme(type=type) //获取关注我的用户,参数类型和上面一样

recently_tie = user.get_recently_tie(num=10) //获取最近回复的帖子10个

#返回类型为字典:{"编号":{回复内容相关信息的字典}}

下载某个帖子的内容:

tiezi = Tiezi("帖子的编号") //如3926556029

pagenum = tiezi.getnum() //获取楼主的页数

tiezi.downloadLZ(type=type,start=1,end=5) //下载帖子从start页到end页的内容

#type有两种类型:txt,photo

#如果选择txt,将楼主发表的帖子的文本内容下载到一个txt文件中以供阅读(适用于连载的那些)

#如果选择photo,将楼发表的帖子的图片下载到文件夹中


20151119新增回复帖子功能:
使用方法:
from login import Login

login = Login(USERNAME,PASSWORD)

login.login()

login.reply("回复的内容","帖子编号")

#如回复http://tieba.baidu.com/p/4168056569，只需要输入4168056569.
#可以使用这个脚本来刷某个贴吧的经验= =