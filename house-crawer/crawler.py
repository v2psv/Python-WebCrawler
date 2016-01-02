#coding=utf-8

import requests
import json
import urllib2
import time
import sys, gzip, StringIO
import Queue
import threading
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

THREAD_NUM = 200
mutex = threading.Lock()

class Crawler():
    def __init__(self):
        self.pageID_list, self.info_list = range(1, 1304), []
        self.pageID_queue = Queue.Queue()
        for pageID in self.pageID_list: self.pageID_queue.put(pageID)
        self.info_num = 0
        self.headers = {'Host':'map.sogou.com',
                        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'
                        }
        self.url_model = "http://map.sogou.com/index/shanghai/8_6_pageID.html"

    def getInfoMultiThread(self):
        thread_list = []
        thread_list.append(threading.Thread(target = self.getInfoNumber))
        for i in range(THREAD_NUM):
            thread_list.append(threading.Thread(target = self.threadFunc, args = [self.pageID_queue]))
        for i in thread_list:
            i.start()
        for i in thread_list:
            i.join()
        self.info_num = len(self.info_list)

    def getInfoNumber(self):
            time.sleep(5)
            while not self.pageID_queue.empty():
                print "queue size: ", self.pageID_queue.qsize(), "\tlist size: ", len(self.info_list)
                time.sleep(3)

    def threadFunc(self, pageID_queue):
        title, address, phone = '', '', ''
        while not pageID_queue.empty():
            pageID = pageID_queue.get()
            try:
                url = self.url_model.replace("pageID", str(pageID))
                request = urllib2.Request(url)
                content = urllib2.urlopen(request).read()

                soup = BeautifulSoup(content, "html.parser")
                div_list = soup.find_all('div', 'poiItem')
                for div in div_list:
                    title, address, phone = '', '', ''
                    div.find('div', 'floatlayer').extract()
                    # print div
                    subDiv = div.find_all('div')
                    title = subDiv[0].a.contents[0].strip()
                    if len(subDiv) >= 2:
                        address = subDiv[1].contents[0].strip()
                    if len(subDiv) >= 3:
                        phone = subDiv[2].contents[0].strip()
                    # print title, address, phone
                    if mutex.acquire():
                        self.info_list.append((title, address, phone))
                        mutex.release()
            except Exception, e:
                pass
                # print "catch a Exception, re-do later...", url
                # pageID_queue.put(pageID)

def storeDataToText(info_list):
    file = open("Info.txt", "w+")
    for info in info_list:
        file.write(info[0].encode('utf-8') + "\t" + info[1].encode('utf-8') + "\t" + info[2].encode('utf-8') + "\n")
    file.close()

if __name__ == "__main__":
    x = Crawler()
    x.getInfoMultiThread()
    print "all Info num:", x.info_num
    storeDataToText(x.info_list)
