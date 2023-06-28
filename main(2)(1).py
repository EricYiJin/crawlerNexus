import os
import sys
import requests
from requests.models import Response
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

'''
    把代码改成多线程，用 queue
'''
class Main:
    url = "https://www.austlii.edu.au"
    def __init__(self) -> None:
        self.init()

    def init(self) -> None:
        self.ua = UserAgent()
        self.database_q: Queue = Queue()

    # 获取数据库目录
    def databaseGet(self) -> None:
        res: Response = requests.get(url=self.url+"/databases.html")
                                     #headers={"User-Agent": self.ua})
        if res.status_code != 200:
            sys.exit(0)
        data = self.databaseClean(res)
        for i in data:
            self.database_q.put(i)
        
    def databaseClean(self, res: Response) -> list:
        res.encoding = "u8"
        soup = BeautifulSoup(res.text, "html.parser")
        result = []
        for div in soup.find_all("div", class_="card"):
            for li in div.find_all("li"):
                a = li.find("a")
                if a == None:
                    continue
                result.append([a.text, self.url+a.get("href")])
        return result
    
    # 获取案例页目录
    def getDatabasePage(self, name, url) -> None:    # 判断页面是哪种类型
        source_url = url
        html = requests.get(url).text
        if "Specific Year" in html:
            return self.SpecificYearPage(html, source_url)
        # if "for the years" in html or "for the Years" in html:
            # return self.forTheYears(html, source_url)
        print("未知页面类型：", name)
        return None

    def SpecificYearPage(self, html: str, source_url) -> list:
        soup = BeautifulSoup(html, "html.parser")
        # 是否能按年份分类？
        year_box = soup.find("div", class_="year-options-list")
        if len(year_box.find_all("li")) in [0, 1]: # 只有 any 一类
            return self.SpecificByLetter(html)
        result = []
        for i in year_box.find_all("li")[1:]:
            a = i.find("a")
            result.append([a.text, source_url+a.get("href")])
        return result
    
    def SpecificByLetter(self, html: str, source_url: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        letter_box = []
        id_s = soup.find("div", {"id", "panel-letter"})
        if len(id_s) in [0, 1]:
            print("未找到首字母标签")
            return None
        for i in id_s[1:]:
            a = i.find("a")
            letter_box.append([a.text, source_url+a.get("href")])
        return letter_box

    def getInfo(self, html: str) -> None:
        pass
    
    '''
    def forTheYears(self, html: str, source_url: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        year_list = []
        block = soup.find_all("blockquote")[0]
        for a in block.find_all("a"):
            year_list.append([a.text, source_url+a.get("href")])
        return year_list
    '''

    # 下载页面
    def contextGet(self, url) -> list:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        result = []
        for div in soup.find_all("div", class_="all-section"):
            for li in div.find_all("li"):
                a = li.find("a")
                result.append([a.text, self.url+a.get("href")])
        return result
    
    def getPage(self, path, data: list) -> None:
        try:
            os.makedirs(path)
        except:
            pass
        for name, url in data:
            res = requests.get(url, headers={"User-Agent": self.ua.chrome})
            with open(os.path.join(path, name+".html"), "w") as f:
                f.write(res.text)
            print(name)
    
    def run(self) -> None:
        data = self.databaseGet()   # 获取所有数据库
        print("共找到 <{}> 个数据库".format(len(data)))
        # 进入每一个数据库
        for db_name, db_url in data:
            # 获取案例页目录
            db_name = "aaa"; db_url = "https://www.austlii.edu.au/au/other/rulings/ato/ATODMTR/"
            d = self.judgePage(db_name, db_url)
            for filename, url in d:
                result_d = self.contextGet(url)
                self.getPage(os.path.join(db_name, filename), result_d)

if __name__=="__main__":
    self = Main()
    self.run()
    # data = self.databaseGet()
    # line = data[0]
    # result = self.judgePage(*line)
    # for i in result:
    #     path = os.path.join(line[0], i[0])