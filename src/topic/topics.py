import requests
from bs4 import BeautifulSoup
import json, os, sys, time, random, csv, hashlib
from itertools import islice
from threading import Thread
from BackEnd.Spyder.SpyderFrame import *
from BackEnd.Spyder.DBFrame import *

'''
    topic.py -> tables:Topic_Class Topic Topic_raltion
    1.通过爬取知乎话题广场爬取所有话题
    2.通过话题爬取话题具体信息，话题关系信息，基础问题信息（不足构成表数据）
    
    文件最后是执行部分
'''

tempPath = r'./temp.json'
classPath = r'./class.json'  # 爬取话题辅助文件，自动生成


class topicSpyder(Spyder, DBIF):
    '''
    话题爬虫 -> data tables: Topic_Class, Class_Topics, Topic, Answer
              relation tables: Topic_Parents, Topic_Childen
    ：param cookie: 登录信息
    '''

    def __init__(self, cookie: str):
        super(topicSpyder, self).__init__('topic')
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

    def get_classTopic_support(self):
        '''
        获取话题类别，数据量不大 -> table: ClassTopic
        '''
        url = 'https://www.zhihu.com/topics'
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
            # 找到标签
            soup = BeautifulSoup(html.text, 'lxml')
            classlist = soup.findAll('li', attrs={'class': 'zm-topic-cat-item'})  # 话题类别标签
            # 提取数据
            data = []
            for oneclass in classlist:
                # 插入不完整数据，缺失topicsCount
                self.add(ClassTopic({"id": oneclass.get('data-id'), "name": oneclass.text}))
        except Exception as e:
            print(e)
            del_exception("topic", step='0', status_code=code, description=e.__str__())

    def get_classTopic(self, id: str, offset=0):
        '''
        爬取属类话题信息，携带20条话题从属关系数据 -> table: Topic_Class
        :param id: 属类话题id
        :param name: 属类话题名称
        :param offset: 查询偏移量
        '''

        url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
        payload = {
            'method':
                'next',
            'params':
                '{"topic_id":' + id + ',"offset":' + str(offset) + ',"hash_id":""}'
        }
        code = 200  # 请求接收器
        try:
            # POST请求
            data = self.s.request(method="POST",
                                  url=url,
                                  data=payload,
                                  headers=super().random_Agent(),
                                  proxies=super().random_proxy())
            code = data.status_code
            data.raise_for_status()  # 检查请求异常
            # 提取数据
            data = json.loads(data.text)  # to json
            # 返回不空，提取20条话题从属关系，存入数据库
            if data["msg"]:
                html = '\n'.join(data["msg"])
                soup = BeautifulSoup(html, 'lxml')
                topicslist = soup.findAll('div', attrs={'class': 'item'})
                for onetopic in topicslist:
                    # 向数据库话题属类关系表导入一条话题属类与话题的数据
                    topicid = onetopic.find('a', attrs={'target': '_blank'}).get('href').split(r'/')[-1]
                    self.add_relationship(Topic_Class({"categoryID": id, "topicID": topicid}))
                    offset += 1  # 记录进度
            if len(data["msg"]) == 20:
                self.get_topics_simple(id, offset)  # 递归查询后面20条
        except Exception as e:
            print(e)
            del_exception('topic', setp='1', id=id, offset=offset, status_code=code, description=e.__str__())

    def get_topic(self, id):
        '''
        1.获取一个话题的详细信息以及该话题下面的问题 -> table:Topic,Answer

        2.获取一个话题的详细信息以及该话题下面的问题 -> table:Topic_Parents, Topic_Childen

        :param id: 话题id
        '''

        url = 'https://www.zhihu.com/topic/' + id + '/hot'
        parenturl = 'https://www.zhihu.com/api/v3/topics/' + id + '/parent'
        childurl = 'https://www.zhihu.com/api/v3/topics/' + id + '/children'
        code = 200  # 请求接收器
        pcode = 200  # 请求接收器
        ccode = 200  # 请求接收器
        try:
            # GET请求
            html = self.s.request(method='GET',
                                  url=url,
                                  headers=super().random_Agent(),
                                  proxies=super().random_proxy(),
                                  allow_redirects=False)
            code = html.status_code
            html.raise_for_status()  # 检查请求异常
            if code == 302:  # topicid发生改变需要修改
                soup = BeautifulSoup(html.text, 'lxml')
                newid = soup.find('a').text.split('/')[-1]
                # 更新数据表 Topic_Class
                session = self.DbSession()
                # 找到旧topicID的所有数据主键,遍历更新
                idlist = [row.id for row in session.query(Topic_Class.id).filter(Topic_Class.topicID == id).all()]
                for i in idlist:
                    session.query(Topic_Class).filter(Topic_Class.id == i).update({"topicID": newid})
                    session.commit()
                session.close()
                self.get_topic(newid)  # 重新爬
                return
            parentdata = self.s.request(method='GET',
                                        url=parenturl,
                                        headers=super().random_Agent(),
                                        proxies=super().random_proxy(),
                                        allow_redirects=False)
            pcode = parentdata.status_code
            parentdata.raise_for_status()  # 检查请求异常
            childdata = self.s.request(method='GET',
                                       url=childurl,
                                       headers=super().random_Agent(),
                                       proxies=super().random_proxy(),
                                       allow_redirects=False)
            ccode = childdata.status_code
            childdata.raise_for_status()  # 检查请求异常
            # 1.
            # 找到标签
            soup = BeautifulSoup(html.text, 'lxml')
            classlist = soup.find('script', attrs={'id': 'js-initialData'})  # json数据所在标签
            classlist = json.loads(classlist.contents[0])
            # 提取数据
            answers = classlist["initialState"]["entities"]["answers"]  # 10条,list
            topic = classlist["initialState"]["entities"]["topics"][id]  # 1条,dict
            self.update(Topic(topic))
            print("add one topic to db.topic")
            for answer in answers.values():
                save_token(answer["author"]["urlToken"])  # 为爬取user提供更多前提userToken
                self.add(Answer(answer))
            print("add ten answer to db.answer")
            # 2.
            # 分析json
            parentdata = json.loads(parentdata.text)
            childdata = json.loads(childdata.text)
            for parent in parentdata["data"]:
                self.add_relationship(Topic_Parents({"topicID": id, "parentTopicID": parent["id"]}))
            print("add parents topic to db.topic&parents ")
            for child in childdata["data"]:
                self.add_relationship(Topic_Children({"topicID": id, "childTopidID": parent["id"]}))
            print("add childen topic to db.topic&children ")
        except Exception as e:
            print(e)
            del_exception('topic', setp='2', id=id, status_code=code, parentCode=pcode,
                          childCode=ccode, description=e.__str__())

    def updateclasslist(self):
        '''
        通过数据库更新待爬取话题类别缓冲区 (classid, offset)
        '''
        local = load_retry('topic', step=1)  # (classid, offset)
        # 数据库实际进度
        session = self.DbSession()
        # 假设所有属类话题待爬取, 本地属类话题信息，缺失offset, totals (classid, offset:0)
        need = [[row.id, 0] for row in session.query(ClassTopic).all()]
        # 实际爬取进度
        id_offset = [(row.categoryID, row.offset) for row in session.query(
            Topic_Class.categoryID, func.count(distinct(Topic_Class.topicID)).label('offset')).group_by(
            Topic_Class.categoryID).all()]  # (classid, offset)
        session.close()
        # 合并进度
        localid = [col[0] for col in local]
        offsetid = [col[0] for col in id_offset]
        for i in range(len(need)):
            id = need[i][0]  # 截取classid字段
            # 先合并本地进度
            if id in localid:
                need[i][-1] = local[localid.index(id)][-1]  # 修改offset字段
            # 再合并数据库计算进度
            if id in offsetid:
                need[i][-1] = id_offset[offsetid.index(id)][-1]  # 修改offset字段
        return need

    def step1(self):
        '''
        ----------step1:从话题广场爬取属类话题信息和属类话题和话题的从属关系
        '''
        session = self.DbSession()
        exist = session.query(ClassTopic).all()
        session.close()
        local = load_retry('topic', step=0)  # 本地请求异常信息记录
        # 因为爬一次就能爬取所有话题大类，所以数据库有数据并且本地异常记录中没有记录，就说明爬取过了
        if len(local) != 0 or len(exist) == 0:
            self.get_classTopic_support()
        need = self.updateclasslist()  # (classid, offset)
        while len(need):
            log = need.pop(0)  # (classid, offset)
            self.get_classTopic(log[0], log[1])
            time.sleep(random.choice([0.5, 1, 3, random.randint(1, 3)]))  # 每个话题页面请求间隔一个短时间段，500ms-3s

    def updatetopiclist(self, oldlist=[]):
        '''
        更新待爬取话题id缓冲区
        :param oldlist: 现存缓冲区
        '''
        session = self.DbSession()
        need = [row.topicID for row in session.query(Topic_Class.topicID).group_by(Topic_Class.topicID).all()]
        existqidlist = [id.id for id in session.query(Topic.id).all()]  # 数据库中的话题id列表
        session.close()
        retryidlist = load_retry('topic', 2)  # 需要从异常中重新爬取的话题id列表
        need = list((set(oldlist) | set(retryidlist) | set(need)) - set(existqidlist))
        return need

    def step2(self):
        '''
        ----------step3:获取话题详细信息--可以异常恢复进度
        '''
        needlist = self.updatetopiclist()
        signal = 0  # 爬虫休息信号
        while len(needlist):
            id = needlist.pop(0)
            signal += 1
            self.get_topic(id)
            if signal != 0 and signal % 5000 == 0:  # 每请求5k个问题，随机休眠一个长时间段
                print(f"剩余{len(needlist)}个话题，进入长时间段休息......")
                time.sleep(random.choice([600, 900, 1200, random.randint(300, 1200)]))  # 10分钟-20分钟
                print("休息结束。")
            time.sleep(random.choice([0.5, 1, 3, random.randint(1, 5)]))  # 每个话题页面请求间隔一个短时间段，500ms-5s

    def start(self):
        '''
        启动话题爬虫
        step1-2： -> table: ClassTopic, Topic_Class
        '''
        # ----------step1:爬取话题广场属类并从话题广场每个类爬取话题, 1+33*n次请求，基本不会变
        # st1 = Thread(target=self.step1())
        # st1.setDaemon(True)
        # st1.start()
        # ----------step2:获取话题详细信息, 33*20*n次请求
        # st2 = Thread(target=self.step2())
        # st2.setDaemon(True)
        # st2.start()
        self.step2()


