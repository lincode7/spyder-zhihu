import requests
import random, json, os

retryPath = r"./retry.json"
tokenPath = r"./token.json"
tokenLoadPath = [os.path.join(os.path.dirname(os.getcwd()), 'topic', 'token.json'),
                 os.path.join(os.path.dirname(os.getcwd()), 'question', 'token.json'),
                 os.path.join(os.path.dirname(os.getcwd()), 'answer', 'token.json'),
                 os.path.join(os.path.dirname(os.getcwd()), 'comment', 'token.json')]


def del_exception(spydername: str, path=retryPath, **kwargs):
    '''
    记录爬虫过程中出现的异常，保存爬虫进度，

    例:topic爬虫在步骤1爬取id为123的话题时出现了404异常

    del_exception('topic',setp=1,id='123',code=404,description)

    :param spydername: 爬虫名字
    :param kwargs: 爬虫进度，必须包含setp字段
    :param path: retry.json路径，默认与调用py文件同目录
    '''
    try:
        with open(path, 'r', encoding='utf-8') as f:
            info = json.load(f)
            with open(path, 'w', encoding='utf-8') as f2:
                info.append({spydername: kwargs})
                json.dump(info, f2)
    except Exception as e:
        print(e)
        # 文件不存在，创建并写入基础格式
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([{spydername: kwargs}], f)


def load_retry(spydername: str, step: int):
    '''
    加载保存的爬虫进度，-> 爬虫某阶段需要重新爬取的id列表

    :param spydername: 爬虫名称
    :param step: 出现异常的爬虫步骤
    :param path: retry.json路径，默认与调用py文件同目录
    :return: 该步骤下需要重新爬取的id列表
    '''
    try:
        with open(retryPath, 'r', encoding='utf-8') as f:
            info = json.load(f)  # 加载
            data = []
            for i in list(info):
                if list(i.keys()) == [spydername] and i[spydername]["step"] == step:
                    # 提取进度
                    log = [i[spydername]["id"]]  # 零食变量，组成一条进度数据
                    if "offset" in i[spydername].keys():
                        log.append(i[spydername]["offset"])
                    if "totals" in i[spydername].keys():
                        log.append(i[spydername]["totals"])
                    if "type" in i[spydername].keys():
                        log.append(i[spydername]["type"])
                    if len(log) == 1:
                        log = log[0]
                    else:
                        log = tuple(log)
                    data.append(log)
                    info.remove(i)  # 更新retry信息
            with open(retryPath, 'w', encoding='utf-8') as f2:
                json.dump(info, f2)  # 更新retry信息写出
            return data
    except Exception as e:
        print(e)
        # 文件不存在，创建并写入基础格式
        with open(retryPath, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []


def save_token(token: str):
    '''
    保存一条用户token

    :param token: token数据
    '''
    try:
        local = []  # 本地列表
        with open(tokenPath, 'r', encoding='utf-8') as f:
            local = json.load(f)  # 加载本地
        if token not in local:
            local.append(token)  # 并入本地列表
        with open(tokenPath, 'w', encoding='utf-8') as f2:
            json.dump(local, f2)  # 写入
    except Exception as e:
        print(e)
        # 文件不存在，创建并写入基础格式
        with open(tokenPath, 'w', encoding='utf-8') as f:
            json.dump([token], f)


def load_token():
    '''
    载入保存的用户token列表
    :return token列表
    '''
    try:
        # 合并其他路径下的token.json
        local = []
        # 从其他爬虫目录下获取爬取过程中保存的urlToken
        for path in tokenLoadPath:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    local = list(set(local) | set(json.load(f)))  # 合并
            except Exception as e:
                # 文件不存在，创建并写入基础格式
                with open(path, 'w', encoding='utf-8') as f2:
                    json.dump([], f2)
        # 合并当前目录下的token.json
        with open(tokenPath, 'r', encoding='utf-8') as r:
            local = list(set(local) | set(json.load(r)))  # 合并
        # 写入合并结果到user爬虫目录下
        with open(tokenPath, 'w', encoding='utf-8') as w:
            json.dump(local, w)
        # 返回合并结果
        return local
    except Exception as e:
        print(e)
        # 文件不存在，创建并写入基础格式
        with open(tokenPath, 'w', encoding='utf-8') as w:
            json.dump([], w)
        return []


def update_token(tokenlist: list):
    '''
    更新保存的用户token列表，仅用于用户爬虫中断时的进度保留

    :param tokenlist: 待爬取用户token列表
    '''
    try:
        local = []  # 本地文件内部列表
        # 读取本地列表
        with open(tokenPath, 'r', encoding='utf-8') as r:
            local = json.load(r)
        newlist = list(set(local) | set(tokenlist))  # 本地与程序合并后的列表
        # 写入本地文件
        with open(tokenPath, 'w', encoding='utf-8') as w:
            json.dump(newlist, w)
    except:
        # 读取时发现文件不存在，直接创建并写入
        with open(tokenPath, 'w', encoding='utf-8') as w:
            json.dump(tokenlist, w)


class Spyder:
    def __init__(self, name: str):
        # 初始化爬虫信息
        self.name = name
        # 准备会话
        self.s = requests.Session()
        self.s.keep_alive = True
        self.headers = {
            'User-Agent': None,
        }

    @staticmethod
    def random_Agent():
        '''
        随机生成浏览器头
        '''
        agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:65.0) Gecko/20100101 Firefox/65.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/31.0.1650.18 Mobile/11B554a Safari/8536.25',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4',
            'Mozilla/5.0 (Linux; Android 4.2.1; M040 Build/JOP40D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.59 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; M351 Build/KTU84P) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ]
        return {"User-Agent": random.choice(agent_list)}

    @staticmethod
    def random_proxy():
        '''
        随机生成代理ip
        '''
        # http = None
        # https = None
        # return {
        #     "http": random.choice(http),
        #     "https": random.choice(https),
        # }
        pass
