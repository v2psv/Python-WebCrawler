#-*- coding: utf-8 -*-

import time
import Queue
import threading
import requests
from bs4 import BeautifulSoup

THREAD_NUM = 10
PAGES_PER_TAG = 10

class Book:
	def __init__(self):
		self.tag_list = []
		self.tag_queue = Queue.Queue()
		self.tag_url = "http://book.douban.com/tag/?view=cloud"
		self.book_url = "http://www.douban.com/tag/this_is_tag/book"
		self.headers1 = {
			'Host':'book.douban.com',
			'Connection':'keep-alive',
			'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
			'Referer':'http://book.douban.com/tag/?view=type&icn=index-sorttags-all',
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
			'Cookie':'bid="U5k+t1Oea4U"; ll="108296"; push_noty_num=0; push_doumail_num=0; ps=y; ap=1; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1439183313%2C%22http%3A%2F%2Fwww.douban.com%2F%22%5D; __utmt_douban=1; __utmt=1; _pk_id.100001.3ac3=303b99e5664ea9f0.1439179156.2.1439184790.1439179283.; _pk_ses.100001.3ac3=*; __utma=30149280.318137177.1438926241.1439179150.1439183313.7; __utmb=30149280.12.10.1439183313; __utmc=30149280; __utmz=30149280.1438926241.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=30149280.12292; __utma=81379588.1359695583.1439179155.1439179155.1439183313.2; __utmb=81379588.10.10.1439183313; __utmc=81379588; __utmz=81379588.1439179155.1.1.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/'
			}
		self.headers2 = {
			'Host':'www.douban.com',
			'Connection':'keep-alive',
			'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
			'Cookie':'bid="U5k+t1Oea4U"; ll="108296"; push_noty_num=0; push_doumail_num=0; ps=y; _pk_id.100001.8cb4=ae3aa95b83ce68de.1438926236.5.1439186874.1439179318.; __utma=30149280.318137177.1438926241.1439179150.1439183313.7; __utmc=30149280; __utmz=30149280.1438926241.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=30149280.12292; ap=1'
			}

	def getTags(self):
		response = requests.get(self.tag_url, headers = self.headers1)
		soup = BeautifulSoup(response.content, "html.parser")
		div = soup.find('div', {'class':"indent tag_cloud"})
		for tag in div.find_all('a'):
			self.tag_queue.put(tag.contents[0].strip().encode('utf8'))
			self.tag_list.append(tag.contents[0].strip().encode('utf8'))
		open("books/Book_tags.txt", "w+").write('Tags number: ' + str(len(self.tag_list)) + '\n' + '\n'.join(self.tag_list))

	def getBooks(self):
		self.finished = 0
		thread_list = []
		for i in range(THREAD_NUM):
			thread_list.append(threading.Thread(target = self.threadFunc))
		thread_list.append(threading.Thread(target = self.getTagsRemainCount))
		for t in thread_list:
			t.start()
		for t in range(THREAD_NUM):
			thread_list[t].join()
		self.finished = 1

	def getTagsRemainCount(self):
		size = tag_queue_size = self.tag_queue.qsize()
		print "%d tags remained..." % size
		while not self.tag_queue.empty():
			if self.finished == 1:
				return
			if size != tag_queue_size:
				print "%d tags remained..." % size
				tag_queue_size = size
			time.sleep(1)
			size = self.tag_queue.qsize()

	def threadFunc(self):
		while not self.tag_queue.empty():
			tag = self.tag_queue.get()
			book_list = []
			url = self.book_url.replace("this_is_tag", tag)
			for i in range(PAGES_PER_TAG):
				params = {'start': i * 15}
				response = requests.get(url, params = params, headers = self.headers2)
				soup = BeautifulSoup(response.content, "html.parser")
				div = soup.find('div', {'class': 'mod book-list'})
				for info in div.find_all('dd'):
					book_id, book_title, book_desc, book_rate = '', '', '', '0.0'
					try:
						book_id = info.a['href'].split('/')[-2].encode('utf8')
						book_title = info.a.contents[0].strip().encode('utf8')
						try:
							book_desc = info.find('div', {'class':'desc'}).contents[0].strip().encode('utf8')
							book_rate = info.find('span', {'class':'rating_nums'}).contents[0].encode('utf8')
						except:
							pass
					except Exception, e:
						print e
					book_list.append((book_rate, book_id, book_title, book_desc))
			open("books/"+tag+".txt", "w+").write('Book number: ' + str(len(book_list)) + '\n' + '\n'.join(['\t'.join(b) for b in book_list]))

if __name__ =='__main__':
	b = Book()
	b.getTags()
	b.getBooks()