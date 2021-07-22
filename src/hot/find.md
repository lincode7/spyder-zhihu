# 一次访问获取当天当时刷新热榜，共50条，以及部分前几天热榜数据（不登陆）
一次访问获取当天当时刷新热榜，共50条，可以使用另一个接口获取指定历史数据

# methods   url                       -> reponse type
GET https://tophub.today/n/mproPpoq6O -> html

# 找到当天实时热榜标签位置
today_hot = soup.find('tbody') # 当天热榜位于页面第一个tbody标签内
<!-- 一条数据例子
<tr>
    <td align="center">1.</td>
    <td class="al"><a href="https://www.zhihu.com/question/420016446" target="_blank" rel="nofollow" itemid="39003207">如何看待 OPPO 给应届生开出 40w+ 的待遇？</a></td>
    <td>928 万热度</td>
    <td align="right"><a class="collect-a" href="https://www.zhihu.com/question/420016446" title="查看详细" target="_blank" rel="nofollow"><i class="m-n">&#xe652;</i></a></td>
</tr>
-->
<!-- 提取信息 -->
question = {
    "id": ,
    "title": ,
    "hot": ,
    "rank": ,
}

# 需要找到日期




