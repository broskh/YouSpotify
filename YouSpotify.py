#!/usr/bin/python3
import argparse
import ast
import json
import os
import taglib

from util import *

CONFIG_FILE = "config.json"

DEFAULT_MUSIC_FOLDER = "/home/broskh/Musica/"


def main():
    config = import_config()
    log.set_log_file(config['LOG_FILE'])
    if config['DEBUG']:
        log.enable_debug()
    else:
        log.disable_debug()
    log.print_log("-------", "-------")
    log.print_log("START", "")
    # Parse arguments.
    parser = argparse.ArgumentParser(description='Exports your Spotify playlists. By default, opens a browser window '
                                                 + 'to authorize the Spotify Web API, but you can also manually specify'
                                                 + ' an OAuth token with the --token option.')
    parser.add_argument('--token', metavar='OAUTH_TOKEN', help='use a Spotify OAuth token (requires the '
                                                               + '`playlist-read-private` permission)')
    args = parser.parse_args()

    if args.token:
        spotify = Spotify.Spotify(args.token)
    else:
        spotify = Spotify.authorize(client_id='5c098bcc800e45d49e476265bc9b6934', scope='playlist-read-private')

    log.print_console("LOGGED IN", '{id}'.format(**spotify.get_user()))

    playlists = spotify.get_user_playlists()
    i = 0
    for playlist in playlists:
        print(str(i) + ") " + playlist['name'])
        i += 1
    choice = input("Scegli la playlist che vuoi scaricare: ")
    playlist_chosen = playlists[int(choice)]
    log.print_console("PLAYLIST SCELTA", playlist_chosen['name'])

    ambiguos = []
    not_found = []

    for track in playlist_chosen['tracks']:
        found = None
        for filename in os.listdir(config['MUSIC_FOLDER']):
            if filename.lower().endswith('.mp3'):
                song = taglib.File(config['MUSIC_FOLDER'] + filename)
                if 'COMMENT' in song.tags:
                    if song.tags['COMMENT'][0] == track['track']['uri']:
                        track['file_path'] = config['MUSIC_FOLDER'] + filename
                        found = True
                        log.print_console("TRACCIA TROVATA", "traccia \'" + track['track']['name'] +
                                          "\' trovata nella cartella Musica")
                        break
        if not found:
            for filename in os.listdir(config['MUSIC_FOLDER']):
                if filename.lower().endswith('.mp3'):
                    song = taglib.File(config['MUSIC_FOLDER'] + filename)
                    if 'TITLE' in song.tags:
                        if track['track']['name'] in song.tags['TITLE'][0]:
                            track['file_path'] = config['MUSIC_FOLDER'] + filename
                            ambiguos.append(track)
                            found = True
                            break
        if not found:
            track['yt_videos'] = youtube.youtube_search(track)
            for video in track['yt_videos']:
                duration_yt = youtube.get_video_duration(video)
                if (duration_yt >= track['track']['duration_ms'] - 3000) and \
                        (duration_yt <= track['track']['duration_ms'] + 3000):  # match con video di 3 secondi +- lunghi
                    filename = config['MUSIC_FOLDER'] + ', '.join([artist['name'] for artist in track['track']['artists']]) + \
                               " - " + track['track']['name']
                    youtube.download_youtube(video, filename)
                    track['file_path'] = filename + ".mp3"
                    spotify.tag_mp3_file(track)
                    found = True
                    log.print_console("TRACCIA TROVATA", "traccia \'" + track['track']['name'] + "\' scaricata da youtube")
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
            log.print_console("TRACCIA TROVATA", "traccia \'" + track['track']['name'] + "\' trovata nella cartella Musica")
    for track in not_found:
        print("Il brano della playlist: {titolo: " + track['track']['name'] + " , artisti: " +
              ', '.join([artist['name'] for artist in track['track']['artists']]) + "} non trovata")
        print("1) Indica il nome del file all'interno della cartella musica")
        print("2) Indica il video youtube dal quale estrarre la canzone")
        print("3) Rimuovi la canzone dalla playlist")
        answer = False
        while not answer:
            choice = input("Scegli un opzione: ")
            choice = int(choice)
            if choice == 1:
                answer = True
                file = input("Nome del file: ")
                track['file_path'] = config['MUSIC_FOLDER'] + file
                spotify.tag_mp3_file(track)
                log.print_console("TRACCIA TROVATA",
                                  "traccia \'" + track['track']['name'] + "\' trovata nella cartella Musica")
            elif choice == 2:
                answer = True
                artisti = ', '.join([artist['name'] for artist in track['track']['artists']])
                filename = config['MUSIC_FOLDER'] + artisti + " - " + track['track']['name']
                codice_yt = input("Inserisci il codice del video youtube: ")
                youtube.download_youtube(codice_yt, filename)
                track['file_path'] = filename + ".mp3"
                spotify.tag_mp3_file(track)
                log.print_console("TRACCIA TROVATA", "traccia \'" + track['track']['name'] + "\' scaricata da youtube")
            elif choice == 3:
                answer = True
                playlist_chosen.remove(track)
                log.print_console("TRACK RIMOSSA", "traccia \'" + track['track']['name'] + "\' rimossa dalla playlist")
            else:
                print("Scelta errata")

    playlist_file = playlist_chosen['name'] + ".m3u"
    of = open(config['MUSIC_FOLDER'] + playlist_file, 'w')
    for track in playlist_chosen['tracks']:
        of.write(track['file_path'] + "\n")
    of.close()
    log.print_console("FINE", "playlist \'" + playlist_chosen['name'] + "\' creata correttamente nel file "
                      + playlist_file)


# Import imformation from config file and opportunely set variables
def import_config():
    config = {}
    if os.path.isfile(CONFIG_FILE):
        json_file = open(CONFIG_FILE, 'r')
        config = json.load(json_file)

    else:
        config['MUSIC_FOLDER'] = DEFAULT_MUSIC_FOLDER
        config['LOG_FILE'] = log.DEFAULT_LOG_FILE
        config['DEBUG'] = log.DEFAULT_DEBUG
        json_file = open(CONFIG_FILE, 'w')
        json_file.write(json.dumps(config))
    json_file.close()
    return config


if __name__ == '__main__':
    main()
