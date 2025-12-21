import matplotlib.pyplot as plt
import tensorflow as tf


class Translator(tf.Module):
  def __init__(self, tokenizers, transformer):
    self.tokenizers = tokenizers
    self.transformer = transformer

  def __call__(self, sentence, max_length):
    # The input sentence is Portuguese, hence adding the `[START]` and `[END]` tokens.
    assert isinstance(sentence, tf.Tensor)
    if len(sentence.shape) == 0:
        sentence = sentence[tf.newaxis] # type: ignore

    sentence = self.tokenizers.source.tokenize(sentence).to_tensor()

    encoder_input = sentence

    # As the output language is English, initialize the output with the
    # English `[START]` token.
    start_end = self.tokenizers.target.tokenize([''])[0]
    start = start_end[0][tf.newaxis]
    end = start_end[1][tf.newaxis]

    # `tf.TensorArray` is required here (instead of a Python list), so that the
    # dynamic-loop can be traced by `tf.function`.
    output_array = tf.TensorArray(dtype=tf.int32, size=0, dynamic_size=True)
    output_array = output_array.write(0, start)

    for i in tf.range(max_length):
        output = tf.transpose(output_array.stack())
        predictions = self.transformer([encoder_input, output], training=False)

        # Select the last token from the `seq_len` dimension.
        predictions2 = predictions[:, -1:, :]  # Shape `(batch_size, 1, vocab_size)`.

        predicted_id = tf.cast(tf.argmax(predictions2, axis=-1), tf.int32)

        # Concatenate the `predicted_id` to the output which is given to the
        # decoder as its input.
        output_array = output_array.write(i+1, predicted_id[0]) # type: ignore

        if predicted_id == end:
            break

    output = tf.transpose(output_array.stack())
    # The output shape is `(1, tokens)`.
    text = self.tokenizers.target.detokenize(output)[0]  # Shape: `()`.

    tokens = self.tokenizers.target.lookup(output)[0]

    # `tf.function` prevents us from using the attention_weights that were
    # calculated on the last iteration of the loop.
    # So, recalculate them outside the loop.
    self.transformer([encoder_input, output[:,:-1]], training=False)
    attention_weights = self.transformer.decoder.last_attn_scores

    return text, tokens, attention_weights


def print_translation(sentence, tokens):
  print(f'{"Input:":15s}: {sentence}')
  print(f'{"Prediction":15s}: {tokens.numpy().decode("utf-8")}')

def translate(translator, prompt, training=False):
    translated_text, translated_tokens, attention_weights = translator(tf.constant(prompt), training=training)
    text_output = translated_text.numpy().decode("utf-8")
    return text_output, translated_text


if __name__ == '__main__':

    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    
