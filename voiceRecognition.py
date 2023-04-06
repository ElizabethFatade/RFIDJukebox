"""import numpy as np
from scipy.io import wavfile
import pyaudio
def sound(array, fs=8000):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=len(array.shape), rate=fs, output=True)
    stream.write(array.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()
def record(duration=3, fs=8000):
    nsamples = duration*fs
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=fs, input=True,
                    frames_per_buffer=nsamples)
    buffer = stream.read(nsamples, exception_on_overflow = False)
    array = np.frombuffer(buffer, dtype='int16')
    stream.stop_stream()
    stream.close()
    p.terminate()
    return array"""

import pyaudio
import wave 
from array import array
from struct import pack
import speech_recognition as sr

def record(outputFile):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    DURATION = 5

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    #print("Recording....")
    frames = []
    for i in range(0, int(RATE/CHUNK *DURATION)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(outputFile, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def play(file):
    CHUNK = 1024
    wf = wave.open(file, 'rb')
    p=pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while len(data)>0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()

def speechRecognition():
    """r = sr.Recognizer()
    audioF = sr.AudioFile(audioFile)
    with audioF as source:
        audio = r.record(source)
    print(type(audio))
    r.recognize_google(audio)"""

    r = sr.Recognizer()                    
    #keyWord1 = 'DJ'
    keyWord1 = 'Hello'
    keyWord2 = 'play track'
    playCommand = False
    attempts = 0
    startUpAttempts = 0

    with sr.Microphone() as source:
        print('Please start speaking...\n')
        while True and startUpAttempts != 3:
            print("heey")
            startUpAttempts += 1
            audio1 = r.listen(source, 5)
            try:
                print("hey")
                text1 = r.recognize_google(audio1)
                if keyWord1.lower() in text1.lower():
                    playCommand = True
                    print('Start up Keyword detected in the speech.')
                    print('Please give play command.')

                    while playCommand and attempts != 3:
                        attempts += 1
                        audio2 = r.listen(source, 5)
                        try:
                            text2 = r.recognize_google(audio2)
                            if keyWord2.lower() in text2.lower():
                                print('Keyword detected in the speech.')
                                print(text2)
                                playCommand = False
                                startUpAttempts = 3
                                
                                text2_list = text2.split()
                                trackSelect = text2_list[-1]
                                print(trackSelect)
                                
                                try:
                                    trackNum = int(trackSelect)
                                    print(trackNum)
                                    return trackNum
                                except ValueError:
                                    print("No valid integer following /'Play track/'")
                                    return -1
                               
                            else:
                                if attempts != 3:
                                    print('Wrong command.')
                                    print('Please speak again.')
                                    print('in else')
                                else:
                                    print("done")
               
                        except Exception as e:
                            if attempts != 3:
                                print('in except')
                                print('Wrong command.')
                                print('Please speak again.')
                            else:
                                print("done")
                   
                    if attempts == 3:
                        startUpAttempts = 3
                else:
                    if startUpAttempts != 3:
                        print('Please speak again.')
                        print('in else')
                    else:
                        print("done")

            except Exception as e:
                if startUpAttempts != 3:
                    print('in except')
                    print('Please speak again.')
                else:
                    print("done")
        return -1


        """print('Please start speaking..\n')
        while True:
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                if keyWord.lower() in text.lower():
                    print('Keyword detected in the speech.')
                    print('Please speak again.')
            except Exception as e:
                print('Please speak again.')"""

if __name__ == "__main__":
    #sound(data, fs=4000) # The do note was recorded using a lower sampling frequency of 4000
    #my_recording = record() # Say something wise
    #sound(my_recording)
    #record('output1.wav')
    #play('output1.wav')
    speechRecognition()
