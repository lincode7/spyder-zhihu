import requests
from bs4 import BeautifulSoup
import json, os, sys, time
from threading import Thread
from BackEnd.Spyder.SpyderFrame import *
from BackEnd.Spyder.DBFrame import *

'''
    question.py -> tables:Question,Question_Topic,Question_Parents,Question_Children,Answer
    1.通过数据库以及因异常导致爬取失败的信息中获取待爬取qid列表
    2.当qid列表不空时不断取出表头qid进行爬取

    文件最后是执行部分
'''

tokenPath = os.path.join(os.path.dirname(os.getcwd()), 'user', 'token.json')


class questionSpyder(Spyder, DBIF):
    '''
    问题爬虫，爬取问题页面，携带部分回答信息，可截取部分用户urltoken
    -> data tables: Question, Answer
       relation tables: Question_Topic
    ：param cookie: 登录信息
    '''

    def __init__(self, cookie: str):
        super(questionSpyder, self).__init__("question")
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

    def get_question(self, qid: str):
        '''
        获取一个问题详细信息 -> table:Question, Question_Topic, Answer
        '''
        url = 'https://www.zhihu.com/question/' + qid
        code = 200  # 请求接收器
        try:
            # GET请求
            html = self.s.request(method="POST",
                                  url=url,
                                  headers=super().random_Agent(),
                                  proxies=super().random_proxy())
            code = html.status_code
            html.raise_for_status()  # 检查请求异常
            # 问题信息json数据位置
            soup = BeautifulSoup(html.text, 'lxml')
            po1 = soup.find('script', attrs={'id': 'js-initialData'}).contents
            # str->json
            po1 = json.loads(po1[0])
            # 提取json, 找到数据位置
            question_json = po1["initialState"]["entities"]["questions"][qid]  # 问题数据
            save_token(question_json["author"]["urlToken"])  # 为爬取user提供更多前供userToken
            question_topics = question_json["topics"]
            answer_json = po1["initialState"]["entities"]["answers"]  # 回答数据列表
            # 保存到数据库
            self.update(Question(question_json))  # -> table: Question
            for topic in question_topics:
                self.add_relationship(
                    Question_Topics({"questionID": qid, "topicID": topic["id"]}))  # -> table: Question_Topics
            for answer in answer_json.values():
                save_token(answer["author"]["urlToken"])  # 为爬取user提供更多前提userToken
                self.add(Answer(answer))  # -> table: Answer
        except Exception as e:
            print(e)
            del_exception('question', step=1, id=qid, code=code, discription=e.__str__())

    def updatelist(self, oldlist=[]):
        '''
        更新爬虫缓冲区
        从本地异常进度保存文件，以及服务器数据库Question, Answer, Comment, Hot表，更新待爬取的qid列表
        :param oldlist: 现存缓冲区
        :return 爬虫缓冲区->qid
        '''
        local = load_retry('question', 1)  # 本地保存的因为异常需要重新爬取的问题id列表
        session = self.DbSession()
        aqidlist = [row.qid for row in
                    session.query(Answer.questionID.label("qid")).group_by(Answer.questionID).all()]  # 回答表中存在的问题id列表
        cqidlist = [row.qid for row in
                    session.query(Comment.responseID.label("qid")).filter(Comment.responseType == 'Q').group_by(
                        Comment.responseID).all()]  # 评论表中存在的id列表
        hqidlist = [row.qid for row in
                    session.query(Hot.questionID.label("qid")).group_by(Hot.questionID).all()]  # 热榜表中存在的问题id列表
        existqidlist = [row.qid for row in session.query(Question.id.label("qid")).all()]  # 问题表中存在的问题id列表
        session.close()
        need = [id for id in
                list((set(local) | set(oldlist) | set(aqidlist) | set(cqidlist) | set(hqidlist)) - set(existqidlist))]
        return need

    def from_answer_get_question(self):
        '''
        启动爬虫
        更新缓冲区，爬取问题数据
        '''
        needlist = self.updatelist()
        signal = 0  # 爬虫休息信号
        while len(needlist):
            qid = needlist.pop(0)
            signal += 1
            self.get_question(str(qid))
            if signal != 0 and signal % 5000 == 0:  # 每请求5k个问题，随机休眠一个长时间段
                needlist = self.updatelist()
                print(f"剩余{len(needlist)}个问题，进入长时间段休息......")
                time.sleep(random.choice([600, 900, 1200, random.randint(300, 1200)]))  # 10分钟-20分钟
                print("休息结束。")
            time.sleep(random.choice([0.5, 1, 3, random.randint(1, 5)]))  # 每个话题页面请求间隔一个短时间段，500ms-5s

    def from_related_get_question(self):
        '''
        知乎v4 API，缺少身份验证，无法使用
        '''
        pass


# --------------------------------------------------------------------------------------------执行阶段
qs = questionSpyder(None)
qs.from_answer_get_question()
