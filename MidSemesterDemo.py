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

import mraa
import time
import sys

# initialize UART
uart = mraa.Uart("/dev/ttyS4")
# uart = mraa.Uart("~/../../dev/ttyS4")

# set UART parameters
uart.setBaudRate(9600)
uart.setMode(8, mraa.UART_PARITY_NONE, 1)
uart.setFlowcontrol(False, False)

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
        
        """
    Card UIDs:
    1 - D8 28 15 21 --> 
    2 - 38 D5 13 21 --> 
    3 - AB 01 0E 21 --> 
    4 - BB 8F 79 B2 --> 
    5 - 48 E8 80 B2 --> 
    6 - EB 84 9B 5A --> 
    7 - BB D7 74 B2 --> 
    8 - 88 C0 AC 52 --> 
    9 - 48 05 ED 3D --> 
    0 - EB D8 EA 3D --> 
    """
        self.idMap = {
            1: "DB 28 15 21",
            2: "3B D5 13 21",
            3: "AB 01 0E 21",
            4: "BB 8F 79 B2",
            5: "4B E8 80 B2",
            6: "EB 84 9B 5A",
            7: "BB D7 74 B2",
            8: "1E FC C9 10",
            9: "4B 05 ED 3D",
            0: "EB DB EA 3D"
        }
        
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
            0: ""
        }
    
    def getID(self, UID):
        n = ""
        for num, uid in self.idMap.items():
            if uid.replace(" ", "") == UID.replace(" ", ""):
                n = num
        print(n)
        return n
    """
    This function updates an RFID tag with the new song to be programmed on it
    @param rfidID: This is the ID of the rfid tag to be updated
    @param songName: This is the song name to be programmed onto the card and used in spotify search
    @param artist: This is the artist of the desired song and used in spotify search
    
    @return None
    """
    def updateMap(self, rfidID=None, songName=None, artist=None):
        try:
            for i in range(0,100,50):
                track_results = self.sp.search(q='track:'+songName, type='track', limit=50,offset=1)
                for i, t in enumerate(track_results['tracks']['items']):
                    if t['artists'][0]['name'].lower() == artist.lower() and t['name'].lower() == songName.lower():
                        self.songMapping[rfidID] = t['uri']
        except:
            print("An exception occurred")
    
    def getCurrentlyPlaying(self):
        print(self.sp.current_user_playing_track())
        print(True)
        
    """
    This function obtains the song stored on an rfid tag and plays it on spotify
    @param rfidID: This is the ID of the rfid tag with the desired song to play

    @return None
    """
    def playSong(self, rfidID):
        #try:
        track = self.songMapping[rfidID]
        devices = self.sp.devices()
        print(devices['devices'][0]['id'])
        playTrack = self.sp.start_playback(device_id=devices['devices'][0]['id'], uris=[track])
            
            #return playTrack
        #except:
            #print("An exception occurred")

# MAIN
if __name__ == "__main__":
    sp = SpotifyApi()

    """sp.updateMap(1, "Umbrella", "Rihanna")
    sp.updateMap(2, "Wildest Dreams", "Taylor Swift")
    sp.updateMap(3, "Work Out", "J. Cole")
    sp.updateMap(4, "Gone Girl", "SZA")
    sp.updateMap(5, "Traitor", "Olivia Rodrigo")"""
    
    """
    Card UIDs:
    1 - D8 28 15 21 --> 
    2 - 3B D5 13 21 --> 
    3 - AB 01 0E 21 --> 
    4 - BB 8F 79 B2 --> 
    5 - 48 E8 80 B2 --> 
    6 - EB 84 9B 5A --> 
    7 - BB D7 74 B2 --> 
    8 - 88 C0 AC 52 --> 
    9 - 48 05 ED 3D --> 
    0 - EB D8 EA 3D --> 
    """
    
    #sp.getCurrentlyPlaying()
    #1
    sp.updateMap(1, "Rock that Body", "Black Eyed Peas")
    #2
    sp.updateMap(2, "Boy's a liar", "PinkPantheress")
    #3
    sp.updateMap(3, "Waiting For Love", "Avicii")
    #4
    sp.updateMap(4, "Vete", "Bad Bunny")
    #5
    sp.updateMap(5, "Traitor", "Olivia Rodrigo")#
    #6
    sp.updateMap(6, "Get Lucky (feat. Pharrell Williams & Nile Rodgers)", "Daft Punk")
    #7
    sp.updateMap(7, "Wonderland", "Taylor Swift")
    #8
    sp.updateMap(8, "Wildest Dreams", "Taylor Swift")
    #9
    sp.updateMap(9, "Gone Girl", "SZA")
    #10
    sp.updateMap(0, "Work Out", "J. Cole")
    
    #sp.playSong("D8 28 15 21")
    
    
    
    # Code to catch UID here
    while True:
        #Wait for data to be available
        while uart.dataAvailable() == 0:
            pass
    
        #Read the data
        data = uart.readStr(1)
        print(data, end = '')
        
        # To grab card UID
        if data == ':':
            UID = uart.readStr(20)
            print(UID)
            uid = sp.getID(UID)
            print(uid)
            b = sp.playSong(uid)
            print(b)
            

