# 知乎综合数据爬虫  
爬取知乎数据信息，存储到服务器的数据库中，对知乎热榜，话题，问题，回答，评论，用户数据进行分析挖掘，通过ajax传输分析结果到前端，前端运用EChats和Bootstrap，绘制热榜话题热度图、热榜词云、用户画像，用户分布，问题-回答曲线等。  
在该项目中，我负责构建MySQL数据库与爬取知乎数据。  
1. 实现了数据去重添加、更新、删除接口，实现了数据操作异常记录；  
2. 实现了爬虫的分板块（话题，问题，回答，评论，用户）多进程爬取，基本反爬虫机制、本地异常日志记录、重启本地恢复、多表分析生成爬取列表补充关系数据等；  
3. 测试与优化。  
7天内，爬取问题、回答、评论、用户总计100w+条数据。

## 开发环境
- Windows 10 1909
- PyCharm（Community Edition）
- Python 3.7
- 第三方库：
    1. requests：HTTP库，用于网络访问；
    2. beautifulsoup：网页解释库，提供lxml的支持
    3. sqlalchemy：关系型数据库的orm库，提供简易明了的mysql操作

## 测试支持
- 检查各py文件的引入路径

        ···
        from Tables import * # 找不到引入位置可尝试 from src.Tables import *
        ···
- 修改DBFrame.py

        ···
            def __init__(self, username, passwd, address="你的远程或本地数据库链接"):
        ···
- 修改answer、comment、hot、question、topic、user文件夹下的py文件，

        ···
            def __init__(self, cookie: str):  
                super(answerSpyder, self).__init__("answer")  
                DBIF.__init__(self, username='远程链接数据库的用户名', passwd="远程链接数据库的密码")  
        ···
- 运行
    - 先运行topic.py至自动结束，话题数据少1w左右，很快就爬取结束
    - 其后先运行question.py一段时间（10分钟-1小时不等）、再运行answer、comment、user的py文件，多进程爬取相关数据。（只在最初爬取阶段按该顺序执行）
    - 上述步骤执行过后，以后中断继续爬取就可同时运行question、answer、comment、user的py文件

## 注：每个文件夹下提前删除json文件或放入useless文件夹。现存json为个人使用时的日志表，仅作参考，一定程度影响预期数据效果。
