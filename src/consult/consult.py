import requests
from bs4 import BeautifulSoup
import json, os, sys, time, random, csv, hashlib
from itertools import islice
from threading import Thread
from BackEnd.Spyder.SpyderFrame import *
from BackEnd.Spyder.DBFrame import *

'''
    consult.py -> tables: 

    1.爬取付费咨询话题列表
    2.爬取付费咨询的热门答主信息
    3.爬取付费咨询的最新答主信息
    4.爬取每个咨询话题下的答主信息
    

'''


class consultSpyder(Spyder, DBIF):
    '''
    付费咨询爬虫 -> table:
    ：param cookie: 登录信息
    '''

    def __init__(self, cookie: str):
        super(consultSpyder, self).__init__("comment")
        DBIF.__init__(self, username='HXL', passwd="123456")
        if cookie:
            self.cookie = {
                i.split("=")[0]: i.split("=")[-1]
                for i in cookie.split("; ")
            }
        else:
            self.cookie = None
        self.s = requests.Session()  # 准备https会话
        self.s.keep_alive = True

    def get_topic(self):
        '''
        知乎v4 API 缺少身份验证
        '''
        url = 'https://www.zhihu.com/api/v4/infinity/topics'
        data = {
            "limit": 20
        }
        code = 200
        try:
            # GET请求
            data = self.s.request(method='GET', url=url, params=data, headers=self.random_Agent(),
                                  proxies=self.random_proxy())
            data.raise_for_status()
            code = data.status_code
        except Exception as e:
            print(e)
            del_exception('consult', step=1, code=code, description=e.__str__())
        print(data.content)

    def get_hot_responser(self):
        pass

    def get_new_responser(self):
        pass

    def get_topic_responser(self, id):
        pass

    def updatelist(self, oldlist=[]):
        '''
        更新爬虫缓冲区
        从本地异常进度保存文件，以及服务器数据库Question, Answer, Comment, Hot表，更新待爬取的qid列表
        :param oldlist: 现存缓冲区
        :return 爬虫缓冲区->qid
        '''
        local = load_retry('user', 1) + load_token()  # 本地保存的因为异常需要重新爬取的问题id列表
        need = local
        return need

    def start(self):
        '''
        启动爬虫
        更新缓冲区，爬取用户数据
        '''
        needlist = self.updatelist()
        signal = 0  # 爬虫休息信号
        while len(needlist):
            id = needlist.pop(0)
            if id:
                signal += 1
                self.get_topic_responser(id)
                if signal != 0 and signal % 5000 == 0:  # 每请求5k个问题，随机休眠一个长时间段
                    needlist = self.updatelist()
                    print(f"剩余{len(needlist)}个问题，进入长时间段休息......")
                    time.sleep(random.choice([600, 900, 1200, random.randint(300, 1200)]))  # 10分钟-20分钟
                    print("休息结束。")
                time.sleep(random.choice([0.5, 1, 3, random.randint(1, 5)]))  # 每个话题页面请求间隔一个短时间段，500ms-5s


cs = consultSpyder(None)
# cs.get_topic()
cs.update(RealForSpark({"keyWord":'1', "weightValue":9.9}))
