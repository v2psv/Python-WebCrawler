#coding=utf-8
import requests, json, urllib2
import time, sys, gzip
import threading, Queue, os
from bs4 import BeautifulSoup
from cStringIO import StringIO
from PIL import Image
reload(sys)
sys.setdefaultencoding('utf8')

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.210 Safari/537.36'}
proxies = {
  "http": "60.178.1.61:8081",
  'http': "43.241.225.147:3128"
  }
url_prefix = "http://openaccess.thecvf.com/"
root_url = "http://openaccess.thecvf.com/CVPR2017.py"
folder = 'cvpr2017_accepted_papers'
num_jobs = 10


def set_proxy():
    proxy = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)


def parse_urls(web_page, url_queue):
    soup = BeautifulSoup(web_page, "html.parser")
    span_list = soup.find_all('dt', attrs={"class":"ptitle"})

    for span in span_list:
        url = url_prefix + span.a['href'].replace('html', 'papers', 1).replace('html', 'pdf')
        title = span.text
        url_queue.put((url, title))

    print('%d urls extracted' % url_queue.qsize())


def get_urls(root_url, url_queue):
    request = urllib2.Request(root_url, headers=header)
    content = urllib2.urlopen(request).read()
    print('root webpage downloaded')
    parse_urls(content, url_queue)
    header['Refer'] = root_url


def downloader(url_queue, folder, mutex):
    while not url_queue.empty():
        if mutex.acquire():
            url, title = url_queue.get()
            mutex.release()

        try:
            request = urllib2.Request(url, headers=header)
            pdf = urllib2.urlopen(request, timeout=5).read()

            with open(os.path.join(folder, title+'.pdf'), "wb") as f:
                f.write(pdf)
            print('saved ' + title)
        except:
            url_queue.put((url, title))


if __name__ == "__main__":
    if not os.path.exists(folder):
        os.makedirs(folder)

    url_queue = Queue.Queue()
    # set_proxy()
    get_urls(root_url, url_queue)

    thread_list = []
    for i in range(num_jobs):
        t = threading.Thread(target=downloader, args=(url_queue, folder, threading.Lock()))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()
