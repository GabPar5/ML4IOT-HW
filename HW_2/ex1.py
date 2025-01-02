import adafruit_dht
import uuid
from time import time
from datetime import datetime
from board import D4
import sounddevice as sd
import tensorflow as tf
from scipy import signal
import numpy as np
import tensorflow as tf
import argparse
import redis


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

# Computes the log-Mel spectrogram of an audio signal
class MelSpectrogram():
    def __init__(
        self, 
        sampling_rate,
        frame_length_in_s,
        frame_step_in_s,
        num_mel_bins,
        lower_frequency,
        upper_frequency
    ):
        self.spectrogram_processor = Spectrogram(sampling_rate, frame_length_in_s, frame_step_in_s)
        num_spectrogram_bins = self.spectrogram_processor.frame_length // 2 + 1

        self.linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
            num_mel_bins=num_mel_bins,
            num_spectrogram_bins=num_spectrogram_bins,
            sample_rate=sampling_rate,
            lower_edge_hertz=lower_frequency,
            upper_edge_hertz=upper_frequency
        )

    def get_mel_spec(self, audio):
        spectrogram = self.spectrogram_processor.get_spectrogram(audio)
        mel_spectrogram = tf.matmul(spectrogram, self.linear_to_mel_weight_matrix)
        log_mel_spectrogram = tf.math.log(mel_spectrogram + 1.e-6)

        return log_mel_spectrogram

    def get_mel_spec_and_label(self, audio, label):
        log_mel_spectrogram = self.get_mel_spec(audio)

        return log_mel_spectrogram, label

# Computes the MFCCs
class MFCC():
    def __init__(
        self, 
        sampling_rate,
        frame_length_in_s,
        frame_step_in_s,
        num_mel_bins,
        lower_frequency,
        upper_frequency,
        num_coefficients
    ):
        self.mel_spec_processor = MelSpectrogram(
            sampling_rate, frame_length_in_s, frame_step_in_s, num_mel_bins, lower_frequency, upper_frequency
        )
        self.num_coefficients = num_coefficients

    def get_mfccs(self, audio):
        log_mel_spectrogram = self.mel_spec_processor.get_mel_spec(audio)
        mfccs = tf.signal.mfccs_from_log_mel_spectrograms(log_mel_spectrogram)
        mfccs = mfccs[..., :self.num_coefficients]

        return mfccs

    def get_mfccs_and_label(self, audio, label):
        mfccs = self.get_mfccs(audio)

        return mfccs, label

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
timestamp = None # Time stamp used to check if at least 2 seconds passed from the previous data collection
length_in_secs = 1 # Time interval between each callback execution (in seconds)
bit_depth = "int16" # Resolution of each sample
samplerate = 48000 # Sampling rate of the microphone
targetrate = 16000 # Target rate used to calculate the downsampling factor
downsampling_factor = samplerate/targetrate # Factor used to downsample an audio signal from 48 khz to 16 khz
data_collection_state = False # State variable, tells if data about temperature and humidity is being collected or not
oldT = None # Time stamp used to check if at least 5 seconds passed from the previous state change
normalization_processor = Normalization(tf.int16)
vad_params = [16000, 0.008, 0.002, 20, 0.1] # VAD optimal hyperparameters - latency: 17.5 +/- 0.2 ms, accuracy: 97.67% - got from exercise 2.1 HW1
vad_processor = VAD(vad_params[0], vad_params[1], vad_params[2], vad_params[3], vad_params[4])
mfcc_params = [16000, 0.016, 0.016, 30, 20, 6000, 30] # Preprocessing optimal hyperparameters
mfcc_processor = MFCC(mfcc_params[0], mfcc_params[1], mfcc_params[2], mfcc_params[3], mfcc_params[4], mfcc_params[5], mfcc_params[6])
model_file_path = './model10.tflite' # KWS tflite model path
interpreter = tf.lite.Interpreter(model_path=model_file_path) # Initialize tflite interpreter
interpreter.allocate_tensors()
input_details = interpreter.get_input_details() # Get input details from tflite model
output_details = interpreter.get_output_details() # Get output details from tflite model
labels = ['down', 'up'] # Keywords labels

