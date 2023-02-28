"""
Connecting and using the spotify API

A map is created with RFID ID as the key and spotify song as the value
    - Function to create mapping: init function at startup
    - Function to update mapping: updateMap
    - Function to play song
"""
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
from decouple import config

"""
    Creates the spotify agent that connects to the spotify API
    Functions: 
        updateMap: int RFID, string songName, string artist
        playSong: int RFID
"""
class SpotifyApi:
    
    def __init__(self):
        CID = config('CID', default='')
        CID_SECRET = config('CID_SECRET', default='')
        SCOPE = config('SCOPE', default='')
        USERNAME = config('USERNAME', default='')
        REDIRECT_URI = config('REDIRECT_URI', default='')

        token = util.prompt_for_user_token(USERNAME, SCOPE, CID, CID_SECRET, REDIRECT_URI)
        self.sp = spotipy.Spotify(auth=token)
       
        self.songMapping = {
            1: "",
            2: "",
            3: "",
            4: "",
            5: "",
            6: "",
            7: "",
            8: "",
            9: "",
            10: "",
        }

    """
    This function updates an RFID tag with the new song to be programmed on it
    @param rfidID: This is the ID of the rfid tag to be updated
    @param songName: This is the song name to be programmed onto the card and used in spotify search
    @param artist: This is the artist of the desired song and used in spotify search
    
    @return None
    """
    def updateMap(self, rfidID=None, songName=None, artist=None):
        for i in range(0,100,50):
            track_results = self.sp.search(q='track:'+songName, type='track', limit=50,offset=1)
            for i, t in enumerate(track_results['tracks']['items']):
                if t['artists'][0]['name'].lower() == artist.lower() and t['name'].lower() == songName.lower():
                    self.songMapping[rfidID] = t['uri']

    """
    This function obtains the song stored on an rfid tag and plays it on spotify
    @param rfidID: This is the ID of the rfid tag with the desired song to play

    @return None
    """
    def playSong(self, rfidID):
        try:
            track = self.songMapping[rfidID]
            devices = self.sp.devices()
            print(devices['devices'][0]['id'])
            playTrack = self.sp.start_playback(device_id=devices['devices'][0]['id'], uris=[track])
            
            #return playTrack
        except:
            print("An exception occurred")

# MAIN
if __name__ == "__main__":
    sp = SpotifyApi()

    sp.updateMap(1, "Umbrella", "Rihanna")
    sp.updateMap(2, "Wildest Dreams", "Taylor Swift")
    sp.updateMap(3, "Work Out", "J. Cole")
    sp.updateMap(4, "Gone Girl", "SZA")
    sp.updateMap(5, "Traitor", "Olivia Rodrigo")

    b = sp.playSong(3)
    print(b)

