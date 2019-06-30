# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pymongo
import time

'''
拉勾网会限制爬取，通常会在爬取第6，7页的时候，遇到无数据返回，可以增加sleep的时候解决
'''

class Spider():

    def __init__(self, url):
        self.start_url = url


    def get_response(self,url):
        headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 '
        +'(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }


        response = requests.get(url, headers = headers)
        print("获取的回复：")
        print(response)
        self.get_item(response.text) # 把获得的结果传递给get_item进行解析

    def get_item(self, response):
        # 现在提取出了所有的，职位，公司，工资，他们三个各自为列表。
        global soup
        soup = BeautifulSoup(response, 'lxml')

        # soup = soup.prettify() #生成树状html代码
        positions = soup.find_all('h3') #这个是所有的职位
        companys  = soup.select('.company_name') # 所有的公司
        '''
        for i in companys:
            print(i.get_text())
        '''
        moneys = soup.select('.money')    # 所有的工资


        self.conduct_item(positions, companys, moneys) # 把获得的三个列表传递给数据处理函数


    def conduct_item(self, positions, companys, moneys,): # 这个是处理数据的函数
        item_list = []
        for i in range(len(positions)):
            item_dict = dict()
            item_dict['position'] = positions[i].string     # 把三个数据传入字典
            item_dict['money'] = moneys[i].get_text()
            item_dict['company'] = companys[i].get_text().strip('\n')

            item_list.append(item_dict)         #字典传入数组


        # print(item_list)
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["demo"]
        mycol = mydb['lagou_item']   # 创建集合，类似mysql的表

        x = mycol.insert_many(item_list)
        # print(x.inserted_ids)

        # 都保存到数据库后，再次判断下一页是否存在，如果存在，重新跑一遍
        next_page = soup.select('.page_no')[-1]['href'] # 获取下一页的url
        if next_page is not None:
            time.sleep(5)
            print("休息了5秒，抓取下一页" + next_page)
            self.get_response(next_page)


    def run(self):
        self.get_response(self.start_url)





if __name__ == "__main__":
    spider = Spider("https://www.lagou.com/zhaopin/Python/?labelWords=label")
    spider.run()