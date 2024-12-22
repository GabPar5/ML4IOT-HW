import tensorflow as tf
from reader import AudioReader
from preprocessing import Padding, Normalization
from preprocessing import MelSpectrogram, MFCC


def predict(audio):
    preprocess_audio, model = preprocessing(audio)
    predictions = model.predict(preprocess_audio)
    probabilities = tf.nn.softmax(predictions)
    return probabilities

def preprocessing(audio):
    audio_reader = AudioReader(tf.int16)
    padding = Padding(PREPROCESSING_ARGS['sampling_rate'])
    normalization = Normalization(tf.int16)
    # preprocessing audio
    PREPROCESSING_ARGS = {
        'sampling_rate': 16000,
        'frame_length_in_s': 0.016,
        'frame_step_in_s': 0.016,
        'num_mel_bins': 30,
        'lower_frequency': 20,
        'upper_frequency': 6000,
        'num_coefficients': 30
    }

    TRAINING_ARGS = {
        'batch_size': 20,
        'learning_rate': 1.e-2,
        'end_learning_rate': 1.e-4,
        'epochs': 20,
        'width_multiplier': [0.25, 0.5, 0.75], # structured pruning
    }

    LABELS = ['down', 'up']

    if PREPROCESSING_ARGS['num_coefficients'] == 0:
        PREPROCESSING_ARGS.pop('num_coefficients')
        feature_processor = MelSpectrogram(**PREPROCESSING_ARGS)
        feature_processor_fn = feature_processor.get_mel_spec
        feature_processor_fn_lab = feature_processor.get_mel_spec_and_label
    else:
        feature_processor = MFCC(**PREPROCESSING_ARGS)
        feature_processor_fn = feature_processor.get_mfccs
        feature_processor_fn_lab = feature_processor.get_mfccs_and_label

    def prepare_for_training(feature, label):
        feature = tf.expand_dims(feature, -1)
        label_id = tf.argmax(label == LABELS)
        return feature, label_id
    audio = (audio
            .map(audio_reader.get_audio_and_label)
            .map(padding.pad)
            .map(normalization.normalize)
            .map(feature_processor_fn_lab)
            .map(prepare_for_training)
            .batch(TRAINING_ARGS['batch_size']))
    
    #define the model
    wm = TRAINING_ARGS['width_multiplier']

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=audio.shape[1:]),
        tf.keras.layers.Conv2D(filters=int(128*wm[1]), kernel_size=[3, 3], strides=[2, 2], use_bias=False, padding='valid'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.DepthwiseConv2D(kernel_size=[3, 3], strides=[1, 1], use_bias=False, padding='same'),
        tf.keras.layers.Conv2D(filters=int(128*wm[1]), kernel_size=[1, 1], strides=[1, 1], use_bias=False),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.DepthwiseConv2D(kernel_size=[5, 5], strides=[1, 1], use_bias=False, padding='same'),
        tf.keras.layers.Conv2D(filters=int(128*wm[1]), kernel_size=[1, 1], strides=[1, 1], use_bias=False),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(units=len(LABELS)),
        tf.keras.layers.Softmax()
    ]) # originally 128 filters and 3 conv2d layers
    return audio, model
