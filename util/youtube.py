from googleapiclient.discovery import build
import json
import re
import subprocess
import urllib

from util import log

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyDOZnawRC1wEPErZmSyLYWdTplXKX3Q_oo"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MAX_VIDEOS_RESULT = 15


def youtube_search(track):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY, cache_discovery=False)

    text_to_search = '{name}\t{artists}\t'.format(
        name=track['track']['name'],
        artists=', '.join([artist['name'] for artist in track['track']['artists']])
    )

    # Call the search.list method to retrieve results matching the specified query term.
    search_string = youtube.search().list(
            q=text_to_search,
            part="id,snippet",
            maxResults=MAX_VIDEOS_RESULT
        )
    log.print_log('YOUTUBE SEARCH', search_string)
    search_response = search_string.execute()
    log.print_log('YOUTUBE SEARCH RESULT', search_response)

    videos = []
    # Add each result to the appropriate list, and then display the lists of matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s" % (search_result["id"]["videoId"]))
    return videos


def get_video_duration(video_id):
    search_url = "https://www.googleapis.com/youtube/v3/videos?id=" + video_id + "&key=" + \
                DEVELOPER_KEY + "&part=contentDetails"
    log.print_debug("DURATION REQUEST", search_url)
    response = urllib.request.urlopen(search_url).read().decode('utf-8')
    data = json.loads(response)
    all_data = data['items']
    content_details = all_data[0]['contentDetails']
    duration = content_details['duration']
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
    duration = minutes*60000 + seconds*1000
    log.print_log("DURATION", video_id + ": " + str(duration))
    return duration


def download_youtube(yt_id, filename):
    link = "https://www.youtube.com/watch?v=" + yt_id
    path = filename + ".%(ext)s"
    log.print_console("DOWNLOAD START", yt_id + " video")
    command = 'youtube-dl -o \"' + path + '\" --extract-audio --audio-format mp3 ' + link + '\n'
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    proc.stdout.read()