parser = argparse.ArgumentParser()
parser.add_argument("-ho", "--host", default = None, type=str, help="Redis host")
parser.add_argument("-po", "--port", default = None, type=int, help="Redis port")
parser.add_argument("-us", "--user", default = None, type=str , help="Redis username")
parser.add_argument("-pw", "--password", default = None, type=str , help="Redis password")
args = parser.parse_args()


# ------------------------------------------ Functions ---------------------------------------------

def callback(indata, frames, callback_time, status):
    global silence
    global oldT
    global data_collection_state
    
    # If there was no change of state or more than 2 seconds passed from the previous change of state, check if there is silence, else do nothing
    if oldT is None or time() - oldT >= 5: # oldT is None until the first change of state happens
        # Audio preprocessing (casting, downsampling, conversion to tensor, squeezing, normalization)
        audio = indata.astype(np.float32)
        audio = signal.resample_poly(audio, up=1, down=downsampling_factor)
        audio = tf.convert_to_tensor(audio)
        audio = tf.squeeze(audio)
        audio = normalization_processor.normalize_audio(audio)
        # Check if the processed audio signal is silent
        silence = vad_processor.is_silence(audio) 
        if not silence: # Perform keyword spotting if there is no silence
            audio_features = mfcc_processor.get_mfccs(audio) # Compute MFCCs
            audio_features = tf.expand_dims(audio_features, 0) # Match audio features and model input shape
            audio_features = tf.expand_dims(audio_features, -1)
            interpreter.set_tensor(input_details[0]['index'], audio_features) # Set value of input tensor
            interpreter.invoke() # Performs inference (KWS)
            probabilities = interpreter.get_tensor(output_details[0]['index']) # Return the probabilities of down and up
            print(f'Probabilities (down/up): {probabilities[0]}')
            top_1 = np.argmax(probabilities[0]) # return the index of the higher probability
            top_1_prob = probabilities[0,top_1] # return the probability of the top 1 prediction
            print(f'The word {labels[top_1]} has been said with probability {top_1_prob}')
            if top_1_prob <=0.99:
                pass
            elif probabilities[0,1] > 0.99: # if the probability of up is higher that 99%, enable data collection
                data_collection_state = True
                oldT = time()
                print(f'Data collection: {data_collection_state}') 
            elif probabilities[0,0] > 0.99: # if the probability of down is higher that 99%, disable data collection
                data_collection_state = False
                oldT = time()
                print(f'Data collection: {data_collection_state}')


# ------------------------------------------ Main ---------------------------------------------

# Establish a connection to the database and check if the connection works
redis_client = redis.Redis(host = args.host, 
                           port = args.port, 
                           username = args.user, 
                           password = args.password) 

is_connected = redis_client.ping()
print('REDIS CONNECTION:', is_connected)

# Create new time series for temperature and humidity, if they don't exist
try:
    redis_client.ts.create(str(mac_address)+':temperature')
except:
    pass
try:
    redis_client.ts.create(str(mac_address)+':humidity')
except:
    pass


# Starts audio recording
with sd.InputStream(device = 1, channels = 1, dtype = bit_depth, samplerate = samplerate, blocksize = length_in_secs*samplerate, callback = callback):
    print('AUDIO RECORDING STARTED')
    # Store timestamp when there is no silence
    while True:
        # If data collection is enabled and 2 seconds have passed from the previous data collection, collect new data
        if data_collection_state and (timestamp is None or (time() - timestamp >= 2)):
            timestamp = int(time())
            formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f') # Convert the timestamp to human-readable time
            try:
                # Get temperature and humidity from the sensor, store them in the database and print them
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                redis_client.ts().add(str(mac_address)+':temperature', timestamp, temperature)
                redis_client.ts().add(str(mac_address)+':humidity', timestamp, humidity)
                print(f'{formatted_time} - {mac_address}:temperature = {temperature}')
                print(f'{formatted_time} - {mac_address}:humidity = {humidity}')
            except:
                # If the connection fails, print an error message and try to restart the connection
                # This is done because the connection is generally unrealiable
                print('Sensor failure')
                dht_device.exit()
                dht_device = adafruit_dht.DHT11(D4)