import tensorflow as tf
import tensorflow_io as tfio


class AudioReader():
    def __init__(self, bit_depth):
        self.bit_depth = bit_depth

    def get_audio(self, filename):
        audio_io_tensor = tfio.audio.AudioIOTensor(filename, self.bit_depth) 
        audio_tensor = audio_io_tensor.to_tensor()

        return audio_tensor

    def get_label(self, filename):
        path_parts = tf.strings.split(filename, '/')
        path_end = path_parts[-1]
        file_parts = tf.strings.split(path_end, '_')
        label = file_parts[0]
        
        return label

    def get_audio_and_label(self, filename):
        audio = self.get_audio(filename)
        label = self.get_label(filename)

        return audio, label