import argparse
import os
import struct
from datetime import datetime
from threading import Thread
import time
import numpy as np
import pvporcupine
import pyaudio
import soundfile
from PIL import Image, ImageTk
from playsound import playsound
from multiprocessing import Process
import sys
from gtts import gTTS
import speech_recognition as sr
from io import BytesIO
import webbrowser
import urllib.request
import urllib.parse
import re
from youtube_search import YoutubeSearch
import keyboard
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.utils import timestamps


def fileRead(File):
    f = open(File, "r")
    str=f.readline()
    f.close()
    return str 

def fileWrite(File,str):
    f = open(File, "w")
    f.write(str)
    f.close()

def hotWord():
    """
     Creates an input audio stream, instantiates an instance of Porcupine object, and monitors the audio stream for
     occurrences of the wake word(s). It prints the time of detection for each occurrence and the wake word.
    """
    try:
        porcupine = None
        pa = None
        audio_stream = None
        porcupine = pvporcupine.create(keyword_paths=['assist/PvtAsset/violet_windows_2021-04-29-utc_v1_9_0.ppn'],sensitivities=[1])
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length)

        print('Listening {')

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            result = porcupine.process(pcm)
            if result >= 0:
                print(result)
                porcupine.delete()
                audio_stream.close()
                pa.terminate()
                print("Going to main")
                return False
    except :
        print('An exception was thrown but we will try again')
        if porcupine is not None:
            porcupine.delete()

        if audio_stream is not None:
            audio_stream.close()

        if pa is not None:
            pa.terminate()
        return True

"""          
def disp():
    print("Disp reached")
    print("audio play")
    root = tk.Tk()
    root.image = tk.PhotoImage(file='assist\Assets\IN.png')
    label = tk.Label(root, image=root.image, bg='white')
    root.overrideredirect(True)
    root.geometry("+1+1")
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", False)
    root.wm_attributes("-transparentcolor", "white")
    label.pack()
    root.after(5000, lambda: root.destroy())
    root.after(1,multi=multi+1)
    label.mainloop()
"""

def sound(str):
    print("Play Sound")
    tts = gTTS(str, lang='en',tld="co.in")
    tts.save("speech.mp3")
    del tts
    playsound('speech.mp3')
    if os.path.exists("speech.mp3"):
        os.remove("speech.mp3")

def speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        r.energy_threshold=2000
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
        print("Intake stopped.")
    WIT_AI_KEY =fileRead("assist\PvtAsset\WIT_Token.txt")   # Wit.ai keys are 32-character uppercase alphanumeric strings
    try:
        print("Processing now")
        str=r.recognize_wit(audio, key=WIT_AI_KEY)
        del r
        print(str)
        return str
    except sr.UnknownValueError:
        print("Wit.ai could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Wit.ai service; {0}".format(e))

def webPlay(string) :
    print("trying to open top result for"+string)
    talk="trying to open top result for"+string
    sound(talk)
    results = YoutubeSearch(string, max_results=1).to_dict()
    string="www.youtube.com"+results[0]["url_suffix"]
    webbrowser.open(string)
    time.sleep(8)#Increase for low speed. Decrease for higher speed of computer/Internet connection
    print("Getting keypress")
    keyboard.press_and_release('space')

def STTtest():   
    print("Start speaking")
    sound(speech())

def WeatherDetect(state):
    try:
        try:
            loc=fileRead("assist\PvtAsset\Location.txt")
        except:
            sound("Hey looks like there is a little problem with the location file. Type in your location to continue")
            LocIn=input("Enter location: ")
            fileWrite("assist\PvtAsset\Location.txt",LocIn)
            loc=fileRead("assist\PvtAsset\Location.txt")
        print("Location is "+loc)
        #here is the actual weather detection code
        token=fileRead("assist\PvtAsset\OpenWeather_token.txt")
        print("Open Weather token is "+token)
        print("Location is loc")
        if(state==0):
            owm = OWM(token)
            mgr = owm.weather_manager()
            observation = mgr.weather_at_place(loc)
            w = observation.weather

            print("Weather object created")

            # Search for current weather in London (Great Britain) and get details
            observation = mgr.weather_at_place(loc)
            print("observation fetched")
            w = observation.weather
            print("weather found")
            print(w.detailed_status)         # 'clouds'
            print(w.wind())                  # {'speed': 4.6, 'deg': 330}
            print(w.humidity)                # 87
            print(w.temperature('celsius'))  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
            print(w.rain)
            print(w.clouds)                  # 75
            Tfeels=str(w.temperature("celsius")['feels_like'])
            WeatherReport="The weather is "+w.detailed_status+". It feels like "+Tfeels+" degrees celcius"
            print("trying to print the temps")
            print(WeatherReport)
            sound(WeatherReport)
        if(state==1):
            sound("Real sorry but I can't forecast weather for now. MAybe wait for an update?")
            return
            owm = OWM(token)  
            mgr = owm.weather_manager()
            daily_forecast = mgr.forecast_at_place(loc, 'daily').forecast
            print("forecast get")
            nr_of_weathers = len(daily_forecast)
            for weather in daily_forecast:
                print(weather.get_reference_time('iso'))
                print(weather.get_status())

        #Code end
    except Exception as e: # work on python 3.x
        print('Weather fetch error '+ str(e))






#Main loopb
while True:
    try:
        state=True
        state=hotWord()
        if state:
            continue
        print("Hot word Detected")
        sound("Hey! What Can I do for you?")
        command=speech()
        print("Command recived is  "+command)
        res = command.split()
        if res[0]=="play":
            res.pop(0)
            query=' '.join(res)
            webPlay(query)
            del command
            del res
            del query
            continue
        elif res[0]=="nothing":
            del command
            del res
            sound("Ok. I will be waiting for your command!")
            continue
        elif res[0]=="sleep":
            del res
            break
        elif any(x for x in res if x=="weather") and (any(x for x in res if x=="tell") or any(x for x in res if x=="what")):
            state=0
            if any(x for x in res if x=="tomorrow") or any(x for x in res if x=="tomorrow's"):
                state=1
            WeatherDetect(state)
    except Exception as e: # work on python 3.x
        print('Fatal Error '+ str(e))
        print("Sorry!. An error occured , Lets try that again")
        sound("Sorry! An error occured , Lets try that again")
sound("Good Night.")

#DONE!!
#NOTES: UPDATE DISP FUNCTION(Or maybe not!) 