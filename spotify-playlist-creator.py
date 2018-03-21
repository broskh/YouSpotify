#!/usr/bin/python
##########!/usr/bin/env python3

import argparse
import json

import mp3_tagger
import os
from mutagen.easyid3 import EasyID3
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

    trovato = None
    for filename in os.listdir(youtubeDownloader.MUSIC_FOLDER):
        if filename.lower().endswith(('.mp3')):
            audioFile = mp3_tagger.MP3File(youtubeDownloader.MUSIC_FOLDER + filename)
            audioFile.set_version(mp3_tagger.VERSION_1)
            if audioFile.comment == track['track']['uri']:
                track['file_path'] = filename
                trovato = True
                break
    if not(trovato):
        for filename in os.listdir(youtubeDownloader.MUSIC_FOLDER):
            if filename.lower().endswith(('.mp3')):
                audioFile = mp3_tagger.MP3File(youtubeDownloader.MUSIC_FOLDER + filename)
                audioFile.set_version(mp3_tagger.VERSION_1)
                if audioFile.song == track['track']['name']:
                    track['file_path'] = filename
                    ambiguos.append(track)
                    trovato = True
                    break
    if not(trovato):
        for video in track['yt_videos']:
            duration_yt = youtubeDownloader.getVideoDuration(video)
            if (duration_yt >= track['track']['duration_ms']-3000) and \
                    (duration_yt <= track['track']['duration_ms']+3000):#match con video di 2 secondi + o - lunghi
                filename = ', '.join([artist['name']
                    for artist in track['track']['artists']]) + " - " + track['track']['name']
                youtubeDownloader.downloadYoutube(video, filename)
                track['file_path'] = filename + ".mp3"
                trovato = True
                break;
    if not(trovato):
        not_found.append(track)

for track in ambiguos:
    scelta = input("Il brano della playlist: {titolo: " + track['track']['name'] + " , artisti: " +
          ', '.join([artist['name'] for artist in track['track']['artists']]) + "} corrisponde al file: " +
          track['file_path'] + "?[y|N] ")
    if not(scelta == 'y' or scelta == 'Y'):
        track['file_path'] = ""
        not_found.append(track)
for track in not_found:
    print("Il brano della playlist: {titolo: " + track['track']['name'] + " , artisti: " +
          ', '.join([artist['name'] for artist in track['track']['artists']]) + "} non trovata")
    print("1) Indica il percorso contenente il file")
    print("2) Indica l'URL youtube dal quale estrarre la canzone")
    print("3) Rimuovi la canzone dalla plyalist")
    scelta = input("Scegli un opzione: ")
    if scelta == 1:
        track['file_path'] = input("Nome del file: ")
    elif scelta == 2:
        filename = ', '.join([artist['name'] for artist in track['track']['artists']]) + " - " + track['track']['name']
        codice_yt = input("Inserisci il codice del video youtube: ")
        youtubeDownloader.downloadYoutube(codice_yt, filename)
        track['file_path'] = filename + ".mp3"
    elif scelta == 3:
        playlist_scelta.remove(track)

of = open(youtubeDownloader.MUSIC_FOLDER + playlist_scelta['name'] + ".m3u", 'w')
of.write("#EXTM3U\n")
for track in playlist_scelta['tracks']:
    audioFile = mp3_tagger.MP3File(youtubeDownloader.MUSIC_FOLDER + track['file_path'])
    audioFile.song = track['track']['name']
    print(track['track']['name'])
    print(audioFile.song)
    audioFile.artist = ', '.join([artist['name'] for artist in track['track']['artists']])
    print(', '.join([artist['name'] for artist in track['track']['artists']]))
    print(audioFile.artist)
    audioFile.album = track['track']['album']['name']
    print(track['track']['album']['name'])
    print(audioFile.album)
    audioFile.comment = track['track']['uri']
    print(track['track']['uri'])
    print(audioFile.comment)
    audioFile.track = str(track['track']['track_number'])
    print(str(track['track']['track_number']))
    print(audioFile.track)
    audioFile.save()

    #ALTRI META?

    of.write("#EXTINF:%s,%s\n" % (track['track']['duration_ms'], track['file_path']))
    of.write(track['file_path'] + "\n")
of.close()