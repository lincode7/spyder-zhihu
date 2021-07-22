
# 对问题的评论
    GET https://www.zhihu.com/api/v4/questions/58570383/root_comments -> json
    params = {
        "order":"normal",
        "limit":20,
        "offset":0,
        "status":"open"
    }
response: comment["data"]中的10条
根据comment["paging"]["next"]访问后续数据
根据comment["paging"]["is_end"]判断是否还有剩余数据
# 对回答的评论
    GET https://www.zhihu.com/api/v4/answers/1429104963/root_comments -> json
    params = {
        "order":"normal",
        "limit":20,
        "offset":0,
        "status":"open"
    }
