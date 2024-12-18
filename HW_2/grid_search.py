
import tensorflow as tf
import numpy as np
import os
import zipfile
from glob import glob
from reader import AudioReader
from preprocessing import Padding, Normalization
from preprocessing import MelSpectrogram, MFCC
from tensorboard.plugins.hparams import api as hp

os.environ["TF_GPU_ALLOCATOR"] = "cuda_malloc_async"
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"

SCRIPT_DIR = os.path.abspath('')


from sklearn.model_selection import ParameterGrid 

# Build an hyperparameters grid
frame_lengths = [0.016, 0.032] 
param_grid = {
'frame_lengths': frame_lengths,
'num_mel_bins':[30, 40],
'lower_frequency':[20, 40, 60],
'upper_frequency': [2000, 4000, 6000],
'num_coefficients': [0,30,40]
}

grid = ParameterGrid(param_grid)

for params in grid:

    frame_lengths = params['frame_lengths']
    frame_step = [1* frame_lengths]+ [0.75*frame_lengths]+ [0.5*frame_lengths]+ [0.25*frame_lengths]

    for frame_step in frame_step:

        PREPROCESSING_ARGS = {
            'sampling_rate': 16000,
            'frame_length_in_s': frame_lengths,
            'frame_step_in_s': frame_step,
            'num_mel_bins': params['num_mel_bins'],
            'lower_frequency': params['lower_frequency'],
            'upper_frequency': params['upper_frequency'],
            'num_coefficients': params['num_coefficients']
        }

        print(PREPROCESSING_ARGS)

        TRAINING_ARGS = {
            'batch_size': 20,
            'learning_rate': 1.e-2,
            'end_learning_rate': 1.e-5,
            'epochs': 20,
            'width_multiplier': [0.25, 0.5, 0.75], # structured pruning
        }

        LABELS = ['down', 'up']

        train_ds = tf.data.Dataset.list_files([os.path.join(SCRIPT_DIR, 'msc-train/down*'), os.path.join(SCRIPT_DIR, 'msc-train/up*')])
        val_ds = tf.data.Dataset.list_files([os.path.join(SCRIPT_DIR, 'msc-val/down*'), os.path.join(SCRIPT_DIR, 'msc-val/up*')])
        test_ds = tf.data.Dataset.list_files([os.path.join(SCRIPT_DIR, 'msc-test/down*'), os.path.join(SCRIPT_DIR, 'msc-test/up*')])

        linear_decay = tf.keras.optimizers.schedules.PolynomialDecay(
            initial_learning_rate=TRAINING_ARGS['learning_rate'],
            end_learning_rate=TRAINING_ARGS['end_learning_rate'],
            decay_steps=int(tf.data.experimental.cardinality(train_ds)/TRAINING_ARGS['batch_size']) * TRAINING_ARGS['epochs'],
            power = 1.0
        )

        exponential_decay = tf.keras.optimizers.schedules.ExponentialDecay(
            initial_learning_rate=TRAINING_ARGS['learning_rate'],
            decay_steps=int(tf.data.experimental.cardinality(train_ds)/TRAINING_ARGS['batch_size']),
            decay_rate = (TRAINING_ARGS['end_learning_rate'] / TRAINING_ARGS['learning_rate'])**(1/30),
            staircase = True
        )
        lr_scheduler = tf.keras.callbacks.LearningRateScheduler(linear_decay)


        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=8,
            verbose=1,
            mode='min'
        )

        audio_reader = AudioReader(tf.int16)
        padding = Padding(PREPROCESSING_ARGS['sampling_rate'])
        normalization = Normalization(tf.int16)

        if PREPROCESSING_ARGS['num_coefficients'] == 0:
            PREPROCESSING_ARGS.pop('num_coefficients')
            feature_processor = MelSpectrogram(**PREPROCESSING_ARGS)
            feature_processor_fn = feature_processor.get_mel_spec
            feature_processor_fn_lab = feature_processor.get_mel_spec_and_label
        else:
            feature_processor = MFCC(**PREPROCESSING_ARGS)
            feature_processor_fn = feature_processor.get_mfccs
            feature_processor_fn_lab = feature_processor.get_mfccs_and_label

        LABELS = ['down', 'up']

        def prepare_for_training(feature, label):
            feature = tf.expand_dims(feature, -1)
            label_id = tf.argmax(label == LABELS)

            return feature, label_id

        train_ds = (train_ds
                    .map(audio_reader.get_audio_and_label)
                    .map(padding.pad)
                    .map(normalization.normalize)
                    .map(feature_processor_fn_lab)
                    .map(prepare_for_training)
                    .batch(TRAINING_ARGS['batch_size'])
                    .cache())
        val_ds = (val_ds
                    .map(audio_reader.get_audio_and_label)
                    .map(padding.pad)
                    .map(normalization.normalize)
                    .map(feature_processor_fn_lab)
                    .map(prepare_for_training)
                    .batch(TRAINING_ARGS['batch_size']))
        test_ds = (test_ds
                    .map(audio_reader.get_audio_and_label)
                    .map(padding.pad)
                    .map(normalization.normalize)
                    .map(feature_processor_fn_lab)
                    .map(prepare_for_training)
                    .batch(TRAINING_ARGS['batch_size']))

        for example_batch, example_labels in train_ds.take(1):
            print('Batch Taken')


        wm = TRAINING_ARGS['width_multiplier']

        model_1 = tf.keras.Sequential([
            tf.keras.layers.Input(shape=example_batch.shape[1:]),
            tf.keras.layers.Conv2D(filters=128, kernel_size=[3, 3], strides=[2, 2], use_bias=False, padding='valid'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.ReLU(),
            tf.keras.layers.Conv2D(filters=128, kernel_size=[3, 3], strides=[1, 1], use_bias=False, padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.ReLU(),
            tf.keras.layers.Conv2D(filters=128, kernel_size=[3, 3], strides=[1, 1], use_bias=False, padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.ReLU(),
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(units=len(LABELS)),
            tf.keras.layers.Softmax()
        ]) 


        loss = tf.losses.SparseCategoricalCrossentropy(from_logits=False)
        optimizer = tf.optimizers.Adam(learning_rate=linear_decay)
        metrics = [tf.metrics.SparseCategoricalAccuracy()]
        model_1.compile(loss=loss, optimizer=optimizer, metrics=metrics)

        history = model_1.fit(
            train_ds, 
            epochs=TRAINING_ARGS['epochs'], 
            validation_data=val_ds, 
            callbacks=[lr_scheduler, early_stopping]
        )


        training_loss = history.history['loss'][-1]
        training_accuracy = history.history['sparse_categorical_accuracy'][-1]
        val_loss = history.history['val_loss'][-1]
        val_accuracy = history.history['val_sparse_categorical_accuracy'][-1]

        test_loss, test_accuracy = model_1.evaluate(test_ds)

        print(f'Training Loss: {training_loss:.4f}')
        print(f'Training Accuracy: {training_accuracy*100.:.2f}%')
        print()
        print(f'Validation Loss: {val_loss:.4f}')
        print(f'Validation Accuracy: {val_accuracy*100.:.2f}%')
        print()
        print(f'Test Loss: {test_loss:.4f}')
        print(f'Test Accuracy: {test_accuracy*100.:.2f}%')


        import os
        from time import time

        timestamp = int(time())

        saved_model_dir = f'./saved_models/{timestamp}'
        if not os.path.exists(saved_model_dir):
            os.makedirs(saved_model_dir)
        model_1.save(saved_model_dir)

        import pandas as pd

        output_dict = {
            'timestamp': timestamp,
            **PREPROCESSING_ARGS,
            **TRAINING_ARGS,
            'test_accuracy': test_accuracy
        }

        df = pd.DataFrame([output_dict])

        output_path='./mel_spectrogram_results.csv'
        df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)


        converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
        tflite_model = converter.convert()

        tflite_model_dir = './tflite_models'
        # create the path if it doesn't exist
        if not os.path.exists(tflite_model_dir):
            os.makedirs(tflite_model_dir)

        # name the model
        tflite_model_name = os.path.join(tflite_model_dir, f'{timestamp}.tflite')
        tflite_model_name

        # write the model
        with open(tflite_model_name, 'wb') as fp:
            fp.write(tflite_model)


        MODEL_FILE_PATH = tflite_model_name

        # Measure model size
        model_size = os.path.getsize(MODEL_FILE_PATH)

        if MODEL_FILE_PATH.endswith('.zip'):
            with zipfile.ZipFile(MODEL_FILE_PATH, 'r') as fp:
                fp.extractall('/tmp/')
                model_filename = fp.namelist()[0]
                MODEL_FILE_PATH = '/tmp/' + model_filename

        interpreter = tf.lite.Interpreter(model_path=MODEL_FILE_PATH)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()


        SCRIPT_DIR = os.path.abspath('')

        filenames = glob(os.path.join(SCRIPT_DIR, 'msc-test/down*')) + glob(os.path.join(SCRIPT_DIR, 'msc-test/up*'))

        accuracy = 0.0

        for filename in filenames:
            audio, true_label = audio_reader.get_audio_and_label(filename)   
            true_label = true_label.numpy().decode()
            
            audio = padding.pad_audio(audio)
            audio = normalization.normalize_audio(audio)
            features = feature_processor_fn(audio)
            features = tf.expand_dims(features, 0)
            features = tf.expand_dims(features, -1)

            interpreter.set_tensor(input_details[0]['index'], features)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])

            top_index = np.argmax(output[0])
            predicted_label = LABELS[top_index]

            accuracy += true_label == predicted_label

        accuracy /= len(filenames)

        if accuracy > 0.994:
            with open('best_models.txt', 'a') as fil:
                fil.write(f"Params: {PREPROCESSING_ARGS}\n")
                fil.write(f"Model: {tflite_model_name}\n")
                fil.write(f"Accuracy: {100 * accuracy:.3f}%\n")
                fil.write(f"Model size: {model_size / 2 ** 10:.1f}KB\n\n")

        del model_1



