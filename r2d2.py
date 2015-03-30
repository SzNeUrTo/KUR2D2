# -*- coding: utf-8 -*-
import pyaudio
import wave
import audioop
from collections import deque
import os
import urllib2
import urllib
import time
import math
import re
import tkMessageBox
import httplib
import json
import sys
import subprocess
import requests
from practicum import findDevices
from peri import PeriBoard
from time import sleep
from math import floor

devs = findDevices()
if len(devs) == 0:
    print "*** No MCU board found."
    exit(1)
b = PeriBoard(devs[0])

def TextToSpeech(Ask) :
    #TestAsk.py
    try :
        url = 'http://203.151.27.86/asuku/client.php'
        postData = {'question': Ask}
        req = requests.post(url, postData)
        #print 'ans : ' + str(req.text.encode('utf-8'))

        #Download.py
        #print "A --> " + Ans
        #Debug Error
        Ans = Ans.replace(" ", "%20")
        # print "OK"
        isEngLang = False
        countEng = 0
        for x in Ans :
            if x in ['A','B','C','D','E','F','G','H','I', \
                           'J','K','L','M','N','O','P','Q','R','S',\
                           'T','U','V','W','X','Y','Z','a','b','c',\
                           'd','e','f','g','h','i','j','k','l','m','n',\
                            'o','p','q','r','s','t','u','v','w','x','y','z'] :
                countEng += 1


        if countEng > len(Ans) - countEng :
                isEngLang = True
        if isEngLang or True:
            url = "http://translate.google.com/translate_tts?tl=en-Us&q="+Ans
        else :
            url = "http://translate.google.com/translate_tts?tl=th&q="+Ans

        request = urllib2.Request(url)
        request.add_header('User-agent', 'Mozilla/5.0') 
        opener = urllib2.build_opener()

        fff = open("999.mp3", "wb")
        fff.write(opener.open(request).read())
        fff.close()

        #playsound2.py
        audio_file = "999.mp3"
        return_code = subprocess.call(["afplay", audio_file])
    except Exception as e:
        Ans = "Say Again "+str(e)
    Ans = Ans.replace("%20", " ")
    return Ans


#import win32com.client as comclt
END_LOOP = True
#LANG_CODE = 'en-US'
LANG_CODE = 'th'
Command = ''
GOOGLE_SPEECH_URL = "https://www.google.com/speech-api/v2/recognize?output=json&lang=%s&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"  % (LANG_CODE)

FLAC_CONV = 'flac -f'  # We need a WAV to FLAC converter. flac is available
                       # on Linux

# Microphone stream config.
CHUNK = 1024  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
THRESHOLD = 1500  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1.5  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 1  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.


def audio_int(num_samples=50):
    """ Gets average audio intensity of your mic sound. You can use it to get
        average intensities while you're talking and/or silent. The average
        is the avg of the 20% largest intensities recorded.
    """

    print "Getting intensity values from mic."
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    values = [math.sqrt(abs(audioop.avg(stream.read(CHUNK), 4))) 
              for x in range(num_samples)] 
    values = sorted(values, reverse=True)
    r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
    print " Finished "
    print " Average audio intensity is ", r
    stream.close()
    p.terminate()
    return r


def listen_for_speech(threshold=THRESHOLD, num_phrases=1):
    """
    Listens to Microphone, extracts phrases from it and sends it to 
    Google's TTS service and returns response. a "phrase" is sound 
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process 
    (-1 for infinite). 
    """
    try :
    #Open stream
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print "* Listening mic. "
        audio2send = []
        cur_data = ''  # current chunk  of audio data
        rel = RATE/CHUNK
        slid_win = deque(maxlen=SILENCE_LIMIT * rel)
        #Prepend audio from 0.5 seconds before noise was detected
        prev_audio = deque(maxlen=PREV_AUDIO * rel) 
        started = False
        n = num_phrases
        response = []

        while (num_phrases == -1 or n > 0):
            cur_data = stream.read(CHUNK)
            slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
            #print slid_win[-1]
            if(sum([x > THRESHOLD for x in slid_win]) > 0):
                if(not started):
                    print "Starting record of phrase"
                    started = True
                audio2send.append(cur_data)
            elif (started is True):
                print "Finished"
                # The limit was reached, finish capture and deliver.
                filename = save_speech(list(prev_audio) + audio2send, p)
                # Send file to Google and get response
                r = stt_google_wav(filename) 
                #if num_phrases == -1:
                #    print "Response", r
                #else:
                #    response.append(r)

                # Reset all
                started = False
                slid_win = deque(maxlen=SILENCE_LIMIT * rel)
                prev_audio = deque(maxlen=0.5 * rel) 
                audio2send = []
                n -= 1
                #print "Listening ..."
            else:
                prev_audio.append(cur_data)

        # Remove temp file. Comment line to review.
        filenameflac = filename.split('.')[0] + '.flac'
        os.remove(filename)
        os.remove(filenameflac) 

        print "* Job Finished Delete File"
        stream.close()
        p.terminate()
    except :
        r = ""
        print "Bombbb Say"

    return r

