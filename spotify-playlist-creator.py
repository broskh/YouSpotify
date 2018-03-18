#!/usr/bin/python
##########!/usr/bin/env python3

import argparse
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

for track in playlist_scelta['tracks']:
    link = youtubeDownloader.youtube_search(track)
    print (link)
#                 f.write()

#downloadYoutube(link)
# Write the file.
# with open(args.file, 'w', encoding='utf-8') as f:
#     # JSON file.
#     if args.format == 'json':
#         json.dump(playlists, f)
#
#     # Tab-separated file.
#     elif args.format == 'txt':
#         for playlist in playlists:
#             f.write(playlist['name'] + '\r\n')
#             for track in playlist['tracks']:
#                 f.write('{name}\t{artists}\t{album}\t{uri}\r\n'.format(
#                     uri=track['track']['uri'],
#                     name=track['track']['name'],
#                     artists=', '.join([artist['name'] for artist in track['track']['artists']]),
#                     album=track['track']['album']['name']
#                 ))
#             f.write('\r\n')
# log.print('Wrote file: ' + args.file)


#if __name__ == '__main__':
#    main()
