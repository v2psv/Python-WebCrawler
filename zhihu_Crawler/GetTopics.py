#coding=utf-8

import requests
import json
import urllib2
import sys, gzip, StringIO
import copy
import Queue
import threading
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

THREAD_NUM = 20
mutex = threading.Lock()

class LabelsAndTopics():
    def __init__(self):
        self.label_list, self.topic_list = [], []
        self.label_num, self.topic_num = {}, {}
        self.headers = {'Host':'www.zhihu.com',
                        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
                        'Cookie':'_za=871ac97f-7daf-4206-92e5-772427214f8a; cap_id="YjRjMDFmNTlhYTA2NGVjN2FkMDY1ZjdlZmM0YjgyZmQ=|1436777101|7871a743c32dfdf4380d05720ebb3a187a66cacc"; _ga=GA1.2.1480612025.1435405027; q_c1=244ab18a37df4415a985b301ad94020f|1438059173000|1435405031000; _xsrf=ab79ee4d4c7e2694774f0363077383fb; __utmt=1; __utma=51854390.1480612025.1435405027.1438664773.1438670375.18; __utmb=51854390.11.9.1438670431532; __utmc=51854390; __utmz=51854390.1438664773.17.10.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/topic/19674181; __utmv=51854390.000--|2=registration_date=20131128=1^3=entry_date=20150627=1'
                        }
        self.json_form_data = "method=next&params=%7B%22topic_id%22%3Athis_is_topic_id%2C%22offset%22%3Athis_is_offset%2C%22hash_id%22%3A%22%22%7D&_xsrf=ab79ee4d4c7e2694774f0363077383fb"

    def getLabels(self):
        session = requests.Session()
        response = session.get("http://www.zhihu.com/topics", headers = self.headers)
        soup = BeautifulSoup(response.text)
        li_tag_list = soup.find_all('li')
        for li in li_tag_list:
            if not li.has_attr('data-id'):
                continue
            label_id, label_title = li['data-id'], li.a.contents[0]
            self.label_list.append((label_id, label_title))
        self.label_num["all"] = len(self.label_list)
        self.label_list = list(set(self.label_list))
        self.label_num["no_repeat"] = len(self.label_list)

    def getTopics(self):
        for label in self.label_list:
            data = self.json_form_data.replace("this_is_topic_id", label[0])
            for i in range(0, 80, 20):
                data = data.replace("this_is_offset", str(i))
                ajax_Response = self.request_ajax_data("http://www.zhihu.com/node/TopicsPlazzaListV2", data)
                msg_text = ''.join(ajax_Response['msg'])
                soup = BeautifulSoup(msg_text)
                div_tag_list = soup.find_all('div', 'blk')
                for div in div_tag_list:
                    topic_id, topic_title = div.a['href'].split('/')[-1], div.a.strong.contents[0]
                    if len(div.p.contents) != 0:
                        topic_disc = div.p.contents[0]
                    else:
                        topic_disc = ''
                    self.topic_list.append((topic_id, topic_title, topic_disc))
        self.topic_num['all'] = len(self.topic_list)
        self.topic_list = list(set(self.topic_list))
        self.topic_num['no_repeat'] = len(self.topic_list)

    def getTopicsMultiThread(self):
        thread_list = []
        label_queue = Queue.Queue()
        for label in self.label_list: label_queue.put(label)
        for i in range(THREAD_NUM):
            thread_list.append(threading.Thread(target = self.threadFunc, args = [label_queue]))
        for i in thread_list:
            i.start()
        for i in thread_list:
            i.join()
        self.topic_num['all'] = len(self.topic_list)
        self.topic_list = list(set(self.topic_list))
        self.topic_num['no_repeat'] = len(self.topic_list)

    def threadFunc(self, label_queue):
        while not label_queue.empty():
            label = label_queue.get()
            data = self.json_form_data.replace("this_is_topic_id", label[0])
            for i in range(0, 1000, 20):
                data = data.replace("this_is_offset", str(i))
                while True:
                    try:
                        ajax_Response = self.request_ajax_data("http://www.zhihu.com/node/TopicsPlazzaListV2", data)
                        break
                    except Exception, e:
                        print "Got a Exception, continue..."
                        continue
                msg_text = ''.join(ajax_Response['msg'])
                soup = BeautifulSoup(msg_text)
                div_tag_list = soup.find_all('div', 'blk')
                for div in div_tag_list:
                    topic_id, topic_title = div.a['href'].split('/')[-1], div.a.strong.contents[0]
                    if len(div.p.contents) != 0:
                        topic_disc = div.p.contents[0]
                    else:
                        topic_disc = ''
                    if mutex.acquire():
                        self.topic_list.append((topic_id, topic_title, topic_disc))
                        mutex.release()

    def request_ajax_data(self, url, data):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        req.add_header('Host', 'www.zhihu.com')
        req.add_header('Origin', 'http://www.zhihu.com')
        req.add_header('Referer', 'http://www.zhihu.com/topics')
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36')
        req.add_header('X-Requested-With','XMLHttpRequest')

        response = urllib2.urlopen(req, data)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO.StringIO(response.read())
            jsonText = gzip.GzipFile(fileobj=buf).read()
        else:
            jsonText = response.read()
        return json.loads(jsonText)

def storeDataToText(label_list, topic_list):
    file = open("Titles.txt", "w+")
    for label in label_list:
        file.write("%-6s" % label[0] + "\t" + label[1] + "\n")
    file.close()
    file = open("Topics.txt", "w+")
    for topic in topic_list:
        file.write(topic[0].encode('utf-8') + "\t" + topic[1].encode('utf-8') + "\t" + topic[2].encode('utf-8') + "\n")
    file.close()

if __name__ == "__main__":
    x = LabelsAndTopics()
    x.getLabels()
    # x.getTopics()
    x.getTopicsMultiThread()
    print "all labels num:", x.label_num['all']
    print "labels num without-repeat:", x.label_num['no_repeat']
    print "all topics num:", x.topic_num['all']
    print "topics num without-repeat:", x.topic_num['no_repeat']
    storeDataToText(x.label_list, x.topic_list)