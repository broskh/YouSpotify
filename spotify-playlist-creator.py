#!/usr/bin/python
##########!/usr/bin/env python3

import argparse
import os
import taglib

import log
import SpotifyAPI
import youtubeDownloader

# def main():
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
    print(str(i) + ") " + playlist['name'])
    i += 1
scelta = input("Scegli la playlist che vuoi scaricare: ")
playlist_scelta = playlists[int(scelta)]

ambiguos = []
not_found = []

for track in playlist_scelta['tracks']:
    trovato = None
    for filename in os.listdir(youtubeDownloader.MUSIC_FOLDER):
        if filename.lower().endswith('.mp3'):
            song = taglib.File(youtubeDownloader.MUSIC_FOLDER + filename)
            if 'COMMENT' in song.tags:
                if song.tags['COMMENT'][0] == track['track']['uri']:
                    track['file_path'] = filename
                    trovato = True
                    break
    if not trovato:
        for filename in os.listdir(youtubeDownloader.MUSIC_FOLDER):
            if filename.lower().endswith(('.mp3')):
                song = taglib.File(youtubeDownloader.MUSIC_FOLDER + filename)
                if 'TITLE' in song.tags:
                    if track['track']['name'] in song.tags['TITLE'][0]:
                        track['file_path'] = filename
                        ambiguos.append(track)
                        trovato = True
                        break
    if not trovato:
        track['yt_videos'] = youtubeDownloader.youtube_search(track)
        for video in track['yt_videos']:
            duration_yt = youtubeDownloader.getVideoDuration(video)
            if (duration_yt >= track['track']['duration_ms'] - 3000) and \
                    (duration_yt <= track['track']['duration_ms'] + 3000):  # match con video di 2 secondi + o - lunghi
                filename = ', '.join([artist['name'] for artist in track['track']['artists']]) + " - " \
                           + track['track']['name']
                youtubeDownloader.downloadYoutube(video, filename)
                track['file_path'] = filename + ".mp3"
                trovato = True
                break
    if not (trovato):
        not_found.append(track)

for track in ambiguos:
    scelta = input("Il brano della playlist: {titolo: " + track['track']['name'] + " , artisti: " +
                   ', '.join([artist['name'] for artist in track['track']['artists']]) + "} corrisponde al file: " +
                   track['file_path'] + "?[y|N] ")
    if not (scelta == 'y' or scelta == 'Y'):
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
    song = taglib.File(youtubeDownloader.MUSIC_FOLDER + track['file_path'])
    song.tags['TITLE'] = track['track']['name']
    song.tags['ARTIST'] = ', '.join([artist['name'] for artist in track['track']['artists']])
    song.tags['ALBUM'] = track['track']['album']['name']
    song.tags['TRACKNUMBER'] = track['track']['track_number'] + "/" + track['track']['album']['tracks'][-1]['track_number']
    #AGGIUNGERE DISC NUNBER E DISC MAX, CORRETTO TRACK NUMBER?
    song.tags['COMMENT'] = track['track']['uri']
    song.tags['GENRE'] = ', '.join(track['track']['album']['genres'])
    song.tags['YEAR'] = track['track']['album']['release_date']
    song.tags['ALBUMARTISTS'] = ', '.join([artist['name'] for artist in track['track']['album']['artists']])
    song.save()

    # ALTRI META?

    of.write("#EXTINF:%s,%s\n" % (track['track']['duration_ms'], track['file_path']))
    of.write(track['file_path'] + "\n")
of.close()
