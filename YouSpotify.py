#!/usr/bin/python3

import argparse
import os
import taglib

from util import log, Spotify, youtube

# def main():
# Parse arguments.
parser = argparse.ArgumentParser(description='Exports your Spotify playlists. By default, opens a browser window '
                                             + 'to authorize the Spotify Web API, but you can also manually specify'
                                             + ' an OAuth token with the --token option.')
parser.add_argument('--token', metavar='OAUTH_TOKEN', help='use a Spotify OAuth token (requires the '
                                                           + '`playlist-read-private` permission)')
args = parser.parse_args()

# If they didn't give a filename, then just prompt them. (They probably just double-clicked.)
# while not args.file:
#     args.file = input('Enter a file name (e.g. playlists.txt): ')

# Log into the Spotify API.
if args.token:
    spotify = Spotify(args.token)
else:
    spotify = Spotify.authorize(client_id='5c098bcc800e45d49e476265bc9b6934', scope='playlist-read-private')

# Get the ID of the logged in user.
log.print_console("LOGGING", 'Logged in as {display_name} ({id})'.format(**spotify.get_user()))

playlists = spotify.get_user_playlists()
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
    for filename in os.listdir(youtube.MUSIC_FOLDER):
        if filename.lower().endswith('.mp3'):
            song = taglib.File(youtube.MUSIC_FOLDER + filename)
            if 'COMMENT' in song.tags:
                if song.tags['COMMENT'][0] == track['track']['uri']:
                    track['file_path'] = filename
                    trovato = True
                    break
    if not trovato:
        for filename in os.listdir(youtube.MUSIC_FOLDER):
            if filename.lower().endswith('.mp3'):
                song = taglib.File(youtube.MUSIC_FOLDER + filename)
                if 'TITLE' in song.tags:
                    if track['track']['name'] in song.tags['TITLE'][0]:
                        track['file_path'] = filename
                        ambiguos.append(track)
                        trovato = True
                        break
    if not trovato:
        track['yt_videos'] = youtube.youtube_search(track)
        for video in track['yt_videos']:
            duration_yt = youtube.getVideoDuration(video)
            if (duration_yt >= track['track']['duration_ms'] - 3000) and \
                    (duration_yt <= track['track']['duration_ms'] + 3000):  # match con video di 3 secondi + o - lunghi
                filename = ', '.join([artist['name'] for artist in track['track']['artists']]) + " - " \
                           + track['track']['name']
                youtube.downloadYoutube(video, filename)
                track['file_path'] = filename + ".mp3"
                spotify.tag_mp3_file(track)
                trovato = True
                break
    if not trovato:
        not_found.append(track)


for track in ambiguos:
    scelta = input("Il brano della playlist: {titolo: " + track['track']['name'] + " , artisti: " +
                   ', '.join([artist['name'] for artist in track['track']['artists']]) + "} corrisponde al file: " +
                   track['file_path'] + "?[y|N] ")
    if not (scelta == 'y' or scelta == 'Y'):
        track['file_path'] = ""
        not_found.append(track)
    else:
        spotify.tag_mp3_file(track)
for track in not_found:
    print("Il brano della playlist: {titolo: " + track['track']['name'] + " , artisti: " +
          ', '.join([artist['name'] for artist in track['track']['artists']]) + "} non trovata")
    print("1) Indica il file all'interno del filesystem")
    print("2) Indica il video youtube dal quale estrarre la canzone")
    print("3) Rimuovi la canzone dalla playlist")
    answer = False
    while not answer:
        scelta = input("Scegli un opzione: ")
        scelta = int(scelta)
        if scelta == 1:
            answer = True
            track['file_path'] = input("Nome del file: ")
            spotify.tag_mp3_file(track)
        elif scelta == 2:
            answer = True
            artisti = ', '.join([artist['name'] for artist in track['track']['artists']])
            filename = artisti + " - " + track['track']['name']
            codice_yt = input("Inserisci il codice del video youtube: ")
            youtube.downloadYoutube(codice_yt, filename)
            track['file_path'] = filename + ".mp3"
            spotify.tag_mp3_file(track)
        elif scelta == 3:
            playlist_scelta.remove(track)
        else:
            print("Scelta errata")

of = open(youtube.MUSIC_FOLDER + playlist_scelta['name'] + ".m3u", 'w')
for track in playlist_scelta['tracks']:
    of.write(track['file_path'] + "\n")
of.close()
