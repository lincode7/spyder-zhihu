import requests
from bs4 import BeautifulSoup
import json, os, sys, time
from threading import Thread
from BackEnd.Spyder.SpyderFrame import *
from BackEnd.Spyder.DBFrame import *

'''
    question.py -> tables:Answer
    1.通过数据库以及因异常导致爬取失败的信息中获取待爬取qid列表
    2.当qid列表不空时不断取出表头qid进行爬取

    文件最后是执行部分
'''


class answerSpyder(Spyder, DBIF):
    '''
    回答爬虫，爬取问题页面，携带部分回答信息，可截取部分用户urltoken
    -> table: Question, Answer

    ：param cookie: 登录信息
    '''

    def __init__(self, cookie: str):
        super(answerSpyder, self).__init__("answer")
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

    def get_answer(self, qid: str, offset=0):
        '''
        获取一个回答详细信息 -> table:Answer
        '''

        url = f'https://www.zhihu.com/api/v4/questions/{qid}/answers'
        data = {
            "include": "data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,attachment,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,is_labeled,paid_info,paid_info_content,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_recognized;data[*].mark_infos[*].url;data[*].author.follower_count,vip_info,badge[*].topics;data[*].settings.table_of_content.enabled",
            "limit": 20,
            "offset": offset,
            "platform": "desktop",
            "sort_by": "default"
        }
        code = 200  # 请求接收器
        total = -1
        try:
            # GET请求
            data = self.s.request(method='GET', url=url, params=data, headers=super().random_Agent(),
                                  proxies=super().random_proxy())
            code = data.status_code
            data.raise_for_status()  # 检查请求异常
            # 处理数据
            data = json.loads(data.content)
            total = data["paging"]["totals"]  # 数据总量
            is_end = data["paging"]["is_end"]  # 数据尾标志
            if data["data"]:
                # 提取数据
                answerlist = data["data"]
                for answer in answerlist:
                    save_token(answer["author"]["url_token"])
                    self.update(Answer(answer))
                if not is_end:
                    time.sleep(random.choice([0.5, 1, 3, random.randint(1, 5)]))  # 每个话题页面请求间隔一个短时间段，500ms-5s
                    self.get_answer(qid, offset + 20)
        except Exception as e:
            print(e)
            del_exception('answer', step=1, id=qid, offset=offset, totals=total, code=code, discription=e.__str__())

    def updatelist(self, oldlist=[]):
        '''
        更新缓存列表
        从本地异常进度保存文件，数据库Answer, Question, Comment表，更新待爬取的qid列表
        :param oldlist: 现存缓存列表
        :return: 更新后的缓存列表 (qid, offset)
        '''
        session = self.DbSession()
        local = list(set(load_retry('answer', 1)))  # 本地进度列表 (qid,offset,totals)
        localqid = [id[0] for id in local]  # 本地qid列表
        subqf = session.query(Answer.questionID.label("qid"), func.count(Answer.id).label("offset")).group_by(
            Answer.questionID).subquery()  # 子查询 -> (qid,offset)
        subqt = session.query(Question.id.label("qid"), Question.answerCount.label("totals")).filter(
            Question.answerCount > 0).subquery()  # 子查询 -> (qid,totals)
        dblist = [(row.qid, row.offset, row.totals) for row in
                  session.query(subqf.c.qid, subqf.c.offset, subqt.c.totals).outerjoin(
                      subqt, subqf.c.qid == subqt.c.qid).all()]  # 数据库进度列表 (qid,offset,totals)
        session.close()
        dbqid = [col[0] for col in dblist]  # 数据库qid列表
        # 同步本地与数据库的进度,以数据库进度为准
        tempqid = list(set(localqid) & set(dbqid))  # 本地与数据库同时存在的qid
        # 从本地进度中删除tempqid，保存db进度
        for i in local:
            if i[0] in tempqid:
                local.remove(i)
        # 确认进度并合并
        need = list(set(local) | set(dblist))
        # 检查offset<totals  (qid,offset,totals) -> (i[0],i[1],i[-1])
        for i in need:
            if i[-1] != None and i[1] >= i[-1]:
                need.remove(i)
        need = [(row[0], row[1]) for row in need]
        return need

    def start(self):
        '''
        启动爬虫
        更新缓冲区，爬取回答数据
        '''
        needlist = self.updatelist()
        signal = 0  # 爬虫休息信号
        while len(needlist):
            (qid, offset) = needlist.pop(0)
            signal += 1
            self.get_answer(qid, offset)
            if signal != 0 and signal % 5000 == 0:  # 每请求5k个问题，随机休眠一个长时间段
                needlist = self.updatelist()
                print(f"剩余{len(needlist)}个问题，进入长时间段休息......")
                time.sleep(random.choice([600, 900, 1200, random.randint(300, 1200)]))  # 10分钟-20分钟
                print("休息结束。")
            time.sleep(random.choice([0.5, 1, 3, random.randint(1, 5)]))  # 每个话题页面请求间隔一个短时间段，500ms-5s


asp = answerSpyder(None)
asp.start()
