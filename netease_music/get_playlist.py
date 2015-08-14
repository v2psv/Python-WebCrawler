#!usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import Queue
import requests
import threading
from bs4 import BeautifulSoup

THREAD_NUM = 50

def getAllPlaylist(thread_id, playlist_queue):
	url = 'http://music.163.com/discover/playlist/'
	headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Host':'music.163.com',
			'Referer':'http://music.163.com/',
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
			}

	for i in [thread_id, thread_id+THREAD_NUM]:
		params = {'order':'hot', 'cat':'全部', 'limit':35, 'offset':i*35}
		response = requests.get(url, params = params, headers = headers)
		soup = BeautifulSoup(response.content, 'html.parser')
		lists = soup.find('ul', {'class':'m-cvrlst f-cb', 'id':'m-pl-container'}).find_all('li')
		for list in lists:
			playlist_count = list.div.div.find('span', {'class':'nb'}).contents[0]
			p = list.find('p', {'class':'dec'})
			playlist_title = p.a['title'].strip()
			playlist_id = p.a['href'].split('=')[-1]
			playlist_queue.put((playlist_id, playlist_count, playlist_title))

if __name__ == '__main__':
	thread_list = []
	playlist_list = []
	playlist_queue = Queue.Queue()
	for i in range(THREAD_NUM):
		thread_list.append(threading.Thread(target = getAllPlaylist, args = (i, playlist_queue)))
	for t in thread_list:
		t.start()
	for t in thread_list:
		t.join()

	while not playlist_queue.empty():
		playlist_list.append(playlist_queue.get())
	playlist_list = sorted(playlist_list, key = lambda x:int(x[1]), reverse = True)
	open('playlists.txt', 'w+').write('\n'.join(['\t'.join(l) for l in playlist_list]).encode('utf-8'))
