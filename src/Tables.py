from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, DATE, Table, BigInteger, Text, Float

'''
数据库表模型
通过分析网页爬取的json字段，基本每个表模型数据列都可增加，且不影响加入数据库时的调用，以下模型只取其中部分字段
例：User表中可增加回答数，提问数，收到点赞数，关注数，被关注数等数据，按需在模型中添加后更新数据库的表的对应列的加减
'''

# 准备数据表
Base = declarative_base()


# 构造表的格式
# -基础数据表-id-唯一
# 用户数据表
class User(Base):
    __tablename__ = "USER"

    # 基本信息
    id = Column(String(64), primary_key=True, unique=True, comment="用户id")
    urlToken = Column(Text, comment="用户url连接关键词")
    name = Column(Text, comment="用户昵称")
    userType = Column(Text, comment="用户类型：组织与个人")
    headline = Column(Text, comment="用户签名")
    description = Column(Text, comment="用户简介")
    gender = Column(String(6), comment="用户性别")
    business = Column(Text, comment="用户所在行业")
    locations = Column(Text, comment="用户居住地")
    employments = Column(Text, comment="用户职业经历")
    educations = Column(Text, comment="用户教育经历")
    # 一般信息
    answerCount = Column(Integer, comment="回答数")
    zvideoCount = Column(Integer, comment="发布视频数")
    questionCount = Column(Integer, comment="提问数")
    commercialQuestionCount = Column(Integer, comment="付费咨询次数")
    articlesCount = Column(Integer, comment="发表文章数")
    columnsCount = Column(Integer, comment="开设专栏数")
    pinsCount = Column(Integer, comment="提出想法数")
    followingCount = Column(Integer, comment="主动关注数")
    favoriteCount = Column(Integer, comment="收藏数")
    hostedLiveCount = Column(Integer, comment="举办live的次数")
    followingColumnsCount = Column(Integer, comment="关注的专栏数")
    followingTopicCount = Column(Integer, comment="关注的话题数")
    followingQuestionCount = Column(Integer, comment="关注的问题数")
    followingFavlistsCount = Column(Integer, comment="关注的收藏夹数")
    # 成就信息
    followerCount = Column(Integer, comment="关注者数")
    favoritedCount = Column(Integer, comment="被收藏数")
    logsCount = Column(Integer, comment="参与公共编辑次数")
    voteupCount = Column(Integer, comment="收到点赞数")
    thankedCount = Column(Integer, comment="收到喜欢的次数")
    participatedLiveCount = Column(Integer, comment="举办live的参入人数")
    includedAnswersCount = Column(Integer, comment="知乎收录的回答数")
    includedArticlesCount = Column(Integer, comment="知乎收录的文章数")
    recognizedCount = Column(Integer, comment="专业认可数")

    # voteToCount = Column(Integer, comment="")
    # voteFromCount = Column(Integer, comment="")
    # thankToCount = Column(Integer, comment="")
    # thankFromCount = Column(Integer, comment="")

    def __init__(self, user):
        self.id = user["id"]
        self.urlToken = user["urlToken"]
        self.name = user["name"]
        self.userType = user["userType"]
        self.headline = user["headline"]
        self.description = user["description"]
        self.gender = user["gender"]
        self.followerCount = user["followerCount"]
        self.followingCount = user["followingCount"]
        self.answerCount = user["answerCount"]
        self.commercialQuestionCount = user["commercialQuestionCount"]
        self.questionCount = user["questionCount"]
        self.articlesCount = user["articlesCount"]
        self.columnsCount = user["columnsCount"]
        self.zvideoCount = user["zvideoCount"]
        self.favoriteCount = user["favoriteCount"]
        self.favoritedCount = user["favoritedCount"]
        self.pinsCount = user["pinsCount"]
        self.logsCount = user["logsCount"]
        self.voteupCount = user["voteupCount"]
        self.thankedCount = user["thankedCount"]
        self.hostedLiveCount = user["hostedLiveCount"]
        self.participatedLiveCount = user["participatedLiveCount"]
        self.includedAnswersCount = user["includedAnswersCount"]
        self.includedArticlesCount = user["includedArticlesCount"]
        self.followingColumnsCount = user["followingColumnsCount"]
        self.followingTopicCount = user["followingTopicCount"]
        self.followingQuestionCount = user["followingQuestionCount"]
        self.followingFavlistsCount = user["followingFavlistsCount"]
        # self.voteToCount = user["voteToCount"]
        # self.voteFromCount = user["voteFromCount"]
        # self.thankToCount = user["thankToCount"]
        # self.thankFromCount = user["thankFromCount"]
        self.recognizedCount = user["recognizedCount"]
        if isinstance(user["business"], list):
            self.business = ','.join(i["name"] for i in user["business"])
        elif isinstance(user["business"], dict):
            self.business = user["business"]["name"]
        self.locations = ','.join(i["name"] for i in user["locations"])
        try:
            self.employments = ','.join(f'{i["company"]["name"]}-{i["job"]["name"]}' for i in user["employments"])
        except:
            self.employments = ','.join(f'{i["company"]["name"]}' for i in user["employments"])
        self.educations = ','.join(i["school"]["name"]
                                   for i in user["educations"])


