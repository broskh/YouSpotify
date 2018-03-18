#!/usr/bin/python
import json

from googleapiclient.discovery import build
#from apiclient.errors import HttpError
#from oauth2client.tools import argparser

import urllib
from bs4 import BeautifulSoup

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyDOZnawRC1wEPErZmSyLYWdTplXKX3Q_oo"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(track):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  textToSearch = '{name}\t{artists}\taudio'.format(
        name=track['track']['name'],
        artists=', '.join([artist['name'] for artist in track['track']['artists']])
    )

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=textToSearch,
    part="id,snippet",
    maxResults=50
  ).execute()

  videos = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
        print(str(track['duration_ms']) + "\t\t" + str(getVideoDuration(search_result["id"]["videoId"])))
        if track['duration_ms'] == getVideoDuration(search_result["id"]["videoId"]):
            print("bella")

        # videos.append("%s (%s)" % (search_result["snippet"]["title"],
        #                          search_result["id"]["videoId"]))

def searchYoutube(track):
  textToSearch = '{name}\t{artists}'.format(
        name=track['track']['name'],
        artists=', '.join([artist['name'] for artist in track['track']['artists']])
    )
  query = urllib.parse.quote(textToSearch)
  url = "https://www.youtube.com/results?search_query=" + query
  response = urllib.request.urlopen(url)
  html = response.read()
  soup = BeautifulSoup(html, "html.parser")
  #we return the first result
  # return "https://youtube.com" + soup.findAll(attrs={'class':'yt-uix-tile-link'})[0]['href']

def getVideoDuration(videoId):
    video_id = "6_zn4WCeX0o"
    api_key = "Your API KEY replace it!"
    searchUrl = "https://www.googleapis.com/youtube/v3/videos?id=" + videoId + "&key=" + DEVELOPER_KEY + "&part=contentDetails"
    response = urllib.urlopen(searchUrl).read()
    data = json.loads(response)
    all_data = data['items']
    contentDetails = all_data[0]['contentDetails']
    duration = contentDetails['duration']
    return duration

# link = searchYoutube(name)
# downloadYoutube(link)