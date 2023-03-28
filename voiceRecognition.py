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

    print("Recording....")
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

def speechRecognition(audioFile):
    r = sr.Recognizer()
    audioF = sr.AudioFile(audioFile)
    with audioF as source:
        audio = r.record(source)

    print(type(audio))
    r.recognize_google(audio)

if __name__ == "__main__":
    #sound(data, fs=4000) # The do note was recorded using a lower sampling frequency of 4000
    #my_recording = record() # Say something wise
    #sound(my_recording)
    record('output1.wav')
    play('output1.wav')
    speechRecognition('output1.wav')