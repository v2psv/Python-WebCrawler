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

def set_proxy():
    proxy = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)


def parse_urls(web_page, url_queue):
    soup = BeautifulSoup(web_page, "html.parser")
    span_list = soup.find_all('span', 'photoThum')

    for span in span_list:
        url_queue.put(span.a['href'].encode('utf8'))

    print('%d urls extracted' % url_queue.qsize())


def get_urls(root_url, url_queue):
    request = urllib2.Request(root_url, headers=header)
    content = urllib2.urlopen(request).read()
    print('root webpage downloaded')
    parse_urls(content, url_queue)
    header['Refer'] = root_url


def get_image(url_queue, folder, mutex):
    while not url_queue.empty():
        if mutex.acquire():
            url = url_queue.get()
            mutex.release()

        name = os.path.basename(url)
        # data = requests.get(url, headers=header)
        # img = Image.open(StringIO.StringIO(data.content))
        request = urllib2.Request(url, headers=header)
        img = urllib2.urlopen(request, timeout=5).read()
        save_img(img, name, folder)
        print('saved ' + name)
        # time.sleep(0.5)


def save_img(img, name, folder):
    with open(os.path.join(folder, name), "wb") as f:
        f.write(img)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("at list 1 parameter should be provided! (root_url, save_dir, num_jobs)")
    root_url = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) == 3 else 'images'
    num_jobs = sys.argv[3] if len(sys.argv) == 4 else 10
    print('root url: ' + root_url)

    if not os.path.exists(folder):
        os.makedirs(folder)

    url_queue = Queue.Queue()
    # set_proxy()
    get_urls(root_url, url_queue)

    thread_list = []
    for i in range(num_jobs):
        t = threading.Thread(target=get_image, args=(url_queue, folder, threading.Lock()))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()


