import random
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json, os, sys
from threading import Thread
from urllib.parse import quote
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from SpyderFrame import Spyder



currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from DBFrame import  *

class hotspider(Spyder,DBIF):

    def __init__(self, cookie: str):
        super(hotspider, self).__init__('hot')
        self.s = requests.Session()  # 准备httpvvvvs会话
        self.s.keep_alive = True
        self.db = DBIF("HQY", "123456")
        DBIF.__init__(self, username='HQY', passwd="123456")
        # self.e = db.engine
        self.hot_list=[]
        if cookie:
            self.cookie = {
                i.split("=")[0]: i.split("=")[-1]
                for i in cookie.split("; ")
            }
        else:
            self.cookie = None


    def update_hot_class(self,date):
        url = "https://tophub.today/do"
        payload = {
            "p":"1",
            "day":date,
            "nodeid":"6",
            "t":"itemsbydate",
            "c":"node"
        }
        code=200# 请求接收器

        try:
            # POST请求
            data = self.s.request(method="POST",
                                  data=payload,
                                  cookies=self.cookie,
                                  url=url,
                                  headers=super().random_Agent(),
                                  proxies=super().random_proxy())
            code = data.status_code

            data.raise_for_status()  # 检查请求异常
            # 提取数据
            data = json.loads(data.text)  # to json
            # print(data)  # hqy
            lists=data["data"]["items"]
            hot_item={}


            for hot in lists:

                hot_item.update({"questionID": hot["ID"]})
                hot_item.update({"title": hot["title"]})
                hot_item.update({"hot": int(hot["extra"].replace("万热度", "").replace("万领域热度", ""))})
                hot_item.update({"date": date})
                self.add(Hot(hot_item))
                # self.hot_list.append(hot_item)
                hot_item={}
            # 保存数据json文件


        except Exception as e:
            print(e)



if __name__ == "__main__":
    cookie="itc_center_user=7bb5oZNpFoH2jZFHWQBEFrC93w%2BN36Q%2BEUuhBLWckLPNsBWpGTmm46cjIdKVRUCOMS8uBX8N7AeVBR1Ts8fQEZ34djhuBMWsU5zEjD6Z4XGX3QzJSU%2FIJF%2FUZI4CVzAlPvYlYmA3vsN02Zo%2FeN9ew0ByBtH3hX9XuOrFmPeCNNTNOPaXDPABE7LY4jdOVo9AWCtgZB4HlFWrMzS9rf7562ZZy8mzx1t1RJBK6xqdzAAL; Hm_lvt_3b1e939f6e789219d8629de8a519eab9=1623915055,1623915092,1623918426,1623918891; Hm_lpvt_3b1e939f6e789219d8629de8a519eab9=1623918899"
    ts = hotspider(cookie)
    dates=pd.date_range('2021-05-22','2021-06-18')

    for date in dates[:len(dates)]:

        date=str(date)[0:11]
        if date[8]=='0':
            date=date[0:8]+date[9:]
        print("执行到"+date)
        # time.sleep(random.choice([0.5, 1, 5, 10]))
        ts.update_hot_class(date)
    print(ts.hot_list)