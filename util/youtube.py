#!/usr/bin/python
import re
import subprocess
from googleapiclient.discovery import build

import json
import urllib

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyDOZnawRC1wEPErZmSyLYWdTplXKX3Q_oo"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MUSIC_FOLDER = "/home/broskh/Musica/"

def youtube_search(track):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY, cache_discovery=False)

    textToSearch = '{name}\t{artists}\t'.format(
        name=track['track']['name'],
        artists=', '.join([artist['name'] for artist in track['track']['artists']])
    )

  # Call the search.list method to retrieve results matching the specified
  # query term.
    search_response = youtube.search().get_list(
            q=textToSearch,
            part="id,snippet",
            maxResults=15#20
        ).execute()

    videos = []
  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s" % (search_result["id"]["videoId"]))
    return videos

def getVideoDuration(videoId):
    searchUrl = "https://www.googleapis.com/youtube/v3/videos?id=" + videoId + "&key=" + DEVELOPER_KEY + "&part=contentDetails"
    response = urllib.request.urlopen(searchUrl).read().decode('utf-8')
    data = json.loads(response)
    all_data = data['items']
    contentDetails = all_data[0]['contentDetails']
    duration = contentDetails['duration']
    min_regex = re.compile("[0-9]+(?=M)")
    min_search = min_regex.search(duration)
    sec_regex = re.compile("[0-9]+(?=S)")
    sec_search = sec_regex.search(duration)
    if min_search:
        minutes = int(min_search.group(0))
    else:
        minutes = 0
    if sec_search:
        seconds = int(sec_search.group(0))
    else:
        seconds = 0
    return minutes*60000 + seconds*1000

def downloadYoutube(yt_id, filename):
    """ downloading the track """
    link = "https://www.youtube.com/watch?v=" + yt_id
    path = MUSIC_FOLDER + filename + ".%(ext)s"
    # p = Popen(['bash'], stdin=PIPE, stdout=PIPE)
    command = 'youtube-dl -o \"' + path + '\" --extract-audio --audio-format mp3 ' + link + '\n';
    # print("COMMAND DOWNLOAD: " + command)
    # p.stdin.write(command.encode('utf-8'))
    # print(p.stdout.readline())
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    tmp = proc.stdout.read()
    #-------->>>>>>>><CONTROLLO TRACCIA MUTA<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<---------------