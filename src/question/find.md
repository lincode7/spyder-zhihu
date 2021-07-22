GET https://www.zhihu.com/question/464672807 -> html -> json
获取网页，从网页中提取出json数据，464672807更换为指定问题id

问题信息json数据位置
<!-- json所在标签位置 -->
    po1 = soup.find('script', attrs={'id':'js-initialData'}).contents
    json.loads(po1[0])
<!-- 问题相关信息所在json位置 -->
    question_json = po1["initialState"]["entities"]["questions"]["464672807"]
<!-- 问题默认携带回答所在json位置 -->
    answer_list = po1["initialState"]["entities"]["answer"]
    
    
    
    
# 意外发现 不需cookie和authToken
通过 
    
    GET https://www.zhihu.com/api/v4/questions/58570383
可以获得
    
    {
        "type":"question",
        "id":58570383,
        "title":"讲真，应届生一般工资多少啊？",
        "question_type":"normal",
        "created":1492330476,
        "updated_time":1492330476,
        "url":"https://www.zhihu.com/api/v4/questions/58570383",
        "relationship":{}
    }
通过 
    
    GET https://www.zhihu.com/api/v4/topics/19550266
可以获得
    
    {
        "unanswered_count": 227155, 
        "is_black": false, 
        "excerpt": "\u82f9\u679c\u786c\u4ef6\u4ea7\u54c1\u4ee5\u53ca\u8f6f\u4ef6\u670d\u52a1\uff0c\u5305\u62ec\uff1aiMac, iMac Pro, Mac Pro, Mac mini, MacBook, MacBook Air, MacBook Pro, Apple TV, iPod, AirPods, AirPods Pro, iPhone, iPad, iPad Air, iPad Pro, HomePod\u7b49\u786c\u4ef6\u4ea7\u54c1\uff0ciOS,macOS,iPadOS,tvOS,Apple Arcade\u7b49\u8f6f\u4ef6\u670d\u52a1\u53ca\u5404\u79cdapple\u914d\u4ef6\u3002", "is_vote": false, "is_super_topic_vote": true, "id": "19550266", "questions_count": 227155, "name": "\u82f9\u679c\u4ea7\u54c1", "introduction": "\u82f9\u679c\u786c\u4ef6\u4ea7\u54c1\u4ee5\u53ca\u8f6f\u4ef6\u670d\u52a1\uff0c\u5305\u62ec\uff1aiMac, iMac Pro, Mac Pro, Mac mini, MacBook, MacBook Air, MacBook Pro, Apple TV, iPod, AirPods, AirPods Pro, iPhone, iPad, iPad Air, iPad Pro, HomePod\u7b49\u786c\u4ef6\u4ea7\u54c1\uff0ciOS,macOS,iPadOS,tvOS,Apple Arcade\u7b49\u8f6f\u4ef6\u670d\u52a1\u53ca\u5404\u79cdapple\u914d\u4ef6\u3002", 
        "father_count": 3, 
        "url": "http://www.zhihu.com/api/v4/topics/19550266", 
        "followers_count": 59473, 
        "avatar_url": "https://pic2.zhimg.com/50/1212e4cc2_720w.jpg?source=54b3c3a5", 
        "best_answers_count": 775953, 
        "type": "topic"
    }
通过 
    
    GET https://www.zhihu.com/api/v4/members/asdf
可以获得
    
    {
        "id":"c3e31281c15283948ce5d6d0784e4800",
        "url_token":"asdf",
        "name":"窦禹",
        "use_default_avatar":false,
        "avatar_url":"https://pic2.zhimg.com/aa0fe955784fbe7f0bbd30f1581230aa_l.jpg",
        "avatar_url_template":"https://pic1.zhimg.com/aa0fe955784fbe7f0bbd30f1581230aa.jpg","
        is_org":false,
        "type":"people",
        "url":"https://www.zhihu.com/api/v4/people/asdf",
        "user_type":"people",
        "headline":"台灯",
        "gender":0,
        "is_advertiser":false,
        "vip_info":{
            "is_vip":false,
            "rename_days":"60",
            "entrance_v2":null,
            "rename_frequency":0,
            "rename_await_days":0
        },
        "is_realname":false,
        "has_applying_column":false
    }
通过 
    
    GET https://www.zhihu.com/api/v4/answers/100000803
可以获得
    
    {
        "id":100000803,
        "type":"answer",
        "answer_type":"normal",
        "question":{
            "type":"question",
            "id":45570670,
            "title":"《美国队长3》的三观特别歪吗？",
            "question_type":"normal",
            "created":1462522124,
            "updated_time":1591176008,
            "url":"https://www.zhihu.com/api/v4/questions/45570670",
            "relationship":{}
        },
        "author":{
            "id":"ae814c0c3a55e5cbb11bba11d5aaaa49",
            "url_token":"liu-yu-chen-63-51",
            "name":"刘雨辰",
            "avatar_url":"https://pic1.zhimg.com/1796b6ef9_l.jpg?source=1940ef5c",
            "avatar_url_template":"https://pic4.zhimg.com/1796b6ef9.jpg?source=1940ef5c","
            is_org":false,
            "type":"people",
            "url":"https://www.zhihu.com/api/v4/people/ae814c0c3a55e5cbb11bba11d5aaaa49",
            "user_type":"people",
            "headline":"在无限中寻求有限的自由",
            "badge":[],
            "badge_v2":{"title":"","merged_badges":[],"detail_badges":[],"icon":"","night_icon":""},
            "gender":1,
            "is_advertiser":false,
            "is_privacy":false},
            "url":"https://www.zhihu.com/api/v4/answers/100000803",
            "is_collapsed":false,
            "created_time":1462849478,
            "updated_time":1462849478,
            "extras":"",
            "is_copyable":true,
            "ContentMark":null,
            "relationship":{"upvoted_followees":[]},
            "ad_answer":null
        }
通过 
    
    GET https://www.zhihu.com/api/v4/comments/1000002397
可以获得
    
    {
        "id":1000002397,
        "type":"comment",
        "url":"https://www.zhihu.com/api/v4/comments/1000002397",
        "content":"\u003cp\u003eit's always the husband.\u003c/p\u003e",
        "featured":false,
        "top":false,
        "collapsed":false,
        "is_author":false,
        "is_delete":false,
        "created_time":1595054184,
        "resource_type":"question",
        "reviewing":false,
        "allow_like":true,
        "allow_delete":false,
        "allow_reply":true,
        "allow_vote":true,
        "can_recommend":false,
        "can_collapse":false,
        "attached_info":"ggIGCAsQARgA",
        "author":{
            "role":"normal",
            "member":{
                "id":"9145b930980d8226ccad2daf3a325504",
                "url_token":"zi-se-5-28",
                "name":"紫色",
                "avatar_url":"https://pic1.zhimg.com/db52770b3dc618a3b1edd112ca7f7d91.jpg?source=06d4cd63",
                "avatar_url_template":"https://pic4.zhimg.com/db52770b3dc618a3b1edd112ca7f7d91.jpg?source=06d4cd63",
                "is_org":false,
                "type":"people",
                "url":"https://www.zhihu.com/api/v4/people/9145b930980d8226ccad2daf3a325504",
                "user_type":"people",
                "headline":"营销",
                "badge":[],
                "gender":0,
                "is_advertiser":false,
                "vip_info":{"is_vip":false}
            }
        },
        "is_parent_author":false,
        "vote_count":1,
        "voting":false,
        "liked":false,
        "disliked":false
    }
    
