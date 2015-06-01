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

server_addr = '202.121.97.58'
server_port = 65501

class QueueManager(BaseManager):
    pass

cookies = ['tc=AQAAAJIwEghtngkAhU33dLXdPmkpSeUP; q_c1=f9d7904553384c13814f7707393e5df8|1438844760000|1438844760000; cap_id="OTI5Mjc4YjU1OGE5NGU1MmFmZmYwMjVjMjg2Zjk3NTA=|1438844760|a5800a5f39ab46ddfae9e2132a0e0805e77f0448"; __utmt=1; _za=019d35c7-8549-4a25-823f-b6d533d995f0; z_c0="QUFCQXRYVWhBQUFYQUFBQVlRSlZUWVdVNmxVNTFYZUpiNExnejh5NDNVcl9fOGFRNUlWUmtRPT0=|1438844805|816b97805fe7646809f13fcff9683f7c1069cef1"; unlock_ticket="QUFCQXRYVWhBQUFYQUFBQVlRSlZUWTBPdzFXMU1NeF9Zb2RkZmtXcWxoZERIWHFBQ29ob013PT0=|1438844805|b9aeebf67db51b866d57360623b86520d3da155b"; _xsrf=55593f940934e4991fe46e8a1de241e4; __utma=51854390.428674616.1438844762.1438844762.1438844762.1; __utmb=51854390.6.10.1438844762; __utmc=51854390; __utmz=51854390.1438844762.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=51854390.100-1|2=registration_date=20131128=1^3=entry_date=20131128=1',
           '_za=df0eb025-112d-4acf-9e9a-0626e260835b; cap_id="MjU2NDBmYzIzMTQ1NDcxMzllNmVlZDgwOGYzZGYwNjc=|1436421777|5a75e8e81511b295a5f7978fab9bb0a9e5f5fd9a"; _ga=GA1.2.261979713.1435732675; tc=AQAAAPDNqQnrtAIA+psW0kkGL2FNN2Tu; q_c1=a3be575b706241558c59b013385a4e00|1438913158000|1435732673000; __utmt=1; z_c0="QUFCQXRYVWhBQUFYQUFBQVlRSlZUWnFmNjFYdGxvSjdNQmJrZU5NMzN6Y3RtLTUxdlotUUZRPT0=|1438913178|6ea33ef7b878ab54e8420e0684fc137b9d0d4911"; unlock_ticket="QUFCQXRYVWhBQUFYQUFBQVlRSlZUYUlaeEZYQ2JBSHlhTms4RlVyX1VONm9Da0JtNWhsTEV3PT0=|1438913178|6328636adae8c022f83e9f3f60966149a0596121"; _xsrf=67f84ac843a2e170ca12f69de3b9c8c1; __utma=51854390.261979713.1435732675.1436421778.1438913164.7; __utmb=51854390.4.10.1438913164; __utmc=51854390; __utmz=51854390.1435811749.5.5.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=51854390.100-1|2=registration_date=20131128=1^3=entry_date=20131128=1',
           'tc=AQAAAOr00y+ZGQ8AhU33dGaDCRZAyFUr; q_c1=2a8a1c3231364f419f9e8992c684ddca|1438913304000|1438913304000; cap_id="OTk1MGExMzBkYzQwNDQwNGJhZDU4ZjZiZWQ1MTg4NDE=|1438913304|e65c11e14d9e541f3c53d16466b71139ca99b4af"; __utmt=1; _za=7c861d56-b886-4e60-bc04-7c81aa2139eb; z_c0="QUFCQXRYVWhBQUFYQUFBQVlRSlZUU21nNjFYZmd5Qjg3OEpZSEljelMtU1dFdnhSMklWLTZnPT0=|1438913321|963e2d5b7e8da8bb77dab7305fe5a8c3e1b4208f"; unlock_ticket="QUFCQXRYVWhBQUFYQUFBQVlRSlZUVEVheEZXWF9pa19fcGlyWVVmZDVyQ2pKTjFvb1B4LTNnPT0=|1438913321|4c4d2bd2dde7200496839ebe7fb09c0519877f09"; _xsrf=7220fea455a4394b787e83299a41408e; __utma=51854390.2142986390.1438913309.1438913309.1438913309.1; __utmb=51854390.4.10.1438913309; __utmc=51854390; __utmz=51854390.1438913309.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=51854390.100-1|2=registration_date=20131128=1^3=entry_date=20131128=1']
datum = ['55593f940934e4991fe46e8a1de241e4',
         '67f84ac843a2e170ca12f69de3b9c8c1',
         '7220fea455a4394b787e83299a41408e']

class Topics():
    def __init__(self, shared_topic_queue, shared_result_queue):
        self.topic_queue = shared_topic_queue
        self.result_queue = shared_result_queue
        self.topic_num = 0
        self.url = ""
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
        'Cookie': cookies[0]
        }
        self.data = {'_xsrf': datum[0]}

    def getTopicsMultiProcess(self):
        process_list = []
        process_list.append(multiprocessing.Process(target = self.getTopicNumber))
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

if __name__ == "__main__":
    QueueManager.register('get_topic_queue')
    QueueManager.register('get_result_queue')
    manager = QueueManager(address=(server_addr, server_port), authkey='abc')
    manager.connect()

    shared_topic_queue = manager.get_topic_queue()
    shared_result_queue = manager.get_result_queue()

    x = Topics(shared_topic_queue, shared_result_queue)
    x.getTopicsMultiProcess()
    print "all topics num:", x.topic_num