# --------------------------------------------------------------------------------------------执行阶段
ts = topicSpyder(None)
ts.start()
# ------------------------------------------------------------------------------------------解决前期代码问题
# 1.temp.csv的重复行
# a = ('19821942', '杂家（北京）')
# with open(tempPath, 'r', newline="", encoding="utf-8") as f:
#     reader = csv.reader(f)
#     data = [(row[0].encode('utf-8').decode('utf-8-sig').strip(), row[1]) for row in reader]
#     temp = list(set(data))
#     if a in data:
#         print(1)
#     if a in temp:
#         print(2)
#     temp.sort(key=data.index)
#     with open(tempPath, 'w', newline="", encoding='utf-8') as w:
#         writer = csv.writer(w)
#         writer.writerows(temp)
# 2.关系表重复关系的删除 Topic_Class Topic_Parents Topic_Children
# 从数据库导出并去重
# session = ts.DbSession()
# Topic_Class
# all = [(row.categoryID, row.topicID) for row in session.query(Topic_Class).all()]
# temp = list(set(all))
# temp.sort(key=all.index)
# Topic_Parents
# all = [(row.topicID, row.parentTopicID) for row in session.query(Topic_Parents).all()]
# temp = list(set(all))
# temp.sort(key=all.index)
# Topic_Children
# all = [(row.topicID, row.childTopidID) for row in session.query(Topic_Children).all()]
# temp = list(set(all))
# temp.sort(key=all.index)
# session.close()
# 清空数据库，把去重的数据导回数据库
# if len(all) > len(temp):
#     Topic_Children.__table__.drop(ts.engine)
#     Topic_Children.__table__.create(ts.engine)
#     for row in temp:
#         ts.add_relationship(Topic_Children({"topicID": row[0], "childTopidID": row[1]}))