def save_speech(data, p):
    """ Saves mic data to temporary WAV file. Returns filename of saved 
        file """

    filename = 'output_'+str(int(time.time()))
    # writes data to WAV file
    data = ''.join(data)
    wf = wave.open(filename + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)  # TODO make this value a function parameter?
    wf.writeframes(data)
    wf.close()
    return filename + '.wav'


def stt_google_wav(audio_fname):
    """ Sends audio file (audio_fname) to Google's text to speech 
        service and returns service's response. We need a FLAC 
        converter if audio is not FLAC (check FLAC_CONV). """

    print "Sending ", audio_fname
    #Convert to flac first
    filename = audio_fname
    del_flac = False
    if 'flac' not in filename:
        del_flac = True
        print "Converting to flac"
        print FLAC_CONV + filename
        os.system(FLAC_CONV + ' ' + filename)
        filename = filename.split('.')[0] + '.flac'


    f = open(filename, 'rb')
    flac_cont = f.read()
    f.close()

    # Headers. A common Chromium (Linux) User-Agent
    hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
    'Content-type': 'audio/x-flac; rate=16000'}    
    req = urllib2.Request(GOOGLE_SPEECH_URL, data=flac_cont, headers=hrs)
    print "Sending request to Google STT"
    p = urllib2.urlopen(req)
    response = p.read()
    response = response.split('\n', 1)[1]
    try :
        res = json.loads(response)['result'][0]['alternative'][0]['transcript']
    except:
        print "Json Error"
        res= ''

    #pattern = "(transcript\":\")([^\"])(\")"
    #m = re.match(pattern,str(response))
    try:
        print "The Answer is : ["+res.encode('UTF-8')+"]"
    except:
        print "BOMB"
        res = ""
    return res

def turnRight(dutycycle):
    b.setMotor(1, dutycycle) # 01

def turnLeft(dutycycle):
    b.setMotor(2, dutycycle) # 10

def forward(dutycycle):
    b.setMotor(0, dutycycle) # 00

def backWard(dutycycle):
    b.setMotor(3, dutycycle) # 11

def stop():
    b.setMotor(0, 0) # pwm = 0

def slow(lastDir, dutycycle):
    b.setMotor(lastDir, dutycycle)

def goOn(lastDir, dutycycle):
    b.setMotor(lastDir, dutycycle)

if(__name__ == '__main__'):
#def running():
    Command = "GoToLoop"
    dutycycle = 255
    lastDir = 0
    while(Command != 'exit') : 
        Command = listen_for_speech()
        if (Command != 'exit') :
            if(Command != "") :
                print "Q --> " + Command
        else :
            break
        if 'ขวา'.decode('utf-8') in Command :
            print 'Right'
            dutycycle = 255
            turnRight(dutycycle)
            lastDir = 1
        elif 'าย'.decode('utf-8') in Command :
            print 'Left'
            dutycycle = 255
            turnLeft(dutycycle)
            lastDir = 2
        elif 'น้า'.decode('utf-8') in Command :
            print 'Forward'
            dutycycle = 255
            forward(dutycycle)
            lastDir = 0
        elif 'ลัง'.decode('utf-8') in Command :
            print 'BackWard'
            dutycycle = 255
            backWard(dutycycle)
            lastDir = 3
        elif 'ยุ'.decode('utf-8') in Command or 'youtube' in Command:
            print 'Stop'
            stop()
        elif 'ก'.decode('utf-8') in Command or 'อน'.decode('utf-8') in Command or 'ชา'.decode('utf-8') in Command \
        or 'ช้'.decode('utf-8') in Command : #ช้าก่อน
            print 'Slow' # 10%
            dutycycle = floor(0.8*dutycycle)
            slow(lastDir, int(dutycycle))
        elif 'ไปต่อ'.decode('utf-8') in Command :
            dutycycle = 255
            goOn(lastDir, int(dutycycle))

        os.system('rm *.wav')
        os.system('rm *.flac')
