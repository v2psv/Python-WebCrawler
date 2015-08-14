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

if __name__ == '__main__':
	playlist_list = []
	track_list = []
	track_dict = {}

	file = open('playlists.txt', 'r')
	while True:
		playlist_id, playlist_count, playlist_title = file.readline().strip().split('\t')
		if int(playlist_count) < 5000:
			break
		playlist_list.append((playlist_id, playlist_count, playlist_title))
	file.close()

	for p in playlist_list:
		folder = os.path.join('./playlists_1', p[2])
		path = os.path.join(folder, 'playlist.txt')
		print path
		file = open(path, "r")
		for i in range(7): file.readline()
		list = file.read().split('\n')
		track_list.extend([l.split('\t') for l in list])
		file.close()

	print 'get tracks finished...'

	file = open('./playlists/all_music.txt', 'w+')
	file.write('[Total num: ' + str(len(track_list)) + '\n]')
	file.write('\n'.join(['\t'.join(s) for s in track_list]))
	file.close()

	print 'combine all tracks finished...'

	for s in track_list:
		f = bytearray(s[3])
		track_dict[md5(f)] = s
	track_list = track_dict.values()
	file = open('./playlists/top_music.txt', 'w+')
	file.write('[Total num: ' + str(len(track_list)) + '\n]')
	file.write('\n'.join(['\t'.join(s) for s in track_list]))
	file.close()

	print 'remove duplicate tracks finished...'