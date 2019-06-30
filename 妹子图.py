# -*- coding:utf-8 -*-
import requests
import threading
import re
import time
import os



all_urls = []   # 我们拼接好所有分页的url
all_img_urls = [] # 所有页面里的（就是all_urls[] 里的 每个页面的，图片点开后的每个系列图片的url) 图片列表链接
g_lock = threading.Lock() #声明一个锁
pic_links = []    #储存所有图片的地址

headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 '
        +'(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Host':'www.meizitu.com'
    }

class Spider():
    def __init__(self, target_url, headers):       # target_url   目标url
        self.target_url = target_url
        self.headers = headers



    def getUrls(self, start_page, page_num):
        global all_urls
        for i in range(start_page, page_num+1):
            url = self.target_url % i
            all_urls.append(url)


class Producer(threading.Thread):

    def run(self):


        while  len(all_urls)>0:
            g_lock.acquire()    # 在访问all_urls 的时候，需要用到锁机制
            page_url = all_urls.pop()   # 用pop方法移除最后一个元素，并且返回该值   获取了每一个页面的url
            print(page_url)
            g_lock.release()

            try:
                print("分析:" + page_url)
                response = requests.get(page_url, headers = headers, timeout = 3)
                all_pic_link = re.findall('<a target=\'_blank\' href="(.*?)">',response.text,re.S) #原来是 '<a target="_blank" href="(.*?)">' 这里要加''
                global all_img_urls
                g_lock.acquire()
                all_img_urls += all_pic_link  # 将所有的all_pic_link 拼接起来
                print(all_img_urls)
                g_lock.release()
                time.sleep(0.5)
            except:
                pass


# 下面创建一个消费者/观察者，不断关注刚才获取的图片详情页面的数组


class Consumer(threading.Thread):
    def run(self):
        global all_img_urls # 导入图片详情页面的数组
        print("线程 %s 正在运行" % threading.current_thread().name)
        while(len(all_img_urls) > 0):
            g_lock.acquire()
            img_url = all_img_urls.pop()
            g_lock.release()

            try:
                response = requests.get(img_url, headers = headers)
                response.encoding='gb2312'        # 调用的页面编码是gb2312，这里需要转换一下编码
                title = re.search('<title>(.*?) | 妹子图</title>', response.text).group(1)   # 返回匹配到的第一个
                all_pic_src = re.findall('<img alt=.*? src="(.*?)"></br>', response.text, re.S)   # 匹配的是每张图片的链接  这里应该是有很多链接

                pic_dict = {title:all_pic_src}     #声明字典， key为title， value 为图片链接
                global pic_links       # 导入最初声明的储存所有图片链接的列表
                g_lock.acquire()
                pic_links.append(pic_dict)     # 这是一个列表， 列表的每个值是一个字典,字典分为 key和values
                print(title + "获取成功")
                g_lock.release()
            except:
                pass
            time.sleep(1)


# 下面写一个下载类
class DownPic(threading.Thread):
    def run(self):
        while True:          #写成死循环，检测图片链接数组是否更新
            global pic_links       # 导入储存所有图片链接的数组
            # 先上锁，锁住
            g_lock.acquire()
            if len(pic_links) == 0:
                g_lock.release()
                continue
            else:
                pic = pic_links.pop()
                g_lock.release()
                for key, values in pic.items():
                    path = key.rstrip("//")   #删除开头的/
                    pos = "图片保存位置"
                    is_exists = os.path.exists(pos+"//"+path)

                    if not is_exists:
                        # 如果目录不存在 ，创建目录，
                        os.makedirs(pos+"//"+path)
                        print(pos+"//"+path, "创建成功")

                    else:
                        print(pos+"//"+path, "已经存在")

                    for pic in values :
                        filename = pos+"//"+path+"/"+pic.split('/')[-1]
                        if os.pos+"//"+path.exists(filename):
                            continue
                        else:
                            try:
                                response = requests.get(pic, headers=headers)
                                with open(filename, 'wb') as f:
                                    f.write(response.content)
                                    f.close()
                            except Exception as e:
                                print(e)
                                pass






if __name__ == '__main__':

    threads = []

    target_url = 'http://www.meizitu.com/a/pure_%d.html'  #图片集和列表规则
    spider = Spider(target_url, headers)
    spider.getUrls(1, 2)
    for x in range(2):
        t = Producer()
        t.start()          # 可以调用 自己实现的fun方法， 但是不会多线程运行
        threads.append(t)

    for tt in threads:
        tt.join()
    print("进行到我这里了")

    for x in range(10):
        ta = Consumer()
        ta.start()

    for x in range(1):
        down = DownPic()
        down.start()

