#-*- coding: utf-8 -*-

import requests
import Queue
import threading
from bs4 import BeautifulSoup

THREAD_NUM = 5

class Movie:
	def __init__(self):
		self.task_queue = Queue.Queue()
		list = [self.task_queue.put(t) for t in range(0, 250, 25)]
		self.movie_queue = Queue.Queue()
		self.movie_list = []
		self.url = "http://movie.douban.com/top250"
		self.headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Host': 'movie.douban.com',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'
		}

	def crawler(self):
		thread_list = []
		for i in range(THREAD_NUM):
			thread_list.append(threading.Thread(target = self.threadFunc))
		for i in thread_list:
			i.start()
		for i in thread_list:
			i.join()
		while not self.movie_queue.empty():
			self.movie_list.append(self.movie_queue.get())
		self.movie_list = sorted(self.movie_list, key=lambda x:float(x[0]), reverse = True)
		open("Top_movie_list.txt", "w+").write('\n'.join(['\t'.join(m) for m in self.movie_list]).encode('utf-8'))

	def threadFunc(self):
		while not self.task_queue.empty():
			start = self.task_queue.get()
			params = {'start': start, 'filter':'', 'type':''}
			response = requests.get(self.url, params = params, headers = self.headers)
			soup = BeautifulSoup(response.content, "html.parser")
			item_list = soup.find_all('div', 'info')
			for item in item_list:
				head = item.find('div', 'hd')
				body = item.find('div', 'bd')
				span_list = head.a.find_all('span')
				link = head.a['href']
				# title = []
				# for t in span_list: title.append(t.contents[0])
				title = head.a.span.contents[0]
				star = body.div.span.em.contents[0]
				# info = body.find('p').contents[0]
				# quote = body.find_all('p', 'quote')[0].span.contents[0]

				self.movie_queue.put([star, link, title])
				# print title, star, link

if __name__ == "__main__":
	m = Movie()
	m.crawler()