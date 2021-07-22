import requests
from bs4 import BeautifulSoup
import json, os, sys, time, random, csv, hashlib
from itertools import islice
from threading import Thread
from BackEnd.Spyder.SpyderFrame import *
from BackEnd.Spyder.DBFrame import *

'''
    user.py -> tables:User, Answer
    
    1.更新待爬取userToken列表
        1.1.载入本地待爬取列表，locallist = load_token()
        1.2.查询数据库存在用户列表，existlist = [tuple(token)[0] for token in session.query(User.urlToken).all()]
        1.3.生成待爬取列表，needlist = list(set(locallist)-set(existlist))
        # 实际情况待定
    2.列表不空时进行爬虫
        2.1.爬取一个人信息
        2.2.爬取一个人的关注列表,并加入待爬取userToken列表
        2.3.异常处理 
            del_exception('user',step=1,)
            update_token(needlist)
        
'''


class userSpider(Spyder, DBIF):
    '''
    用户爬虫 -> table: User, Question, Answer
    ：param cookie: 登录信息
    '''

    def __init__(self, cookie: str):
        super(userSpider, self).__init__("comment")
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

    def get_user(self, token):
        '''
        爬取指定用户页面，获取用户数据，携带6条回答数据
        -> data table: User, Question, Answer
        :param token: 用户url请求必须字段
        '''
        url = f'https://www.zhihu.com/people/{token}'
        code = 200  # 请求接收器
        try:
            # GET请求
            html = self.s.request(method='GET',
                                  url=url,
                                  headers=super().random_Agent(),
                                  proxies=super().random_proxy(),
                                  allow_redirects=False)
            code = html.status_code
            html.raise_for_status()  # 检查请求异常
            # 用户信息json数据位置
            soup = BeautifulSoup(html.text, 'lxml')
            po1 = soup.find('script', attrs={'id': 'js-initialData'}).contents  # find it
            po1 = json.loads(po1[0])  # str->json
            # 提取json, 找到数据位置
            user = po1["initialState"]["entities"]["users"][token]  # 用户数据
            questions = po1["initialState"]["entities"]["questions"]  # 提问数据列表
            answers = po1["initialState"]["entities"]["answers"]  # 回答数据列表
            # 保存到数据库
            self.update(User(user))  # -> table: User
            for question in questions.values():
                self.add(Question(question))  # -> table: Question
            for answer in answers.values():
                self.add(Answer(answer))  # -> table: Answer
        except Exception as e:
            print(e)
            del_exception("user", setp=1, id=token, code=code, description=e.__str__())

    def get_user_followers(self, usertoken, offset):
        url = 'https://www.zhihu.com/api/v4/members/newson-74/followees'
        code = 200  # 请求接收器
        param = {
            'include': 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics',
            'offset': str(offset),
            'limit': '20',
        }

        try:
            # GET请求
            html = self.s.request(method='GET',
                                  url=url,
                                  params=param,
                                  headers=super().random_Agent(),
                                  proxies=super().random_proxy(),
                                  allow_redirects=False)
            code = html.status_code
            print(code)
            html.raise_for_status()  # 检查请求异常
            soup = BeautifulSoup(html.text, 'lxml')

        except Exception as e:
            print(e)

    def get_user_followees(self, usertoken, offset):
        '''
        知乎v4 API 缺少身份验证
        '''
        url = 'https://www.zhihu.com/api/v4/members/newson-74/followees'
        code = 200  # 请求接收器
        param = {
            'include': 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics',
            'offset': str(offset),
            'limit': '20',
        }

        try:
            # GET请求
            html = self.s.request(method='GET',
                                  url=url,
                                  params=param,
                                  headers=super().random_Agent(),
                                  proxies=super().random_proxy(),
                                  allow_redirects=False)
            code = html.status_code
            print(code)
            html.raise_for_status()  # 检查请求异常
            soup = BeautifulSoup(html.text, 'lxml')

        except Exception as e:
            print(e)

    def updatelist(self, oldlist=[]):
        '''
        更新爬虫缓冲区
        从本地异常进度保存文件，以及服务器数据库Question, Answer, Comment, Hot表，更新待爬取的qid列表
        :param oldlist: 现存缓冲区
        :return 爬虫缓冲区->qid
        '''
        local = load_retry('user', 1) + load_token()  # 本地保存进度
        session = self.DbSession()
        exist = [i.urlToken for i in session.query(User.urlToken).all()]
        need = list(set(local)-set(exist))
        return need

    def start(self):
        '''
        启动爬虫
        更新缓冲区，爬取用户数据
        '''
        needlist = self.updatelist()
        signal = 0  # 爬虫休息信号
        while len(needlist):
            token = needlist.pop(0)
            if token:
                signal += 1
                self.get_user(token)
                if signal != 0 and signal % 5000 == 0:  # 每请求5k个问题，随机休眠一个长时间段
                    needlist = self.updatelist()
                    print(f"剩余{len(needlist)}个问题，进入长时间段休息......")
                    time.sleep(random.choice([600, 900, 1200, random.randint(300, 1200)]))  # 10分钟-20分钟
                    print("休息结束。")
                time.sleep(random.choice([0.5, 1, 3, random.randint(1, 5)]))  # 每个话题页面请求间隔一个短时间段，500ms-5s


if __name__ == "__main__":
    us = userSpider(None)
    # us.get_user('hesenbao') # 测试
    us.start()
