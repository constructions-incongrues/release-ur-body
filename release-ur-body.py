#! /usr/bin/env python 
import os
import discogs_client.client as DiscogsClient
import discogs_client.models as DiscogsModels
import requests
import json

class ReleaseUrBody:
    def __init__(self):
        self.discogs_client = DiscogsClient.Client('MyApp/0.1', user_token="YOUR_DISCOGS_TOKEN")
        self.bandcamp_client = requests.Session()
        self.bandcamp_client.headers.update({
            'Authorization': 'Bearer YOUR_BANDCAMP_TOKEN',
            'Content-Type': 'application/json',
        })

    def analyze_folder(self, folder_path):
        tracks = []
        for file in os.listdir(folder_path):
            if file.endswith('.mp3') or file.endswith('.wav'):
                track_number, artist, title = file.split(' - ')
                tracks.append({
                    'track_number': int(track_number),
                    'artist': artist,
                    'title': title,
                })
        return tracks

    def create_discogs_release(self, folder_path):
        release_name = os.path.basename(folder_path)
        tracks = self.analyze_folder(folder_path)
        data = {
            'id':  None,
            'title': release_name,
            'tracks': tracks,
        }
        release = DiscogsModels.Release(self.discogs_client, data)
        response = release.save()
        
        return response.json()

    def update_bandcamp_release(self, release_id, tracks):
        data = {
            'tracks': tracks,
        }
        response = self.bandcamp_client.put(f'https://bandcamp.com/api/releases/{release_id}', data=json.dumps(data))
        return response.json()

    def create_bandcamp_release(self, release_name, tracks):
        data = {
            'name': release_name,
            'tracks': tracks,
        }
        response = self.bandcamp_client.post('https://bandcamp.com/api/releases', data=json.dumps(data))
        return response.json()

    def command_line_interface(self):
        import argparse

        parser = argparse.ArgumentParser(description='Release your music on Discogs, Musicbrainz and Bandcamp.')
        parser.add_argument('folder_path', help='The path to the folder containing your music files.')
        parser.add_argument('--discogs-release-id', help='The ID of the Discogs release to update.')
        parser.add_argument('--bandcamp-release-id', help='The ID of the Bandcamp release to update.')
        args = parser.parse_args()

        if args.discogs_release_id:
            tracks = self.analyze_folder(args.folder_path)
            self.update_bandcamp_release(args.discogs_release_id, tracks)
        elif args.bandcamp_release_id:
            tracks = self.analyze_folder(args.folder_path)
            self.update_bandcamp_release(args.bandcamp_release_id, tracks)
        else:
            release_name = os.path.basename(args.folder_path)
            tracks = self.analyze_folder(args.folder_path)
            discogs_release = self.create_discogs_release(args.folder_path)
            bandcamp_release = self.create_bandcamp_release(release_name, tracks)

if __name__ == '__main__':
    ReleaseUrBody().command_line_interface()