import requests
from bs4 import BeautifulSoup
import json, os, sys, time
from threading import Thread
from BackEnd.Spyder.SpyderFrame import *
from BackEnd.Spyder.DBFrame import *


class commentSpyder(Spyder, DBIF):
    '''
    评论爬虫，可截取部分用户urltoken -> table: Comment

    ：param cookie: 登录信息
    '''

    def __init__(self, cookie: str):
        super(commentSpyder, self).__init__("comment")
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

    def get_question_comment(self, id, offset=0):
        '''
        获取一个问题评论信息 -> table:Comment
        :param id: questionID
        :param offset: 查询起点，从第几条开始
        '''

        url = f'https://www.zhihu.com/api/v4/questions/{id}/root_comments'
        data = {
            "order": "normal",
            "limit": 20,
            "offset": offset,
            "status": "open"
        }
        code = 200  # 请求接收器
        total = -1
        try:
            # GET请求
            data = self.s.request(method='GET', url=url, params=data,
                                  headers=self.random_Agent(),
                                  proxies=self.random_proxy())
            code = data.status_code
            data.raise_for_status()  # 检查请求状态
            # 数据处理与保存
            data = json.loads(data.content)  # to json
            total = data["paging"]["totals"]
            is_end = data["paging"]["is_end"]
            for i in data["data"]:  # 遍历评论
                save_token(i["author"]["member"]["url_token"])  # 本地保存用户token，辅助user爬虫
                i["responseType"] = 'Q'  # 向一条评论中添加评论对象描述字段
                i["responseID"] = id  # 向一条评论中添加评论对象id字段
                self.update(Comment(i))  # 插入数据表Comment
                for j in i["child_comments"]:  # 遍历评论的子评论
                    save_token(i["author"]["member"]["url_token"])  # 本地保存用户token，辅助user爬虫
                    j["responseType"] = 'C'  # 向一条评论中添加评论对象描述字段
                    j["responseID"] = i["author"]["member"]["id"]  # 向一条评论中添加评论对象id字段
                    self.update(Comment(j))  # 插入数据表Comment
            if not is_end:
                self.get_question_comment(id, offset + 20)
        except Exception as e:
            print(e)
            del_exception('comment', step=1, id=id, offset=offset, totals=total, type='Q', code=code,
                          discription=e.__str__())

    def get_answer_comment(self, id, offset=0):
        '''
        获取一个回答评论信息 -> table:Comment, Question_Comment, Comment_Comment
        :param id: answerID
        :param offset: 查询起点，从第几条开始
        '''

        url = f'https://www.zhihu.com/api/v4/answers/{id}/root_comments'
        data = {
            "order": "normal",
            "limit": 20,
            "offset": offset,
            "status": "open"
        }
        code = 200  # 请求接收器
        total = -1
        try:
            # GET请求
            data = self.s.request(method='GET', url=url, params=data,
                                  headers=self.random_Agent(),
                                  proxies=self.random_proxy())
            code = data.status_code
            data.raise_for_status()  # 检查请求状态
            # 数据处理与保存
            data = json.loads(data.content)  # to json
            total = data["paging"]["totals"]
            is_end = data["paging"]["is_end"]
            for i in data["data"]:  # 遍历评论
                save_token(i["author"]["member"]["url_token"])  # 本地保存用户token，辅助user爬虫
                i["responseType"] = 'A'  # 向一条评论中添加评论对象描述字段
                i["responseID"] = id  # 向一条评论中添加评论对象id字段
                self.update(Comment(i))  # 插入数据表Comment
                for j in i["child_comments"]:  # 遍历评论的子评论
                    save_token(i["author"]["member"]["url_token"])  # 本地保存用户token，辅助user爬虫
                    j["responseType"] = 'C'  # 向一条评论中添加评论对象描述字段
                    j["responseID"] = i["author"]["member"]["id"]  # 向一条评论中添加评论对象id字段
                    self.update(Comment(j))  # 插入数据表Comment
            if not is_end:
                self.get_answer_comment(id, offset + 20)
        except Exception as e:
            print(e)
            del_exception('comment', step=2, id=id, offset=offset, totals=total, type='A', code=code,
                          discription=e.__str__())

    def updatelist(self, oldlist=[]):
        '''
        更新缓存列表 (id, offset, totals, type) (问题id/回答id,请求起点，评论对象)
        :param oldlist: 现存缓存列表
        :return: 更新后的缓存列表 (id, offset, totals, type)
        '''
        session = self.DbSession()
        local = load_retry('comment', 1) + load_retry('comment', 2)  # 本地回答评论异常进度列表 (id, offset, totals, type)
        qid_total = session.query(Question.id,
                                  Question.commentCount.label("totals")).filter(
            Question.commentCount > 0).all()  # 数据库qid列表 (id, totals, 'Q')
        qid = [row.id for row in qid_total]  # 数据库qid列表
        aid_total = session.query(Answer.id, Answer.commentCount.label("totals")).filter(
            Answer.commentCount > 0).all()  # 数据库aid列表 (id, totals, 'A')
        aid = [row.id for row in aid_total]  # 数据库aid列表
        # 回答表id列表 (id, offset, type)
        exist = session.query(Comment.responseID.label("id"), func.count(Comment.id).label("offset"),
                              Comment.responseType.label("type")).group_by(Comment.responseType,
                                                                           Comment.responseID).all()
        session.close()
        # 同步本地和数据库进度
        # 筛查存在与评论表中的数据，生成没爬完的进度和没开始的进度
        ncomplete = []  # 数据库中没爬完的进度 (id, offset, totals, type)
        for row in exist:
            if row.type == 'Q' and row.id in qid:
                if row.offset < qid_total[qid.index(row.id)].totals:
                    ncomplete.append((row.id, row.offset, qid_total[qid.index(row.id)].totals, 'Q'))  # 插入进度
                qid_total.pop(qid.index(row.id))  # 删除存在的qid
                qid.pop(qid.index(row.id))  # 删除存在的qid
            elif row.type == 'A' and row.id in aid:
                if row.offset < aid_total[aid.index(row.id)].totals:
                    ncomplete.append((row.id, row.offset, aid_total[aid.index(row.id)].totals, 'A'))  # 插入进度
                aid_total.pop(aid.index(row.id))  # 删除存在的aid
                aid.pop(aid.index(row.id))  # 删除存在的aid
            else:
                continue
        # 筛查后生成数据库中没开始爬取的进度
        nstart = [(row.id, 0, row.totals, 'Q') for row in qid_total] + \
             [(row.id, 0, row.totals, 'A') for row in aid_total] # 数据库中没开始的进度
        # 处理本地与没爬完的的进度冲突，以数据库为主
        ids = [row[0] for row in ncomplete]
        for row in local:
            # 如果本地与数据库进度冲突-id一致type一致
            if row[0] in ids and row[-1] == ncomplete[ids.index(row[0])][-1]:
                local.remove(row)
        need = local + ncomplete + nstart
        return need  # (id, offset, totals, type)

    def start(self):
        '''
        启动爬虫
        更新缓冲区，爬取评论数据
        '''
        needlist = self.updatelist()
        signal = 0  # 爬虫休息信号
        while len(needlist):
            (id, offset, totals, type) = needlist.pop(0)
            signal += 1
            if type == 'Q':
                self.get_question_comment(id, offset)
            elif type == 'A':
                self.get_answer_comment(id, offset)
            if signal != 0 and signal % 5000 == 0:  # 每请求5k个问题，随机休眠一个长时间段
                needlist = self.updatelist()
                print(f"剩余{len(needlist)}个问题，进入长时间段休息......")
                time.sleep(random.choice([600, 900, 1200, random.randint(300, 1200)]))  # 10分钟-20分钟
                print("休息结束。")
            time.sleep(random.choice([0.5, 1, 3, random.randint(1, 5)]))  # 每个话题页面请求间隔一个短时间段，500ms-5s


cs = commentSpyder(None)
# cs.get_question_comment("58570383") # 测试
# cs.get_answer_comment("1429104963")   # 测试
cs.start()
