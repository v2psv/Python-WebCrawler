#!usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import md5
import random
import Queue
import json
import requests
import threading
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding("utf-8")

THREAD_NUM = 100

class PlaylistInfo:
	def __init__(self, (list_id, play_count, title)):
		self.id = list_id
		self.play_count = play_count
		self.title = title
		self.songs = []
		self.success = True
		self.url = 'http://music.163.com/api/playlist/detail?id=%s' % self.id
		self.headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Host':'music.163.com',
			'Referer':'http://music.163.com/',
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
			'Cookie':'_ntes_nnid=628e32a284dc44116c6730eb2eff8f14,1439198141640; _ntes_nuid=628e32a284dc44116c6730eb2eff8f14; vjuids=1c7ab5fff.14f16e4e37b.0.933be663; vjlast=1439198143.1439198143.30; vinfo_n_f_l_n3=d8f90b2f59f960c6.1.0.1439198143388.0.1439198704814; nteslogger_exit_time=1439198743829; usertrack=ezq0alXLD9ORfXmwmpEMAg==; visited=true; __csrf=11b236c8eff3e2321b85d14d46f6bc59; __utma=94650624.1417039898.1439371222.1439441912.1439446137.5; __utmc=94650624; __utmz=94650624.1439433948.3.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); JSESSIONID-WYYY=9a4f4af156dce0e6c3fa6d91106f6a80549d44b1bd513d9f5bd06edba2b2e6dd407a2e3a5547ac284c948f14766fd3342b2edcb177dcbdad350e03ce75947a7c4c2dd734f060604e6823a96c5df1678bc8ce6684805b1dd1fe41d25f3dbc6a00ef87162c0e21ea3ec09f95d740c175a8e8fa7e9ac38705c9997b6619f860b15cbce67b8d%3A1439457802818; _iuqxldmzr_=25'
			}
		self.getPlaylistInfo()

	def getPlaylistInfo(self):
		try:
			response = requests.get(self.url, headers = self.headers)
			response.encoding = "utf-8"
			data = json.loads(response.text)
			self.getFileds(data['result'])
		except Exception, e:
			print '---------------------------------------------\n', e
			self.success = False

	def getFileds(self, data):
		self.creator = data['creator']['nickname']
		self.tag = '&'.join(data['tags'])
		self.track_count = str(data['trackCount'])
		self.subscribe_count = str(data['subscribedCount'])
		for song in data['tracks']:
			info = self.getSong(song)
			# print info
			self.songs.append(info)

	def getSong(self, song):
		album, artists, name = '未知专辑', '未知艺术家', ''
		if song['name']:
			name = song['name'].strip()
		if song['album']:
			album = song['album']['name']
		if song['artists']:
			artists = '&'.join([a['name'] for a in song['artists']])
		if song['hMusic']:
			music = song['hMusic']
			quality = 'HD'
		elif song['mMusic']:
			music = song['mMusic']
			quality = 'MD'
		elif song['lMusic']:
			music = song['lMusic']
			quality = 'LD'
		else:
			ext = song['mp3Url'].split('.')[-1]
			return (album, artists, name, song['mp3Url'], 'None', ext)

		quality = quality + ' {0}k'.format(music['bitrate']/1000)
		song_id = str(music['dfsId'])
		enc_id = self.encryptId(song_id)
		ext = music['extension']
		if name == '':
			name = music['name']
		url = "http://m%s.music.126.net/%s/%s.%s"%(random.randrange(1,3), enc_id, song_id, ext)
		return (album, artists, name, url, quality, ext)

	def encryptId(self, id):
	    byte1 = bytearray('3go8&$8*3*3h0k(2)2')
	    byte2 = bytearray(id)
	    byte1_len = len(byte1)
	    for i in xrange(len(byte2)):
	        byte2[i] = byte2[i]^byte1[i%byte1_len]
	    m = md5.new()
	    m.update(byte2)
	    result = m.digest().encode('base64')[:-1]
	    result = result.replace('/', '_')
	    result = result.replace('+', '-')
	    return result

def crawler(playlist_queue, tracks_queue):
	while not playlist_queue.empty():
		p = playlist_queue.get()
		# print '\t'.join(p)
		playlist = PlaylistInfo(p)
		if playlist.success is False:
			print '\t'.join(p)
			continue
		if int(playlist.subscribe_count) < 8000:
			continue
		print playlist.id, playlist.subscribe_count
		try:
			folder = os.path.join('./playlists', playlist.id)
			if not os.path.exists(folder):
				os.makedirs(folder)

			file = open(os.path.join(folder, 'playlist.txt'), 'w+')
			file.write('[playlist_id: ' + playlist.id + ']\n')
			file.write('[playlist_title: ' + playlist.title + ']\n')
			file.write('[play_count: ' + playlist.play_count + ']\n')
			file.write('[creator: ' + playlist.creator + ']\n')
			file.write('[tag: ' + playlist.tag + ']\n')
			file.write('[track_count: ' + playlist.track_count + ']\n')
			file.write('[subscribe_count: ' + playlist.subscribe_count + ']\n')
			file.write('\n'.join(['\t'.join(s) for s in playlist.songs]))
			file.close()
			# try:
			# 	song = ''
			# 	for song in playlist.songs:
			# 		file.write('\t'.join(song) + '\n')
			# except Exception, e:
			# 	print '##################################################\n', e
			# 	print song
			# 	continue
			tracks_queue.put(playlist.songs)

		except Exception, e:
			print '##################################################\n', e
			continue

if __name__ == '__main__':
	playlist_queue = Queue.Queue()
	tracks_queue = Queue.Queue()

	file = open('playlists.txt', 'r')
	while True:
		playlist_id, playlist_count, playlist_title = file.readline().strip().split('\t')
		if int(playlist_count) < 5000:
			break
		playlist_queue.put((playlist_id, playlist_count, playlist_title))
	file.close()

	thread_list = []
	for i in range(THREAD_NUM):
		thread_list.append(threading.Thread(target = crawler, args = (playlist_queue, tracks_queue)))
	for t in thread_list:
		t.start()
	for t in thread_list:
		t.join()

	print 'get tracks finished...'

	track_list = []
	track_dict = {}
	while not tracks_queue.empty():
		track_list.extend(tracks_queue.get())
	file = open('./playlists/all_music.txt', 'w+')
	file.write('[Total num: ' + str(len(track_list)) + ']\n')
	file.write('\n'.join(['\t'.join(s) for s in track_list]))
	file.close()

	print 'combine all tracks finished...'

	for s in track_list:
		# f = bytearray(s[3].encode('utf-8'))
		track_dict[s[3]] = s
	track_list = track_dict.values()
	file = open('./playlists/top_music.txt', 'w+')
	file.write('[Total num: ' + str(len(track_list)) + ']\n')
	file.write('\n'.join(['\t'.join(s) for s in track_list]))
	file.close()

	print 'remove duplicate tracks finished...'

	sys.exit(0)