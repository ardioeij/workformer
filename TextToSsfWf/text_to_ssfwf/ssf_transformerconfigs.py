# Standard
# AdamW, LayerwiseLearningRateDecay, Enhanced-SoftMax
# Decoder-Double-Self-Attention, Standard
# Decoder-Double-Self-Attention, AdamW, LayerwiseLearningRateDecay, Enhanced-SoftMax

# config, trials, value_loss, value_masked, BLEU_score

from enum import Enum, IntEnum

import numpy as np
import tensorflow as tf


class StandardLearningRateSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
  def __init__(self, d_model, warmup_steps=4000):
    super().__init__()

    self.d_model = d_model
    self.d_model = tf.cast(self.d_model, tf.float32)
    self.warmup_steps = warmup_steps

  def __call__(self, step):
    step = tf.cast(step, dtype=tf.float32)
    arg1 = tf.math.rsqrt(step)
    arg2 = step * (self.warmup_steps ** -1.5)
    return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)

class LayerwiseLearningRateDecay(tf.keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self, base_lr, decay_factor, num_layers):
        super(LayerwiseLearningRateDecay, self).__init__()
        self.base_lr = base_lr
        self.decay_factor = decay_factor
        self.num_layers = num_layers

    def __call__(self, step):
        ## Ensure num_layers // 5 is at least 1 and cast to int
        
        num_decay_steps = tf.maximum(self.num_layers // 4, 1)  # Decay over fewer layers

        # Cast step to int before performing division
        step = tf.cast(step, tf.int32)

        # Calculate the layer index and ensure it's an int type
        layer_index = tf.minimum(step // num_decay_steps, self.num_layers - 1) # type: ignore
        #layer_index = 1

        # Calculate the decayed learning rate and cast layer_index to float for power operation
        decayed_lr = self.base_lr * (self.decay_factor ** tf.cast(layer_index, tf.float32))

        # Clip the learning rate to prevent NaNs
        clipped_lr = tf.clip_by_value(decayed_lr, 1e-7, 1.0)

        return clipped_lr


class AdamW(tf.keras.optimizers.Adam):
    def __init__(self, learning_rate=0.001, weight_decay=1e-5, **kwargs):
        super().__init__(learning_rate=learning_rate, **kwargs)
        self.weight_decay = weight_decay

    def _decay_weights_op(self, var):
        if self.weight_decay > 0 and self._use_weight_decay(var):
            return var.assign_sub(self.weight_decay * var, read_value=False)
        return tf.no_op()

    def _use_weight_decay(self, var):
        return 'bias' not in var.name.lower() and 'bn' not in var.name.lower()

    def apply_gradients(self, grads_and_vars, name=None, **kwargs):
        grads_and_vars = list(grads_and_vars)
        # Apply weight decay before gradients
        for grad, var in grads_and_vars:
            self._decay_weights_op(var)
        return super().apply_gradients(grads_and_vars, name=name, **kwargs)


def masked_loss(label, pred):
  mask = label != 0
  loss_object = tf.keras.losses.SparseCategoricalCrossentropy(
    from_logits=True, reduction='none')
  loss = loss_object(label, pred)

  mask = tf.cast(mask, dtype=loss.dtype)
  loss *= mask

  loss = tf.reduce_sum(loss)/tf.reduce_sum(mask)
  return loss
  

class LearningRateType(Enum):
    Standard = 1  # Base learning rate without decay
    LayerwiseLearningRateDecay = 2  # Layer-wise learning rate decay

class OptimizerType(Enum):
    Adam = 1  # AdamW optimizer
    AdamW = 2  # Standard Adam optimizer


class TransformerConfig():
    def __init__(self, name: str, 
                 get_tokenizers,
                 get_dataset,
                 encoder_layers = 4, decoder_layers = 4, d_model = 128, dff = 512, num_heads = 8, dropout_rate = 0.1,
                 optimizerType = OptimizerType.Adam, learningRateType = LearningRateType.Standard, 
                 activation_type = 'relu',
                 ):
        self.encoder_layers = encoder_layers
        self.decoder_layers = decoder_layers
        self.d_model = d_model
        self.dff = dff
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate
        self.optimizerType = optimizerType
        self.learningRateType = learningRateType
        self.name = name
        self.learning_rate = self.init_learning_type(learningRateType, d_model, (decoder_layers + encoder_layers))
        self.optimizer = self.init_optimizer(optimizerType, self.learning_rate)
        self.loss_function = self.init_loss_function()
        self.activation_type = activation_type
        self.get_tokenizers = get_tokenizers
        self.get_dataset = get_dataset

    def init_learning_type(self, learningType: LearningRateType, d_model: int = 128, num_layers: int = 4, base_lr = 5e-4, decay_factor = 0.9, warmup = 1000):
        print('Learning Type ', learningType)
        if (learningType == LearningRateType.Standard):
            learningRate = StandardLearningRateSchedule(d_model)
        elif (learningType == LearningRateType.LayerwiseLearningRateDecay):
            learningRate = LayerwiseLearningRateDecay(base_lr, decay_factor, num_layers)
        return learningRate

    def init_optimizer(self, optimizerType: OptimizerType, learning_rate: tf.keras.optimizers.schedules.LearningRateSchedule,
                       beta_1=0.9, beta_2 = 0.98, weight_decay = 0.01, epsilon = 1e-9):
        print('Optimizer ', optimizerType)
        if (optimizerType == OptimizerType.Adam):
            optimizer = tf.keras.optimizers.Adam(learning_rate, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon) # type: ignore
        elif (optimizerType == OptimizerType.AdamW):
            optimizer = AdamW(learning_rate=learning_rate, weight_decay=weight_decay, beta_1=beta_1, beta_2=beta_2, epsilon=epsilon) # type: ignore
        return optimizer

    def init_loss_function(self):
        loss_function = masked_loss
        return loss_function
