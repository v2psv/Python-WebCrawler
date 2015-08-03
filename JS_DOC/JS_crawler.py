#-*- coding:utf8 -*-

import urllib, urllib2
import copy
import gzip, StringIO
import Queue
import threading
import time
from sgmllib import SGMLParser

THREAD_NUM = 20
LINKS_QUEUE = Queue.Queue()

class GetLinks(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.links_queue = LINKS_QUEUE
        self.link = ''
        self.title = ''
        self.path = ''
        self.status = 0

    def start_li(self, attrs):
        if self.status == 0 and ("data-default-state", "closed") in attrs:
            self.status = 1
        elif self.status == 1:
            self.status = 2

    def start_a(self, attrs):
        if self.status == 2:
            self.link = attrs[0][1]
            self.status = 3

    def handle_data(self, data):
        if self.status == 3:
            try:
                self.title = data.decode('utf-8').encode('gbk')
            except UnicodeEncodeError:
                pass
            self.status = 4

    def end_li(self):
        if self.status == 4:
            self.path = "JS/data/" + self.link.split('/')[-1] + ".html"
            self.links_queue.put({"title":self.title, "link":self.link, "path":self.path})
            self.title = ''
            self.link = ''
            self.path = ''
            self.status = 1
        elif self.status == 1:
            self.status = 0

class DownloadPageThread(threading.Thread):
    def __init__(self, links_queue):
        threading.Thread.__init__(self)
        self.links_queue = links_queue

    def run(self):
        threadname = self.getName()
        while not self.links_queue.empty():
            link = self.links_queue.get()
            urllib.urlretrieve('https://developer.mozilla.org' + link["link"], link["path"])
            print(link["path"] + '\t' + link['link'])

class DownJSDocument(object):
    def __init__(self):
        self.threads = []
        self.main_page = ''

    def getAllLinks(self):
        url = "https://developer.mozilla.org/zh-CN/docs/Web/JavaScript"
        # headers = {'Host': 'developer.mozilla.org',
        #             'Connection': 'keep-alive',
        #             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36 QQBrowser/9.0.2229.400',
        #             'Accept-Encoding': 'gzip, deflate, sdch',
        #             'Accept-Language': 'zh-CN,zh;q=0.8',
        #             'Cookie': '_gat=1; dwf_helpfulness=False; _ga=GA1.2.742419394.1438565172',
        #             'If-None-Match': "d90498e9a13c6b8d191f324e73108b4c6fdfd4d3"
        #           }
        # req = urllib2.Request(url, headers=headers)
        # response = urllib2.urlopen(req)
        response = urllib.urlopen(url)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO.StringIO(response.read())
            htmldata = gzip.GzipFile(fileobj=buf).read()
        else:
            htmldata = response.read()
        # file = open("JavaScript _ MDN.html", "r")
        # htmldata = file.read()
        # file.close()
        self.main_page = htmldata
        get_links = GetLinks()
        get_links.feed(htmldata)

    def downloadPages(self):
        shared_queue = copy.copy(LINKS_QUEUE)
        for i in range(THREAD_NUM):
            self.threads.append(DownloadPageThread(shared_queue))
        for i in self.threads:
            i.start()
        for i in self.threads:
            i.join()

    def handleStartPage(self):
        links_queue = LINKS_QUEUE
        while not links_queue.empty():
            link = links_queue.get()
            self.main_page.replace("\"" + link["link"] + "\"", "\"" + link["path"] + "\"")

        file = open("JS/JS_document.html", "w+")
        file.write(self.main_page)
        file.close()

def main():
    start = time.time()
    robot = DownJSDocument()
    robot.getAllLinks()
    print("Download start page accomplished...")
    print("Get links accomplished...")
    print "Queue size:", LINKS_QUEUE.qsize()
    print("Downloading pages(maybe take a long time)...")
    robot.downloadPages()
    print("Download pages accomplished...")
    robot.handleStartPage()
    end = time.time()
    print end - start

if __name__ == "__main__":
    main()

