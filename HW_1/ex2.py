import adafruit_dht
import uuid
from time import time, sleep
from datetime import datetime
from board import D4
import sounddevice as sd
import tensorflow as tf
from scipy import signal
import numpy as np

# ------------------------------ Classes -----------------------------------------------------------------------
# Normalization of audio signal
class Normalization():
    def __init__(self, bit_depth):
        self.max_range = bit_depth.max

    def normalize_audio(self, audio):
        audio_float32 = tf.cast(audio, tf.float32)
        audio_normalized = audio_float32 / self.max_range

        return audio_normalized

    def normalize(self, audio, label):
        audio_normalized = self.normalize_audio(audio)

        return audio_normalized, label

# Computes the spectrogram of an audio signal
class Spectrogram():
    def __init__(self, sampling_rate, frame_length_in_s, frame_step_in_s):
        self.frame_length = int(frame_length_in_s * sampling_rate)
        self.frame_step = int(frame_step_in_s * sampling_rate)

    def get_spectrogram(self, audio):
        stft = tf.signal.stft(
            audio, 
            frame_length=self.frame_length,
            frame_step=self.frame_step,
            fft_length=self.frame_length
        )
        spectrogram = tf.abs(stft)

        return spectrogram

    def get_spectrogram_and_label(self, audio, label):
        spectrogram = self.get_spectrogram(audio)

        return spectrogram, label

# Detects if an audio signal is silent
class VAD():
    def __init__(
        self,
        sampling_rate,
        frame_length_in_s,
        frame_step_in_s,
        dBthres,
        duration_thres,
    ):
        self.frame_length_in_s = frame_length_in_s
        self.frame_step_in_s = frame_step_in_s
        self.spec_processor = Spectrogram(
            sampling_rate, frame_length_in_s, frame_step_in_s,
        )
        self.dBthres = dBthres
        self.duration_thres = duration_thres

    def is_silence(self, audio):
        spectrogram = self.spec_processor.get_spectrogram(audio)
        
        dB = 20 * tf.math.log(spectrogram + 1.e-6)
        energy = tf.math.reduce_mean(dB, axis=1)
        min_energy = tf.reduce_min(energy)

        rel_energy = energy - min_energy
        non_silence = rel_energy > self.dBthres
        non_silence_frames = tf.math.reduce_sum(tf.cast(non_silence, tf.float32))
        non_silence_duration = self.frame_length_in_s + self.frame_step_in_s * (non_silence_frames - 1)

        if non_silence_duration > self.duration_thres:
            return 0
        else:
            return 1



# ------------------------------------------Global Variables ---------------------------------------------

mac_address = hex(uuid.getnode()) # Get the MAC address of the Raspberry PI
dht_device = adafruit_dht.DHT11(D4) # Declare the existence of the humidity-temperature sensor and indicate the linking pin! (D4)
silence = True # State variable, output of VAD class
length_in_secs = 1 # Time interval between each callback execution (in seconds)
bit_depth = "int16" # Resolution of each sample
samplerate = 48000 # Sampling rate of the microphone
targetrate = 16000 # Target rate used to calculate the downsampling factor
downsampling_factor = samplerate/targetrate # Factor used to downsample an audio signal from 48 khz to 16 khz
data_collection_state = False # State variable, tells if data about temperature and humidity is being collected or not
oldT = None # Time stamp used to check if at least 5 seconds passed from the previous state change
normalization_processor = Normalization(tf.int16)
params = [16000, 0.008, 0.002, 20, 0.1] # VAD optimal hyperparameters - latency: 17.5 +/- 0.2 ms, accuracy: 97.67% - got from exercise 2.1 HW1
vad_processor = VAD(params[0], params[1], params[2], params[3],params[4])

# ------------------------------------------ Functions ---------------------------------------------

def callback(indata, frames, callback_time, status):
    global silence
    global data_collection_state
    
    # If there was no change of state or more than 5 seconds passed from the previous change of state, check if there is silence, else do nothing
    if oldT is None or time() - oldT >= 5: # oldT is None until the first change of state happens
        # Audio preprocessing (casting, downsampling, conversion to tensor, squeezing, normalization)
        audio = indata.astype(np.float32)
        audio = signal.resample_poly(audio, up=1, down=downsampling_factor)
        audio = tf.convert_to_tensor(audio)
        audio = tf.squeeze(audio)
        audio = normalization_processor.normalize_audio(audio)
        # Check if the processed audio signal is silent
        silence = vad_processor.is_silence(audio) 
        if not silence: # Change of state if there is no silence
            data_collection_state = not data_collection_state
            print(f'Data collection: {data_collection_state}') 
    else: 
        silence = 1 # Ignore audio  


# ------------------------------------------ Main ---------------------------------------------

# Starts audio recording
with sd.InputStream(device = 1, channels = 1, dtype = bit_depth, samplerate = samplerate, blocksize = length_in_secs*samplerate, callback = callback):
    print('AUDIO RECORDING STARTED')
    # Store timestamp when there is no silence
    while True:
        if not silence:
            oldT = time() # save the time at which the state changes, in order to start counting 5 seconds until the next command
        # If data collection is enabled, collect data
        if data_collection_state:
            if time() - timestamp >= 2:
                timestamp = int(time())
                formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f') # Convert the timestamp to human-readable time
                try:
                    # Get temperature and humidity from the sensor, store them in the database and print them
                    temperature = dht_device.temperature
                    humidity = dht_device.humidity
                    print(f'{formatted_time} - {mac_address}:temperature = {temperature}')
                    print(f'{formatted_time} - {mac_address}:humidity = {humidity}')
                except:
                    # If the connection fails, print an error message and try to restart the connection
                    # This is done because the connection is generally unrealiable
                    print('Sensor failure')
                    dht_device.exit()
                    dht_device = adafruit_dht.DHT11(D4)

    
    

    