# 话题属类表-√
class ClassTopic(Base):
    __tablename__ = "CLASSTOPIC"

    id = Column(String(16), primary_key=True, unique=True,
                comment="话题类别id")
    name = Column(Text, comment="话题标题")

    def __init__(self, topic_class):
        self.id = topic_class["id"]
        self.name = topic_class["name"]


# 话题表-√
class Topic(Base):
    __tablename__ = "TOPIC"

    id = Column(String(16), primary_key=True, unique=True,
                comment="话题id")  # 话题id
    name = Column(Text, comment="话题标题")
    followersCount = Column(Integer, comment="关注数")
    questionsCount = Column(Integer, comment="问题数")
    bestAnswersCount = Column(Integer, comment="优质回答数")

    def __init__(self, topic):
        self.id = topic["id"]
        self.name = topic["name"]
        self.followersCount = topic["followersCount"]
        self.questionsCount = topic["questionsCount"]
        self.bestAnswersCount = topic["bestAnswersCount"]


# 问题表-√
class Question(Base):
    __tablename__ = "QUESTION"

    id = Column(String(16), primary_key=True, unique=True, comment="问题id")
    authorID = Column(String(64), comment="作者id")
    title = Column(Text, comment="问题标题")
    detail = Column(Text, comment="问题内容")
    createdTime = Column(Text, comment="创建时间")
    updatedTime = Column(Text, comment="更新时间")
    answerCount = Column(Integer, comment="回答数")
    visitCount = Column(Integer, comment="浏览次数")
    commentCount = Column(Integer, comment="评论数")
    followerCount = Column(Integer, comment="关注数")
    voteupCount = Column(Integer, comment="点赞次数")
    collapsedAnswerCount = Column(Integer, comment="")

    def __init__(self, question):
        self.id = question["id"]
        self.authorId = question["author"]["id"]
        self.title = question["title"]
        self.detail = question["excerpt"]
        self.createdTime = question["created"]
        self.answerCount = question["answerCount"]
        self.commentCount = question["commentCount"]
        self.followerCount = question["followerCount"]
        try:
            self.updatedTime = question["updatedTime"]
            self.visitCount = question["visitCount"]
            self.voteupCount = question["voteupCount"]
            self.collapsedAnswerCount = question["collapsedAnswerCount"]
        except:
            self.updatedTime = question["created"]


# 回答表-√
class Answer(Base):
    __tablename__ = "ANSWER"

    id = Column(String(16), primary_key=True, unique=True, comment="回答id")
    questionID = Column(String(16), comment="问题id")
    authorID = Column(String(64), comment="用户id")
    detail = Column(Text, comment="回答内容")
    createdTime = Column(Text, comment="创建时间")
    updatedTime = Column(Text, comment="更新时间")
    voteupCount = Column(Integer, comment="点赞数")
    commentCount = Column(Integer, comment="评论数")

    def __init__(self, answer):
        self.id = answer["id"]
        self.questionID = answer["question"]["id"]
        self.authorID = answer["author"]["id"]
        self.detail = answer["excerpt"]
        try:
            self.createdTime = answer["createdTime"]
        except:
            self.createdTime = answer["created_time"]
        try:
            self.updatedTime = answer["updatedTime"]
        except:
            self.updatedTime = answer["updated_time"]
        try:
            self.voteupCount = answer["voteupCount"]
        except:
            self.voteupCount = answer["voteup_count"]
        try:
            self.commentCount = answer["commentCount"]
        except:
            self.commentCount = answer["comment_count"]


