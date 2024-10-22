import os
from time import time
import sounddevice as sd
from scipy.io.wavfile import write
import argparse


# The callback function is executed every x seconds during the recording
# We can store audio data while recording it!
def callback(indata, frames, callback_time, status):
    global store_audio
    #global params.samplerate

    # If the variable "store_audio" is false the storage is dropped
    if store_audio is True:
        # Store audio every "blocksize" time
        timestamp = time()
        write(f'{timestamp}.wav', params.samplerate, indata)
        filesize_in_bytes = os.path.getsize(f'{timestamp}.wav')
        filesize_in_kb = filesize_in_bytes/1024
        print(f'Size: {filesize_in_kb:.2f} KB')

# The sounddevice library makes possible to record audio from a microphone with the 'with' statement
# Remember that dtype is the bit depth and samplerate is the sample rate in Hz,
# while device and channels are by default 1 (unless you plug in a microphone with multiple channels/multiple microphones)


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--samplerate", choices = [44100, 48000], default = 48000, type = int, help="Sampling Rate in Hz")
parser.add_argument("-b", "--bit_depth", choices = ["int16", "int32"], default = "int32", type = str, help="Bit depth considered during sampling of recordings")
parser.add_argument("-l", "--length_in_secs", default = 1, type = int, help="Recording duration in seconds")
params = parser.parse_args()

store_audio = True
with sd.InputStream(device = 1, channels = 1, dtype = params.bit_depth, samplerate = params.samplerate, blocksize = params.length_in_secs*params.samplerate, callback = callback):
    print('Recording started')
    while True:
        key = input()
        if key in ['q','Q']: # Disable recording of audio if the key 'q' is pressed
            print('Recording stopped shut up')
            break
        if key in ['p','P']: # Disable storage of audio if the key 'p' is pressed
            store_audio = not store_audio
        #continue # Records continuously
