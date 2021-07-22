# 爬话题类别
GET https://www.zhihu.com/topics -> html
# 处理数据
    # 找到标签
    soup = BeautifulSoup(html.text, 'xml')
    classlist = soup.findAll('li', attrs={'class':
                                          'zm-topic-cat-item'})  # 话题类别标签
    # 提取数据
    for oneclass in classlist:
        aclass = {"id": oneclass.get('data-id'), "title": oneclass.text}
        self.add(self.Topic_Class(aclass))
# 爬话题 id+title，记录topic与topicClass的从属关系
POST https://www.zhihu.com/node/TopicsPlazzaListV2 -> json

    data = {
        'method': 'next',
        'params': '{"topic_id":' + id + ',"offset":' + str(offset) + ',"hash_id":""}'
    }
# 返回示例
    data = {
        "r":0,
        "msg": [
            ...
            "<div class=\"item\"><div class=\"blk\">\n<a target=\"_blank\" href=\"/topic/19574331\">\n<img src=\"https://pic4.zhimg.com/e82bab09c_l.jpg\" alt=\"电热水器\">\n<strong>电热水器</strong>\n</a>\n<p>电热水器是指以电作为能源进行加热的热水器。是与燃气热水器、太阳…</p>\n\n<a id=\"t::-8043\" href=\"javascript:;\" class=\"follow meta-item zg-follow\"><i class=\"z-icon-follow\"></i>关注</a>\n\n</div></div>"
            ...
        ]
    }
# 处理数据
    # 找到标签
    soup = BeautifulSoup(html, 'xml')
    topicslist = soup.findAll('div', attrs={'class': 'item'})
    # 提取数据
    for onetopic in topicslist:
        atopic = {
            "id": onetopic.find('a', attrs={'target': '_blank'}).get('href').split(r'/')[-1],
            "title": onetopic.find('strong').text,
            "categoryID": id
    }
# 爬话题具体信息，记录topic数据以及topic的父子topic关系
GET https://www.zhihu.com/topic/19555513/hot -> html
# 处理数据
    # 找到标签
    soup = BeautifulSoup(html.text, 'xml')
    classlist = soup.findAll('script', attrs={'class': 'js-initialData'})  # json数据所在标签
    classlist = json.dumps(classlist)
    # 提取数据
    answers = classlist["answers"] # 10条,list
    topics = classlist["topics"]  # 1条,dict
    
    
