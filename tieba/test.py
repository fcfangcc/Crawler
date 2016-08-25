#!/usr/bin/python
# coding:utf-8
"""
签到指定贴吧
"""
from tieba import Tieba

tbs = ["魔兽世界", "法师", "炉石传说", "lol", "杭州","圣骑士"]
for tb in tbs:
    tieba = Tieba(tb)
    if tieba.sign():
        print("[{0}]签到成功!".format(tb))
    else:
        print("[{0}]签到失败!".format(tb))