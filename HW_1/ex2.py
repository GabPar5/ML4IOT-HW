import adafruit_dht
import uuid
from time import time, sleep
from datetime import datetime
from board import D4
import sounddevice as sd
from preprocessing import Normalization, Spectrogram
from reader import AudioReader
import tensorflow as ts
from scipy import signal

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




def callback(indata, frames, callback_time, status):
    global silence
    global oldT 
    global data_collection_state

    # indata --> flie audio
    audio, label = audio_reader.get_audio_and_label(indata)
    audio = tf.cast(audio, tf.float32)
    audio_resampled = signal.resample_poly(audio, up=1, down=downsampling_factor)

    
    audio, label = normalization.normalize(audio, label)
    audio = signal.resample_poly(audio)
    audio = tf.squeeze(audio)

    if oldT is None or time() - oldT >= 5*(10**6):
        silence = vad_processor.is_silence(audio)
    else: 
        silence = 1

    if data_collection_state:
        timestamp_ms = int(time()*1000)
        formatted_time = datetime.fromtimestamp(timestamp_ms/1000).strftime('%Y-%m-%d %H:%M:%S.%f') # Convert the timestamp to human-readable time
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

silence = True
length_in_secs = 2
bit_depth = "int16"
samplerate = 48000
downsampling_factor = 48/16
data_collection_state = False
oldT = None
audio_reader = AudioReader(tf.int16)
normalization = Normalization(tf.int16)
vad_processor = VAD() # vad(hyperparameter) with hyperparameter to define
with sd.InputStream(device = 1, channels = 1, dtype = bit_depth, samplerate = samplerate, blocksize = length_in_secs*samplerate, callback = callback):
    if not silence:
        oldT = time()
        if not data_collection_state:
            data_collection_state = True
            print ('Data collection started')
        else:
            data_collection_state = False
            print('Data collection stopped')

    
    

    