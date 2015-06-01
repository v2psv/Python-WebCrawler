#coding=utf-8

import requests
import json
import sys
import time
import Queue
import multiprocessing
from multiprocessing.managers import BaseManager
reload(sys)
sys.setdefaultencoding('utf8')

PROCESS_NUM = 50
ROOT_TOPIC = ('19776749', '根话题', '')

server_addr = '202.121.97.58'
server_port = 65501

topic_queue = Queue.Queue()
result_queue = Queue.Queue()

result_file = open("Topics.txt", "w+")

class QueueManager(BaseManager):
    pass

class Topics():
    def __init__(self, shared_topic_queue, shared_result_queue):
        self.topic_queue = shared_topic_queue
        self.result_queue = shared_result_queue
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
        'Cookie': '_za=14fe9eab-d51d-4379-9607-31270e63ec25; q_c1=6bccb028cae4483a8cbd2795f8daa416|1438765518000|1438765518000; cap_id="MjVjMzVmM2FhOGNkNDZkZjg2ODQyYWJkY2UyYjFlODg=|1438765518|22b4f82d063435631a2d101b581c6188412dc273"; z_c0="QUFCQXRYVWhBQUFYQUFBQVlRSlZUUjFmNlZYb0hLb2g2bkJJWFNtU0F4ZERiOER0ODhrOHpnPT0=|1438765597|683408bcd06a19f0c5a82d91d42ae5cf5abd41af"; _xsrf=8bdcd63ab4067b7333014291061c16c8; tc=AQAAAAq4IGQrwgcAhU33dF7s7az9S4Yw; __utmt=1; __utma=51854390.1588842541.1438765496.1438765496.1438827188.2; __utmb=51854390.8.10.1438827188; __utmc=51854390; __utmz=51854390.1438827188.2.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=51854390.100-1|2=registration_date=20131128=1^3=entry_date=20131128=1'
        }
        self.data = {'_xsrf': '8bdcd63ab4067b7333014291061c16c8'}

    def getTopicsMultiProcess(self):
        process_list = []
        process_list.append(multiprocessing.Process(target = self.getTopicNumber))
        process_list.append(multiprocessing.Process(target = self.writeResult))
        for i in range(PROCESS_NUM):
            process_list.append(multiprocessing.Process(target = self.processFunc))
        for i in process_list:
            i.start()
        for i in process_list:
            i.join()
        self.topic_num = self.result_queue.qsize()

    def getTopicNumber(self):
        time.sleep(5)
        while not self.topic_queue.empty():
            print "queue size: ", self.topic_queue.qsize(), "\tlist size: ", self.result_queue.qsize()
            time.sleep(3)

    def writeResult(self):
        global result_file
        time.sleep(5)
        while True:
            topic = self.result_queue.get()
            result_file.write(topic[0].encode('utf-8') + "\t" + topic[1].encode('utf-8') + "\n")
            result_file.flush()

    def processFunc(self):
        while not self.topic_queue.empty():
            topic = self.topic_queue.get()
            if topic[0] == '19776749':
                params = {}
            else:
                params = {'child': topic[2], 'parent': topic[0]}
            try:
                ajax_Response = requests.post(self.url, params = params, data = self.data, headers = self.headers)
                msg_list = json.loads(ajax_Response.text)['msg'][1]
            except Exception, e:
                print "Got a Exception, continue...", e
                self.topic_queue.put(topic)
                continue
            for msg in msg_list:
                if msg[0][0] == 'topic':
                    topic_title, topic_id = msg[0][1], msg[0][2]
                    self.result_queue.put((topic_id, topic_title))
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

def storeDataToText(result_queue):
    while not result_queue.empty():
        topic = result_queue.get()
        file.write(topic[0].encode('utf-8') + "\t" + topic[1].encode('utf-8') + "\n")
    file.close()

if __name__ == "__main__":
    QueueManager.register('get_topic_queue', callable = lambda: topic_queue)
    QueueManager.register('get_result_queue', callable = lambda: result_queue)
    manager = QueueManager(address=(server_addr, server_port), authkey='abc')
    manager.start()

    shared_topic_queue = manager.get_topic_queue()
    shared_result_queue = manager.get_result_queue()

    shared_topic_queue.put(ROOT_TOPIC)

    x = Topics(shared_topic_queue, shared_result_queue)
    x.getTopicsMultiProcess()
    print "all topics num:", x.topic_num
    storeDataToText(x.result_queue)