# 评论表-√
class Comment(Base):
    __tablename__ = "COMMENT"

    id = Column(String(16), primary_key=True, unique=True, comment="评论id")
    authorID = Column(String(64), comment="作者id,用户id")
    responseType = Column(String(1), comment="评论对象描述，Q问题/A回答/C评论")
    responseID = Column(String(64), comment="评论对象id")
    detail = Column(Text, comment="评论内容")
    createdTime = Column(Text, comment="创建时间")
    voteCount = Column(Integer, comment="点赞数")

    def __init__(self, comment):
        self.id = comment["id"]
        self.authorID = comment["author"]["member"]["id"]
        self.responseType = comment["responseType"]
        self.responseID = comment["responseID"]
        self.detail = comment["content"]
        self.createdTime = comment["created_time"]
        self.voteCount = comment["vote_count"]


# -关系数据表-

# 话题的属类-1:n关系表-√
class Topic_Class(Base):
    '''
    一个话题属类包含多个话题
    :param relation: {"categoryID":'',"topicID":''}
    '''
    __tablename__ = "Topic&Class"
    id = Column(Integer, primary_key=True, unique=True)  # 自动创建的主键
    categoryID = Column(String(16), comment="类别id")
    topicID = Column(String(16), comment="话题id")

    def __init__(self, relation):
        self.categoryID = relation["categoryID"]
        self.topicID = relation["topicID"]


# 话题&子话题-1:n关系表-√
class Topic_Children(Base):
    '''
    一个话题有子话题，父话题
    :param relation: {"topicID":'',"childTopidID":''}
    '''
    __tablename__ = "Topic&Children"

    id = Column(Integer, primary_key=True, unique=True)  # 自动创建的主键
    topicID = Column(String(16), comment="话题id")
    childTopidID = Column(String(16), comment="子话题id")

    def __init__(self, relation):
        self.topicID = relation["topicID"]
        self.childTopidID = relation["childTopidID"]


# 话题&父话题-1:n关系表-√
class Topic_Parents(Base):
    '''
    一个话题有子话题，父话题
    :param relation: {"topicID":'',"childTopidID":''}
    '''
    __tablename__ = "Topic&Parents"

    id = Column(Integer, primary_key=True, unique=True)  # 自动创建的主键
    topicID = Column(String(16), comment="话题id")
    parentTopicID = Column(String(16), comment="父话题id")

    def __init__(self, relation):
        self.topicID = relation["topicID"]
        self.parentTopicID = relation["parentTopicID"]


# 问题&话题-1:n-关系表-√
class Question_Topics(Base):
    '''
    一个问题覆盖多个话题
    :param relation: {"questionID":'',"topicID":''}
    '''
    __tablename__ = "Question&Topics"

    id = Column(Integer, primary_key=True, unique=True)
    questionID = Column(String(16), comment="问题id")
    topicID = Column(String(16), comment="话题id")

    def __init__(self, relation):
        self.questionID = relation["questionID"]
        self.topicID = relation["topicID"]


# 热榜信息表-√
class Hot(Base):
    '''热榜信息表：问题id，排名，标题，热度，榜单日期'''
    __tablename__ = "HOT"

    id = Column(Integer, primary_key=True, unique=True)  # 自动创建的主键
    questionID = Column(String(16), comment="问题id")
    title = Column(Text, comment="问题标题")
    hot = Column(Integer, comment="热度")
    date = Column(Text, comment="榜单日期")

    def __init__(self, hot):
        self.questionID = hot["questionID"]
        self.title = hot["title"]
        self.hot = hot["hot"]
        self.date = hot["date"]


# 其他表-√
class RealForSpark(Base):
    __tablename__ = "RealForSpark"
    # 主键
    id = Column(String(32), primary_key=True, unique=True, comment="keyWord")
    weightValue = Column(Float, comment="权值")

    def __init__(self, data):
        self.id = data["keyWord"]
        self.weightValue = data["weightValue"]


# 表构建结束


DataTables = [User, ClassTopic, Topic, Question, Answer, Comment, RealForSpark]
RelationTables = [Topic_Class, Topic_Parents, Topic_Children, Question_Topics]
