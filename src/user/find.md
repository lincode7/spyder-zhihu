# 爬取用户hesenbao的信息
GET https://www.zhihu.com/people/hesenbao -> html -> json

    获取网页，从网页中提取出json数据
    一个用户请求携带部分问题和回答数据
# 获取用户关注的用户
GET https://www.zhihu.com/api/v4/members/he-nan-wei-shi-50/followees -> json

    data = {
        "include": 
            "data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics",
        "offset": 0,
        "limit": 20
    }
# 获取用户的关注用户 
GET https://www.zhihu.com/api/v4/members/ren-huan-xiang/followers -> json

    data = {
        "include": 
            "data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics",
        "offset": 0,
        "limit": 20
    }