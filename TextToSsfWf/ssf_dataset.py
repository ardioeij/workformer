import pathlib
import re
import tensorflow_datasets as tfds
import tensorflow as tf
import tensorflow_text as text


def load_data(source_path, target_path):
    with open(source_path, 'r', encoding='utf-8') as f:
        source_sentences = f.readlines()
    with open(target_path, 'r', encoding='utf-8') as f:
        target_sentences = f.readlines()
    return source_sentences, target_sentences


class TextToSsf0384Dataset(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for TextToSsf0384 dataset."""

    VERSION = tfds.core.Version('0.0.0')

    def _info(self):

        self.train_source_file = 'dataset/ssf_0384/tx_ssf_0384_0100k.txt'
        self.train_target_file = 'dataset/ssf_0384/wf_ssf_0384_0100k.txt'

        self.validation_source_file = 'dataset/ssf_0384/tx_ssf_0384_0010k.txt'
        self.validation_target_file = 'dataset/ssf_0384/wf_ssf_0384_0010k.txt'

        return tfds.core.DatasetInfo(
            builder=self,
            description=("TextToSsf0384 Dataset"),
            features=tfds.features.FeaturesDict({
                'source': tfds.features.Text(),
                'target': tfds.features.Text(),
            }),
            supervised_keys=('source', 'target'),
            homepage='https://dataset-homepage/',
            citation=r"""@article{my-citation}""",
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # You can do custom logic here to split the data
        return [
            tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN, # type: ignore
                gen_kwargs={
                    'source_file': self.train_source_file,
                    'target_file': self.train_target_file,
                },
            ),
            tfds.core.SplitGenerator(
                name=tfds.Split.VALIDATION, # type: ignore
                gen_kwargs={
                    'source_file': self.validation_source_file,
                    'target_file': self.validation_target_file,
                },
            ),
        ]

    def _generate_examples(self, source_file, target_file):
        """Yields examples."""
        sf, tsf = load_data(source_file, target_file)
        #with tf.io.gfile.GFile(source_file) as sf, tf.io.gfile.GFile(target_file) as tsf:
        for idx, (src_line, tgt_line) in enumerate(zip(sf, tsf)):
            yield idx, {
                'source': src_line,
                'target': tgt_line,
            }


class TextToJsonCodeDataset(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for TextToJsonCode dataset."""

    VERSION = tfds.core.Version('0.0.0')

    def _info(self):

        self.train_source_file = 'dataset/json_code/tx_json_code_0100k.txt'
        self.train_target_file = 'dataset/json_code/wf_json_code_0100k.txt'

        self.validation_source_file = 'dataset/json_code/tx_json_code_0010k.txt'
        self.validation_target_file = 'dataset/json_code/wf_json_code_0010k.txt'

        return tfds.core.DatasetInfo(
            builder=self,
            description=("TextToJsonCode Dataset"),
            features=tfds.features.FeaturesDict({
                'source': tfds.features.Text(),
                'target': tfds.features.Text(),
            }),
            supervised_keys=('source', 'target'),
            homepage='https://dataset-homepage/',
            citation=r"""@article{my-citation}""",
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # You can do custom logic here to split the data
        return [
            tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN, # type: ignore
                gen_kwargs={
                    'source_file': self.train_source_file,
                    'target_file': self.train_target_file,
                },
            ),
            tfds.core.SplitGenerator(
                name=tfds.Split.VALIDATION, # type: ignore
                gen_kwargs={
                    'source_file': self.validation_source_file,
                    'target_file': self.validation_target_file,
                },
            ),
        ]

    def _generate_examples(self, source_file, target_file):
        """Yields examples."""
        #print(source_file)
        #print(target_file)
        sf, tsf = load_data(source_file, target_file)
        #with tf.io.gfile.GFile(source_file) as sf, tf.io.gfile.GFile(target_file) as tsf:
        for idx, (src_line, tgt_line) in enumerate(zip(sf, tsf)):
            yield idx, {
                'source': src_line,
                'target': tgt_line,
            }


class TextToJsonAstDataset(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for TextToJsonAst dataset."""

    VERSION = tfds.core.Version('0.0.0')

    def _info(self):

        self.train_source_file = 'dataset/json_ast/tx_json_ast_0100k.txt'
        self.train_target_file = 'dataset/json_ast/wf_json_ast_0100k.txt'

        self.validation_source_file = 'dataset/json_ast/tx_json_ast_0010k.txt'
        self.validation_target_file = 'dataset/json_ast/wf_json_ast_0010k.txt'

        return tfds.core.DatasetInfo(
            builder=self,
            description=("TextToJsonAst Dataset"),
            features=tfds.features.FeaturesDict({
                'source': tfds.features.Text(),
                'target': tfds.features.Text(),
            }),
            supervised_keys=('source', 'target'),
            homepage='https://dataset-homepage/',
            citation=r"""@article{my-citation}""",
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # You can do custom logic here to split the data
        return [
            tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN, # type: ignore
                gen_kwargs={
                    'source_file': self.train_source_file,
                    'target_file': self.train_target_file,
                },
            ),
            tfds.core.SplitGenerator(
                name=tfds.Split.VALIDATION, # type: ignore
                gen_kwargs={
                    'source_file': self.validation_source_file,
                    'target_file': self.validation_target_file,
                },
            ),
        ]

    def _generate_examples(self, source_file, target_file):
        """Yields examples."""
        #print(source_file)
        #print(target_file)
        sf, tsf = load_data(source_file, target_file)
        #with tf.io.gfile.GFile(source_file) as sf, tf.io.gfile.GFile(target_file) as tsf:
        for idx, (src_line, tgt_line) in enumerate(zip(sf, tsf)):
            yield idx, {
                'source': src_line,
                'target': tgt_line,
            }


class TextToSsf0768Dataset(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for TextToSsf0768 dataset."""

    VERSION = tfds.core.Version('0.0.0')

    def _info(self):

        self.train_source_file = 'dataset/ssf_0768/tx_ssf_0768_0100k.txt'
        self.train_target_file = 'dataset/ssf_0768/wf_ssf_0768_0100k.txt'

        self.validation_source_file = 'dataset/ssf_0768/tx_ssf_0768_0010k.txt'
        self.validation_target_file = 'dataset/ssf_0768/wf_ssf_0768_0010k.txt'

        return tfds.core.DatasetInfo(
            builder=self,
            description=("TextToSsf0768 Dataset"),
            features=tfds.features.FeaturesDict({
                'source': tfds.features.Text(),
                'target': tfds.features.Text(),
            }),
            supervised_keys=('source', 'target'),
            homepage='https://dataset-homepage/',
            citation=r"""@article{my-citation}""",
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # You can do custom logic here to split the data
        return [
            tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN, # type: ignore
                gen_kwargs={
                    'source_file': self.train_source_file,
                    'target_file': self.train_target_file,
                },
            ),
            tfds.core.SplitGenerator(
                name=tfds.Split.VALIDATION, # type: ignore
                gen_kwargs={
                    'source_file': self.validation_source_file,
                    'target_file': self.validation_target_file,
                },
            ),
        ]

    def _generate_examples(self, source_file, target_file):
        """Yields examples."""
        sf, tsf = load_data(source_file, target_file)
        #with tf.io.gfile.GFile(source_file) as sf, tf.io.gfile.GFile(target_file) as tsf:
        for idx, (src_line, tgt_line) in enumerate(zip(sf, tsf)):
            yield idx, {
                'source': src_line,
                'target': tgt_line,
            }


class TextToSsfLabelDataset(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for TextToSsfLabel dataset."""

    VERSION = tfds.core.Version('0.0.0')

    def _info(self):

        self.train_source_file = 'dataset/ssf_label/tx_ssf_label_0100k.txt'
        self.train_target_file = 'dataset/ssf_label/wf_ssf_label_0100k.txt'

        self.validation_source_file = 'dataset/ssf_label/tx_ssf_label_0010k.txt'
        self.validation_target_file = 'dataset/ssf_label/wf_ssf_label_0010k.txt'

        return tfds.core.DatasetInfo(
            builder=self,
            description=("TextToSsfLabel Dataset"),
            features=tfds.features.FeaturesDict({
                'source': tfds.features.Text(),
                'target': tfds.features.Text(),
            }),
            supervised_keys=('source', 'target'),
            homepage='https://dataset-homepage/',
            citation=r"""@article{my-citation}""",
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # You can do custom logic here to split the data
        return [
            tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN, # type: ignore
                gen_kwargs={
                    'source_file': self.train_source_file,
                    'target_file': self.train_target_file,
                },
            ),
            tfds.core.SplitGenerator(
                name=tfds.Split.VALIDATION, # type: ignore
                gen_kwargs={
                    'source_file': self.validation_source_file,
                    'target_file': self.validation_target_file,
                },
            ),
        ]

    def _generate_examples(self, source_file, target_file):
        """Yields examples."""
        sf, tsf = load_data(source_file, target_file)
        #with tf.io.gfile.GFile(source_file) as sf, tf.io.gfile.GFile(target_file) as tsf:
        for idx, (src_line, tgt_line) in enumerate(zip(sf, tsf)):
            yield idx, {
                'source': src_line,
                'target': tgt_line,
            }


class TokenizerContainer:
    def __init__(self, tokenizer_source, tokenizer_target):
        self.source = tokenizer_source
        self.target = tokenizer_target


reserved_tokens=["[PAD]", "[UNK]", "[START]", "[END]"]

START = tf.cast(tf.argmax(tf.constant(reserved_tokens) == "[START]"), tf.int32)
END = tf.cast(tf.argmax(tf.constant(reserved_tokens) == "[END]"), tf.int32)

def add_start_end(ragged):
    count = ragged.bounding_shape()[0]
    starts = tf.fill([count, 1], START)
    ends = tf.fill([count, 1], END)
    ragged = tf.cast(ragged, tf.int32)  # Ensure consistency
    return tf.concat([starts, ragged, ends], axis=1)

def cleanup_text(reserved_tokens, token_txt):
  # Drop the reserved tokens, except for "[UNK]".
  bad_tokens = [re.escape(tok) for tok in reserved_tokens if tok != "[UNK]"]
  bad_token_re = "|".join(bad_tokens)

  bad_cells = tf.strings.regex_full_match(token_txt, bad_token_re)
  result = tf.ragged.boolean_mask(token_txt, ~bad_cells)

  # Join them into strings.
  result = tf.strings.reduce_join(result, separator=' ', axis=-1)

  return result


class TextTokenizer(tf.Module):
  
  def __init__(self, reserved_tokens, vocab_path):
    self.tokenizer = text.BertTokenizer(vocab_path, lower_case=True, token_out_type=tf.int32, preserve_unused_token=True)
    self._reserved_tokens = reserved_tokens
    self._vocab_path = tf.saved_model.Asset(vocab_path)

    vocab = pathlib.Path(vocab_path).read_text(encoding='utf-8').splitlines()
    self.vocab = tf.Variable(vocab)

    self.tokenize.get_concrete_function(
        tf.TensorSpec(shape=[None], dtype=tf.string)) # type: ignore

    self.detokenize.get_concrete_function(
        tf.TensorSpec(shape=[None, None], dtype=tf.int32)) # type: ignore

    self.detokenize.get_concrete_function(
          tf.RaggedTensorSpec(shape=[None, None], dtype=tf.int32)) # type: ignore

    self.lookup.get_concrete_function(
        tf.TensorSpec(shape=[None, None], dtype=tf.int32)) # type: ignore

    self.lookup.get_concrete_function(
          tf.RaggedTensorSpec(shape=[None, None], dtype=tf.int32)) # type: ignore

    # These `get_*` methods take no arguments
    self.get_vocab_size.get_concrete_function()
    self.get_vocab_path.get_concrete_function()
    self.get_reserved_tokens.get_concrete_function()

  @tf.function
  def tokenize(self, strings):
    enc = self.tokenizer.tokenize(strings)
    enc = enc.merge_dims(-2,-1)
    enc = add_start_end(enc)
    return enc

  @tf.function
  def detokenize(self, tokenized):
    words = self.tokenizer.detokenize(tokenized)
    return cleanup_text(self._reserved_tokens, words)

  @tf.function
  def lookup(self, token_ids):
    return tf.gather(self.vocab, token_ids)

  @tf.function
  def get_vocab_size(self):
    return tf.shape(self.vocab)[0]

  @tf.function
  def get_vocab_path(self):
    return self._vocab_path

  @tf.function
  def get_reserved_tokens(self):
    return tf.constant(self._reserved_tokens)


def download_dataset_text_to_ssf_0384():
    ds, ds_info = tfds.load('text_to_ssf0384_dataset', with_info=True, as_supervised=True) # type: ignore
    train_examples, val_examples = ds[tfds.Split.TRAIN], ds[tfds.Split.VALIDATION] # type: ignore
    return train_examples, val_examples

def download_dataset_text_to_json_code():
    ds, ds_info = tfds.load('text_to_json_code_dataset', with_info=True, as_supervised=True) # type: ignore
    train_examples, val_examples = ds[tfds.Split.TRAIN], ds[tfds.Split.VALIDATION] # type: ignore
    return train_examples, val_examples

def download_dataset_text_to_json_ast():
    ds, ds_info = tfds.load('text_to_json_ast_dataset', with_info=True, as_supervised=True) # type: ignore
    train_examples, val_examples = ds[tfds.Split.TRAIN], ds[tfds.Split.VALIDATION] # type: ignore
    return train_examples, val_examples

def download_dataset_text_to_ssf_0768():
    ds, ds_info = tfds.load('text_to_ssf0768_dataset', with_info=True, as_supervised=True) # type: ignore
    train_examples, val_examples = ds[tfds.Split.TRAIN], ds[tfds.Split.VALIDATION] # type: ignore
    return train_examples, val_examples

def download_dataset_text_to_ssf_label():
    ds, ds_info = tfds.load('text_to_ssf_label_dataset', with_info=True, as_supervised=True) # type: ignore
    train_examples, val_examples = ds[tfds.Split.TRAIN], ds[tfds.Split.VALIDATION] # type: ignore
    return train_examples, val_examples


def setup_tokenizer_text_to_ssf_0384():
    tokenizers=TokenizerContainer(TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_text.txt'), TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_ssf_0384.txt'))
    return tokenizers

def setup_tokenizer_text_to_json_code():
    tokenizers=TokenizerContainer(TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_text.txt'), TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_json_code.txt'))
    return tokenizers

def setup_tokenizer_text_to_json_ast():
    tokenizers=TokenizerContainer(TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_text.txt'), TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_json_ast.txt'))
    return tokenizers

def setup_tokenizer_text_to_ssf_label():
    tokenizers=TokenizerContainer(TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_text.txt'), TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_ssf_label.txt'))
    return tokenizers

def setup_tokenizer_text_to_ssf_0768():
    tokenizers=TokenizerContainer(TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_text.txt'), TextTokenizer(reserved_tokens, 'dataset/vocab/vocab_ssf_0768.txt'))
    return tokenizers


if __name__ == '__main__':
   
   print()


   download_dataset_text_to_ssf_0384()

   download_dataset_text_to_json_code()
   
   download_dataset_text_to_json_ast()

   download_dataset_text_to_ssf_0768()

   download_dataset_text_to_ssf_label()


   tokenizer = setup_tokenizer_text_to_ssf_0384()
   print(tokenizer)

   tokenizer = setup_tokenizer_text_to_json_code()
   print(tokenizer)

   tokenizer = setup_tokenizer_text_to_json_ast()
   print(tokenizer)

   tokenizer = setup_tokenizer_text_to_ssf_0768()
   print(tokenizer)

   tokenizer = setup_tokenizer_text_to_ssf_label()
   print(tokenizer)
