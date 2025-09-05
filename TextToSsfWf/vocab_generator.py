import re
from tensorflow_text.tools.wordpiece_vocab import bert_vocab_from_dataset as bert_vocab
import tensorflow as tf
import pathlib

ENGLISH_SHORT_WORDS = {
    "i", "a", "am", "an", "as", "at", "be", "by", "do", "go", "he", "if",
    "in", "is", "it", "me", "my", "no", "of", "on", "or", "so", "to", "up",
    "us", "we",
    "[PAD]",
    "[UNK]",
    "[START]",
    "[END]",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "{",
    "}",
    "[",
    "]",
    "(",
    ")",
    ".",
    ",",
    ":",
    ";",
    "+",
    "-",
    "*",
    "/",
    "%",
    "&",
    "|",
    "^",
    "!",
    "~",
    "_",
    "#",
    "$",
    "@",
    "&&",
    "||",
    "??",
    "=>",
    "=",
    "==",
    "!=",
    "<",
    ">",
    "<=",
    ">=",
    "<<",
    ">>",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "&=",
    "|=",
    "^=",
    "<<=",
    ">>=",
    "++",
    "--",
    "?",
    "::",
    "\"",
    "'",
}

def is_useful_token(token):
    # Always keep special essential tokens
    if token in ['[PAD]', '[START]', '[END]', '[UNK]']:
        return True

    # Exclude unwanted special tokens
    if token in ['[CLS]', '[SEP]', '[MASK]']:
        return False

    if re.fullmatch(r"\[unused\d+\]", token):
        return False

    # Exclude if only punctuation or symbols
    if re.fullmatch(r"[^\w\d]+", token):
        return False

    # Exclude any token with non-printable ASCII chars
    if any(ord(ch) < 0x20 or ord(ch) > 0x7E for ch in token):
        return False

    # Exclude numeric tokens with >2 digits
    if token.isdigit() and len(token) > 1 and token not in list("0123456789"):
        return False

    # Exclude subword numeric tokens like ##456
    if token.startswith("##") and token[2:].isdigit() and len(token[2:]) > 1:
        return False

    # Exclude short subword tokens like ##
    if token.startswith("##") and len(token) <= 2:
        return False

    # Keep single alphabetic characters like "a", "Z"
    if len(token) == 1 and token.isalpha():
        return True

    # If token has length 2, keep only if it's an English word
    if len(token) == 2 and token.lower() not in ENGLISH_SHORT_WORDS:
        return False

    return True

def clean_vocab(input_file, output_file, top_k=16384):

    with open(input_file, "r", encoding="utf-8") as f:
        all_tokens = [line.strip() for line in f if line.strip()]

    # Filter out useless tokens
    filtered_tokens = list(filter(is_useful_token, all_tokens))
    # Limit to top_k tokens
    limited_vocab = filtered_tokens[:top_k]

    # Write reduced vocab to file
    with open(output_file, "w", encoding="utf-8") as f:
        for token in limited_vocab:
            f.write(token + "\n")

    print(f"Saved {len(limited_vocab)} filtered tokens to {output_file}")

def clean_text(lower_case=False):
    def _clean(line):
        """Remove non-UTF-8, Chinese characters, emojis, and Unicode symbols. Keep ASCII and code symbols."""
        line = tf.strings.regex_replace(line, r'[^\x00-\x7F]', '')  # remove non-ASCII

        # Keep only allowed characters (common English/code symbols)
        allowed = r'a-zA-Z0-9\s\.,!?;:\'"()\[\]{}<>@#$%^&*+=/_\-\\|'
        line = tf.strings.regex_replace(line, fr'[^{allowed}]', '')

        # Optional lower case
        if lower_case:
            line = tf.strings.lower(line)

        return tf.strings.strip(line)
    return _clean

def split_camel_case(text):
    """
    Splits CamelCase/PascalCase words into separate words.
    Example: 'ANewMessage' -> 'a new message'
    """
    # Insert space before any uppercase letter that follows a lowercase or another uppercase letter (not first)
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
    text = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', text)
    return text.lower()

def build_vocab(input_files, output_file, vocab_size, lower_case=False):
    print('Building vocab from:', input_files)

    def clean_and_split(line):
        cleaned = clean_text(lower_case=False)(line).numpy().decode('utf-8') # type: ignore
        return split_camel_case(cleaned)

    # Load, clean, and split datasets
    def clean_lines(file_path):
        dataset = tf.data.TextLineDataset(file_path)
        return dataset.map(lambda x: tf.py_function(func=clean_and_split, inp=[x], Tout=tf.string))

    datasets = [clean_lines(file) for file in input_files]
    combined_dataset = datasets[0]
    for ds in datasets[1:]:
        combined_dataset = combined_dataset.concatenate(ds)

    combined_dataset = combined_dataset.batch(1024)

    reserved_tokens = ["[PAD]", "[UNK]", "[START]", "[END]"]

    print('Generating BERT vocab...')
    vocab = bert_vocab.bert_vocab_from_dataset(
        dataset=combined_dataset,
        vocab_size=vocab_size,
        reserved_tokens=reserved_tokens,
    )

    pathlib.Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(vocab))

    print(f'Vocabulary saved to: {output_file}')


def remove_token_with_length_greater_then(input_file, output_file, max_length, max_index, max_tokens):
    with open(input_file, "r", encoding="utf-8") as f:
        all_tokens = [line.strip() for line in f if line.strip()]
    
    removes_count = 0
    tokens = []
    for i in range(0, len(all_tokens), 1):
        tkn = all_tokens[i]
        
        if (len(all_tokens) - removes_count <= max_tokens):
            tokens.append(tkn)
        else:
            if (len(tkn) >= max_length and i < max_index):
                removes_count = removes_count + 1
                continue
            else:
                tokens.append(tkn)
        
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))


if __name__ == '__main__':
    print()


    build_vocab(['dataset/trimmed_small_descriptions_corrected.txt'], 
                 'dataset/vocab_text_raw.txt', 18000, False
                 )
    clean_vocab('dataset/vocab/vocab_text_raw.txt', 'dataset/vocab_text_clean.txt', 18000)
    remove_token_with_length_greater_then('dataset/vocab_text_clean.txt', 'dataset/vocab/vocab_text.txt', 12, 12000, 16384)


    build_vocab(['dataset/trimmed_small_workflows_code_clean.txt'], 
                 'dataset/vocab_json_code_raw.txt', 16384, True
                 )
    clean_vocab('dataset/vocab/vocab_json_code.txt', 'dataset/vocab/vocab_json_code2.txt', 16384)


    build_vocab(['dataset/trimmed_small_workflows_ast.ndjson'], 
                 'dataset/vocab_ast_json_raw.txt', 16384, True
                 )
    clean_vocab('dataset/vocab_json_ast_raw.txt', 'dataset/vocab/vocab_ast_json.txt', 16384)


    build_vocab(['dataset/trimmed_small_workflows_label.txt'], 
                 'dataset/vocab_ssf_label_raw.txt', 17000, False
                 )
    clean_vocab('dataset/vocab_ssf_label_raw.txt', 'dataset/vocab/vocab_ssf_label_raw.txt', 17000)

