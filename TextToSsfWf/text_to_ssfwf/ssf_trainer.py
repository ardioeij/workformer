import logging
import os
import time

import numpy as np
import matplotlib.pyplot as plt

import tensorflow_datasets as tfds
import tensorflow as tf

from ssf_transformer import Transformer


MAX_TOKENS = 64
BUFFER_SIZE = 64
BATCH_SIZE = 64


class CustomTrainer():
    def __init__(self, get_tokenizers, get_dataset):
        self.tokenizers = get_tokenizers()
        self.dataset = get_dataset()
   
    def masked_accuracy(self, label, pred):
        pred = tf.argmax(pred, axis=2)
        label = tf.cast(label, pred.dtype)
        match = label == pred

        mask = label != 0

        match = match & mask

        match = tf.cast(match, dtype=tf.float32)
        mask = tf.cast(mask, dtype=tf.float32)
        return tf.reduce_sum(match)/tf.reduce_sum(mask)

    def prepare_batch(self, src, trg):
        src = self.tokenizers.source.tokenize(src)      # Output is ragged.
        src = src[:, :MAX_TOKENS]    # Trim to MAX_TOKENS.
        src = src.to_tensor()  # Convert to 0-padded dense Tensor

        trg = self.tokenizers.target.tokenize(trg)
        trg = trg[:, :(MAX_TOKENS + 1)]
        trg_inputs = trg[:, :-1].to_tensor()  # Drop the [END] tokens
        trg_labels = trg[:, 1:].to_tensor()   # Drop the [START] tokens

        return (src, trg_inputs), trg_labels

    def make_batches(self, ds):
        return (
            ds
            .shuffle(BUFFER_SIZE)
            .batch(BATCH_SIZE)
            .map(self.prepare_batch, tf.data.AUTOTUNE)
            .prefetch(buffer_size=tf.data.AUTOTUNE))

    def run_transformer(self, encoder_layers, decoder_layers, d_model, dff, num_heads, dropout_rate, optimizer, loss_function, 
                        checkpoint_path, 
                        epoch=25, 
                        early_stopping_patience=5,
                        activation_type='relu'):

        train_examples, val_examples = self.dataset

        train_batches = self.make_batches(train_examples)
        val_batches = self.make_batches(val_examples)

        transformer = Transformer(
            encoder_layers=encoder_layers,
            decoder_layers=decoder_layers,
            d_model=d_model,
            num_heads=num_heads,
            dff=dff,
            input_vocab_size=self.tokenizers.source.get_vocab_size().numpy(),
            target_vocab_size=self.tokenizers.target.get_vocab_size().numpy(),
            dropout_rate=dropout_rate,
            activation_type = activation_type
        )

        transformer.compile(
            loss=loss_function,
            optimizer=optimizer,
            metrics=[self.masked_accuracy])

        print(checkpoint_path)
        if os.path.isdir(checkpoint_path):
            print('Loading checkpoint')
            transformer.load_weights(checkpoint_path)
        else:
            print('Creating new model')

        cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
        save_weights_only=True,
        save_best_only=True,
        verbose=1)

        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',  # Track validation loss
            patience=early_stopping_patience,          # Stop after n epochs with no improvement
            restore_best_weights=True  # Restore model weights from the epoch with the best validation loss
        )

        history = transformer.fit(train_batches,
                        epochs=epoch,
                        validation_data=val_batches,
                        shuffle=True,
                        callbacks=[cp_callback, early_stopping])

        return transformer, self.tokenizers, history

    def create_inference_transformer(self, encoder_layers, decoder_layers, d_model, dff, num_heads, dropout_rate, optimizer, loss_function, 
                                    checkpoint_path, activation_type = 'relu'):

        transformer = Transformer(
            encoder_layers=encoder_layers,
            decoder_layers=decoder_layers,
            d_model=d_model,
            num_heads=num_heads,
            dff=dff,
            input_vocab_size=self.tokenizers.source.get_vocab_size().numpy(),
            target_vocab_size=self.tokenizers.target.get_vocab_size().numpy(),
            dropout_rate=dropout_rate,
            activation_type = activation_type
            )
        
        transformer.compile(
            loss=loss_function,
            optimizer=optimizer,
            metrics=[self.masked_accuracy])

        if os.path.isdir(checkpoint_path):
            print('Loading checkpoint ', checkpoint_path)
            transformer.load_weights(checkpoint_path).expect_partial() # type: ignore
        else:
            print('Creating new model')

        return transformer



if __name__ == '__main__':

    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

