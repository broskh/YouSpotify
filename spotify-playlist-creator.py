#!/usr/bin/python
##########!/usr/bin/env python3

import argparse
import json

import eyed3
import os

import log
import SpotifyAPI
import youtubeDownloader

#def main():
# Parse arguments.
parser = argparse.ArgumentParser(description='Exports your Spotify playlists. By default, opens a browser window '
                                             + 'to authorize the Spotify Web API, but you can also manually specify'
                                             + ' an OAuth token with the --token option.')
parser.add_argument('--token', metavar='OAUTH_TOKEN', help='use a Spotify OAuth token (requires the '
                                                           + '`playlist-read-private` permission)')
parser.add_argument('--format', default='txt', choices=['json', 'txt'], help='output format (default: txt)')
parser.add_argument('file', help='output filename', nargs='?')
args = parser.parse_args()

# If they didn't give a filename, then just prompt them. (They probably just double-clicked.)
# while not args.file:
#     args.file = input('Enter a file name (e.g. playlists.txt): ')

# Log into the Spotify API.
if args.token:
    spotify = SpotifyAPI(args.token)
else:
    spotify = SpotifyAPI.authorize(client_id='5c098bcc800e45d49e476265bc9b6934', scope='playlist-read-private')

# Get the ID of the logged in user.
log.print('Logged in as {display_name} ({id})'.format(**spotify.getUser()))

playlists = spotify.getPlaylists()

i = 0
for playlist in playlists:
    print(str(i)+") " + playlist['name'])
    i += 1
scelta = input("Scegli la playlist che vuoi scaricare: ")
playlist_scelta = playlists[int(scelta)];

ambiguos = []
not_found = []

for track in playlist_scelta['tracks']:
    track['yt_videos'] = youtubeDownloader.youtube_search(track)

    for filename in os.listdir(youtubeDownloader.MUSIC_FOLDER):
        if filename.lower().endswith(('.mp3')):
            audioFile = eyed3.load(filename)
            tag = audioFile.getTag()
            if json.loads(tag['comments'])['spotify_track_id'] ==  track['uri']:
                track['file_path'] = filename
            elif tag['title'] == track ['title']:
                track['file_path'] = filename
                ambiguos.append(track)
            else:
                for video in track['yt_videos']:
                    if (youtubeDownloader.getVideoDuration(video) >= track['duration_ms']-1) and \
                            (youtubeDownloader.getVideoDuration(video) <= track['duration_ms']+1):
                        track['file_path'] = youtubeDownloader.downloadYoutube(video)
                    else:
                        not_found.append(track)

for track in ambiguos:
    scelta = input("Il brano della playlist: {titolo: " + track['title'] + " , artisti: " +
          ', '.join([artist['name'] for artist in track['track']['artists']]) + "} corrisponde al file: " +
          track['file_path'] + "?[y|N] ")
    if not(scelta == 'y' or scelta == 'Y'):
        track['file_path'] = ""
        not_found.append(track)
for track in not_found:
    print("Il brano della playlist: {titolo: " + track['title'] + " , artisti: " +
          ', '.join([artist['name'] for artist in track['track']['artists']]) + "} non trovata")
    print("1) Indica il percorso contenente il file")
    print("2) Indica l'URL youtube dal quale estrarre la canzone")
    print("3) Rimuovi la canzone dalla plyalist")
    scelta = input("Scegli un opzione: ")
    if scelta == 1:
        track['file_path'] = input("Percorso del file: ")
    elif scelta == 2:
        track['file_path'] = youtubeDownloader.downloadYoutube(input("URL youtube: "))
    elif scelta == 3:
        playlist_scelta.remove(track)

of = open(playlist_scelta['name'] + ".m3u", 'w')
of.write("#EXTM3U\n")
for track in playlist_scelta:
    audioFile = eyed3.load(track['file_path'])
    tag = audioFile.getTag()
    tag['title'] = track['title']
    tag['artists'] = ', '.join([artist['name'] for artist in track['track']['artists']])
    tag['album'] = track['album']
    tag['comments'] = "{'spotify_track_id': " + track['uri'] + "}"
    #ALTRI META?

    of.write("#EXTINF:%s,%s\n" % (track['length'], track['file_path']))
    of.write(track['file_path'] + "\n")
of.close()