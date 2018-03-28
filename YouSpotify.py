#!/usr/bin/python3
import argparse
import os
import taglib

from util import *

MUSIC_FOLDER = "/home/broskh/Musica/"


def main():
    # Parse arguments.
    parser = argparse.ArgumentParser(description='Exports your Spotify playlists. By default, opens a browser window '
                                                 + 'to authorize the Spotify Web API, but you can also manually specify'
                                                 + ' an OAuth token with the --token option.')
    parser.add_argument('--token', metavar='OAUTH_TOKEN', help='use a Spotify OAuth token (requires the '
                                                               + '`playlist-read-private` permission)')
    args = parser.parse_args()

    # Log into the Spotify API.
    if args.token:
        spotify = Spotify.Spotify(args.token)
    else:
        spotify = Spotify.authorize(client_id='5c098bcc800e45d49e476265bc9b6934', scope='playlist-read-private')

    # Get the ID of the logged in user.
    log.print_console("LOGGING", 'Logged in as {display_name} ({id})'.format(**spotify.get_user()))

    playlists = spotify.get_user_playlists()
    i = 0
    for playlist in playlists:
        print(str(i) + ") " + playlist['name'])
        i += 1
    choice = input("Scegli la playlist che vuoi scaricare: ")
    choise_playlist = playlists[int(choice)]

    ambiguos = []
    not_found = []

    for track in choise_playlist['tracks']:
        found = None
        for filename in os.listdir(MUSIC_FOLDER):
            if filename.lower().endswith('.mp3'):
                song = taglib.File(MUSIC_FOLDER + filename)
                if 'COMMENT' in song.tags:
                    if song.tags['COMMENT'][0] == track['track']['uri']:
                        track['file_path'] = MUSIC_FOLDER + filename
                        found = True
                        break
        if not found:
            for filename in os.listdir(MUSIC_FOLDER):
                if filename.lower().endswith('.mp3'):
                    song = taglib.File(MUSIC_FOLDER + filename)
                    if 'TITLE' in song.tags:
                        if track['track']['name'] in song.tags['TITLE'][0]:
                            track['file_path'] = MUSIC_FOLDER + filename
                            ambiguos.append(track)
                            found = True
                            break
        if not found:
            track['yt_videos'] = youtube.youtube_search(track)
            for video in track['yt_videos']:
                duration_yt = youtube.get_video_duration(video)
                if (duration_yt >= track['track']['duration_ms'] - 3000) and \
                        (duration_yt <= track['track']['duration_ms'] + 3000):  # match con video di 3 secondi +- lunghi
                    filename = MUSIC_FOLDER + ', '.join([artist['name'] for artist in track['track']['artists']]) + \
                               " - " + track['track']['name']
                    youtube.download_youtube(video, filename)
                    track['file_path'] = filename + ".mp3"
                    spotify.tag_mp3_file(track)
                    found = True
                    break
        if not found:
            not_found.append(track)

    for track in ambiguos:
        choice = input("Il brano della playlist: {titolo: " + track['track']['name'] + " , artisti: " +
                       ', '.join([artist['name'] for artist in track['track']['artists']]) + "} corrisponde al file: " +
                       track['file_path'] + "?[y|N] ")
        if not (choice == 'y' or choice == 'Y'):
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
            choice = input("Scegli un opzione: ")
            choice = int(choice)
            if choice == 1:
                answer = True
                file = input("Nome del file: ")
                track['file_path'] = MUSIC_FOLDER + file
                spotify.tag_mp3_file(track)
            elif choice == 2:
                answer = True
                artisti = ', '.join([artist['name'] for artist in track['track']['artists']])
                filename = MUSIC_FOLDER + artisti + " - " + track['track']['name']
                codice_yt = input("Inserisci il codice del video youtube: ")
                youtube.download_youtube(codice_yt, filename)
                track['file_path'] = filename + ".mp3"
                spotify.tag_mp3_file(track)
            elif choice == 3:
                choise_playlist.remove(track)
            else:
                print("Scelta errata")

    of = open(MUSIC_FOLDER + choise_playlist['name'] + ".m3u", 'w')
    for track in choise_playlist['tracks']:
        of.write(track['file_path'] + "\n")
    of.close()


if __name__ == '__main__':
    main()
