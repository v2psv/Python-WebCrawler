#coding=utf-8

import requests
import json
import sys
import time
import Queue
import multiprocessing
reload(sys)
sys.setdefaultencoding('utf8')

PROCESS_NUM = 30
ROOT_TOPIC = ('19776749', '根话题', '')

class Topics():
    def __init__(self):
        self.topic_result_queue = multiprocessing.Queue()
        self.topic_queue = multiprocessing.Queue()
        self.topic_queue.put(ROOT_TOPIC)
        self.topic_num = 0
        self.url = "http://www.zhihu.com/topic/19776749/organize/entire"
        self.headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.zhihu.com',
        'Origin': 'http://www.zhihu.com',
        'Referer': 'http://www.zhihu.com/topic/19776749/organize/entire',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Length': 38,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36',
        'Cookie': ''
        }
        self.data = {'_xsrf': ''}
        self.proxies = {}

    def getTopicsMultiProcess(self):
        process_list = []
        process_list.append(multiprocessing.Process(target = self.getTopicNumber))
        for i in range(PROCESS_NUM):
            process_list.append(multiprocessing.Process(target = self.processFunc))
        for i in process_list:
            i.start()
        for i in process_list:
            i.join()
        self.topic_num = self.topic_result_queue.qsize()

    def getTopicNumber(self):
        time.sleep(5)
        while not self.topic_queue.empty():
            print "queue size: ", self.topic_queue.qsize(), "\tlist size: ", self.topic_result_queue.qsize()
            time.sleep(3)

    def processFunc(self):
        while not self.topic_queue.empty():
            topic = self.topic_queue.get()
            if topic[0] == '19776749':
                params = {}
            else:
                params = {'child': topic[2], 'parent': topic[0]}
            try:
                ajax_Response = requests.post(self.url, params = params, data = self.data, headers = self.headers, proxies = self.proxies)
            except Exception, e:
                print "Got a Exception, continue...", e
                self.topic_queue.put(topic)
                continue
            # print ajax_Response.text
            try:
                msg_list = json.loads(ajax_Response.text)['msg'][1]
            except Exception, e:
                print "Got a Exception, continue...", e
                continue
            for msg in msg_list:
                if msg[0][0] == 'topic':
                    topic_title, topic_id = msg[0][1], msg[0][2]
                    self.topic_result_queue.put((topic_id, topic_title))
                    if len(msg[1]) != 0:
                        if msg[1][0][0][0] == 'load':
                            child, parent, title = '', msg[1][0][0][3], topic_title
                            self.topic_queue.put((parent, title, child))
                        else:
                            print "Not 显示子话题, message type:" + msg[0][0]
                elif msg[0][0] == 'load':
                    child, parent, title = msg[0][2], msg[0][3], topic[1]
                    self.topic_queue.put((parent, title, child))
                else:
                    print "Not 加载更多, message type:" + msg[0][0]

def storeDataToText(topic_result_queue):
    file = open("Topics.txt", "w+")
    while not topic_result_queue.empty():
        topic = topic_result_queue.get()
        file.write(topic[0].encode('utf-8') + "\t" + topic[1].encode('utf-8') + "\n")
    file.close()

if __name__ == "__main__":
    x = Topics()
    x.getTopicsMultiProcess()
    print "all topics num:", x.topic_num
    storeDataToText(x.topic_result_queue)