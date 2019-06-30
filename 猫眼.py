import requests
from bs4 import BeautifulSoup

url_list = []
all_name = []
all_num  = []
all_actor = []
all_score = []

class Product_url():      # 这个地方传入的url是 https://maoyan.com/board/4?offset=

    global url_list
    def __init__(self, url):
        self.url = url
        for x in range(0, 10):
            one_url = self.url + str(x*10)       # 简单暴力的拼接字符串，储存下top100的是个url 
            url_list.append(one_url)



class Get_one_page():
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def get_response(self):
        response = requests.get(self.url, headers = self.headers)
        return response.text

# 这个类用来 进行抓取
class Spider():


    def __init__(self, html):      
        self.html = html

    global all_name     # 电影名字
    def get_name(self):                     
        soup = BeautifulSoup(self.html, 'lxml')
        for html_name in soup.select('.name'):
            all_name.append(html_name.get_text())

    global all_num    # 所有评分
    def get_num(self):
        soup = BeautifulSoup(self.html, 'lxml')
        for html_num in soup.select('.board-index'):
            all_num.append(html_num.get_text())

    global all_actor     # 演员
    def get_actor(self):
        soup = BeautifulSoup(self.html, 'lxml')
        for html_actor in soup.select('.star'):
            all_actor.append(html_actor.get_text().strip())      #strip() 去除了\n

    global all_score
    def get_score(self):
        soup = BeautifulSoup(self.html, 'lxml')
        for html_score_integer in soup.select('.integer'):    # 网页里评分是分为两部分的，整数和小数
            for html_score_fraction in soup.select('.fraction'):
                all_score.append(html_score_integer.get_text() + html_score_fraction.get_text()) # 把整数和小数部分连接起来


if __name__ == '__main__':
    filename = '猫眼电影top100.txt'
    with open(filename, 'w') as file_object:
        file_object.write("猫眼电影top100")

    file_handle = open('猫眼电影top100.txt', 'a+')
    file_handle.write("\nsadas")

    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 '
        +'(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    a_product = Product_url('https://maoyan.com/board/4?offset=')
    for n in range(0, 10):
        one_page = Get_one_page(url_list[n], headers)
        html = one_page.get_response()

        one_spider = Spider(html)
        one_spider.get_actor()
        one_spider.get_score()
        one_spider.get_num()
        one_spider.get_name()


    for n in range(0, 100):
        num = ' '.join(all_num[n])
        actor = ' '.join(all_actor[n])
        name = ' '.join(all_name[n])
        score = ' '.join(all_score[n])
        file_handle = open('猫眼电影top100.txt', 'a+')
        file_handle.write('\n' +'  ' + num +' ' + name +'  ' + actor + '  ' + score)
        file_handle.close()