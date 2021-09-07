#!/usr/bin/python
# https://github.com/youtube/api-samples/tree/master/python
# This sample executes a search request for the specified search term.
# Sample usage:
#   python search.py --q=surfing --max-results=10
# NOTE: To use the sample, you must provide a developer key obtained
#       in the Google APIs Console. Search for "REPLACE_ME" in this code
#       to find the correct place to provide that key..

import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import socks
import socket
# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = '****************'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search():
  # 如下是代理设置
  socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080)
  socket.socket = socks.socksocket

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
  all = []
  # Call the search.list method to retrieve results matching the specified
  # query term.
  txt = 'THUOCL_food_8974.txt'
  with open(txt, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:

        line = line.strip("\n").split("\t")[0]+" 食物"
        search_response = youtube.search().list(
          q=line,
          part='id,snippet',
          maxResults=500
        ).execute()

        videos = []
        channels = []
        playlists = []
        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for search_result in search_response.get('items', []):
          if search_result['id']['kind'] == 'youtube#video':
            videos.append('%s %s https://www.youtube.com/watch?v=%s' % (line, search_result['snippet']['title'],
                                       search_result['id']['videoId']))
            all.append('%s %s https://www.youtube.com/watch?v=%s' % (line, search_result['snippet']['title'],
                                                                        search_result['id']['videoId']))
          elif search_result['id']['kind'] == 'youtube#channel':
            channels.append('%s (%s)' % (search_result['snippet']['title'],
                                         search_result['id']['channelId']))
          elif search_result['id']['kind'] == 'youtube#playlist':
            playlists.append('%s (%s)' % (search_result['snippet']['title'],
                                          search_result['id']['playlistId']))
            
        print('\n'.join(videos), '\n')
  with open('URL_all.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(all))

if __name__ == '__main__':
  try:
    youtube_search()
  except HttpError as e:
    print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
