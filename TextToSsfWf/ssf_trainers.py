import os
import re
import sys
import tensorflow as tf
import csv
from ssf_dataset import download_dataset_text_to_ssf_0384, download_dataset_text_to_ssf_0768, download_dataset_text_to_ssf_label, download_dataset_text_to_json_ast, download_dataset_text_to_json_code, setup_tokenizer_text_to_ssf_0384, setup_tokenizer_text_to_ssf_0768, setup_tokenizer_text_to_ssf_label, setup_tokenizer_text_to_json_ast, setup_tokenizer_text_to_json_code
import ssf_trainer
from ssf_transformerconfigs import TransformerConfig, OptimizerType, LearningRateType
from ssf_translator import Translator 
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import logging


### Create a logger
print('Initializing logger')
logger = logging.getLogger("trainer_logger")
logger.setLevel(logging.INFO)  # Set the logging level
# Create a formatter for log messages
log_format = logging.Formatter('%(message)s')
# Create a file handler (writes logs to a file)
file_handler = logging.FileHandler("pretrained/trainer.log")
file_handler.setFormatter(log_format)
# Add both handlers to the logger
logger.addHandler(file_handler)
#########


def print_system_info():
    # Print versions
    print("Python Version:", sys.version)
    print("TensorFlow Version:", tf.__version__)
    print("Built with CUDA:", tf.test.is_built_with_cuda())
    print("Built with GPU support:", tf.test.is_built_with_gpu_support())

    # GPU details
    gpus = tf.config.list_physical_devices('GPU')
    print("Num GPUs Available:", len(gpus))
    for idx, gpu in enumerate(gpus):
        print(f"GPU {idx} - Name: {gpu.name}, Type: {gpu.device_type}")

MAX_INFERENCE_TOKENS = 128
EARLY_STOP_PATIENCE = 8
MAX_EPOCHS = 30
MAX_TRIALS = 1
TRIAL_INDEX = 0
START_INDEX = 0
TEST_BLEU_INDEX = 0
TEST_BLEU_COUNT = 5000

D_MODEL = 128
DFF = 512
HEADS = 4
DROP_OUT_RATE = 0.1
ENCODERS = 4
DECODERS = 4

def export_training_history_to_csv(history_dict, csv_file_name):
    """
    Export all epoch values from history dict to CSV.
    """
    losses = history_dict['loss']
    accs = history_dict['masked_accuracy']
    val_losses = history_dict['val_loss']
    val_accs = history_dict['val_masked_accuracy']

    # Header row
    rows = [['epoch', 'loss', 'masked_accuracy', 'val_loss', 'val_masked_accuracy']]

    # Data rows per epoch
    for i in range(len(losses)):
        row = [
            i + 1,
            round(losses[i], 6),
            round(accs[i], 6),
            round(val_losses[i], 6),
            round(val_accs[i], 6)
        ]
        rows.append(row)

    if os.path.exists(csv_file_name):
        rows = rows[1:]
    
    to_csv(rows, csv_file_name)

def to_csv(data_list, output_file):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Create the file if it doesn't exist and append if it does
    with open(output_file, 'a', encoding='utf8', newline='') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
        for item in data_list:
            wr.writerow(item)

def get_prompts(inputFile, fromIndex, count):
    with open(inputFile, 'r', encoding='utf8') as f:
        text = f.read()

    sourceList = text.splitlines()

    toIndex = fromIndex + count
    if (toIndex >= len(sourceList)):
        toIndex = len(sourceList) - 1

    slicesList = sourceList[fromIndex:toIndex]

    return slicesList

def translate(translator, prompt, max_tokens = 128):
    translated_text, translated_tokens, attention_weights = translator(tf.constant(prompt), max_tokens)
    text_output = translated_text.numpy().decode("utf-8")
    return text_output, translated_text

def split_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)     # Collapse multiple spaces
    text = text.strip()

    # Lowercase everything
    return text.lower()


def calculate_bleu_score(transformer, tokenizers, checkpoint_path, csv_log_file_name, index, configType, 
                         source_file, target_file,
                         start_index=0, count=1000):

    if (os.path.isfile(csv_log_file_name) == False):
        log_row = ['Index', 'Config Type', 'Trials', 'BLEU Score', 'Exact Match']
        to_csv([log_row], csv_log_file_name)

    inputs = get_prompts(source_file, start_index, count)
    outputs = get_prompts(target_file, start_index, count)
    print(checkpoint_path)
    transformer.load_weights(checkpoint_path).expect_partial()

    translator = Translator(tokenizers, transformer)

    sum2 = float(0)
    exact_match = 0
    for i in range(0, len(inputs), 1):
        
        prompt = inputs[i]

        text2, token2 = translate(translator, prompt, MAX_INFERENCE_TOKENS)

        line_logs = []

        target = clean_text(outputs[i])
        result = clean_text(text2)

        reference = [ split_text(target) ]
        candidate2 = split_text(result)

        bleu_score2 = sentence_bleu(reference, candidate2, smoothing_function=SmoothingFunction().method1)
        #bleu_score2 = sentence_bleu(reference, candidate2)

        is_exact_match = False
        if (int(bleu_score2) >= int(1) or target == result): # type: ignore
            is_exact_match = True
            exact_match = exact_match + 1

        sum2 = sum2 + bleu_score2 # type: ignore

        log_row = [index, configType, i, bleu_score2, is_exact_match]

        to_csv([log_row], csv_log_file_name)

        line_logs.append(f'Type   : {configType}')
        line_logs.append(f'Index  : {str(i+1)}')
        line_logs.append(f'Input  : {prompt}')
        line_logs.append(f'Output : {candidate2}')
        line_logs.append(f'Target : {reference[0]}')
        line_logs.append(f'BLEU   : {bleu_score2}')
        line_logs.append(f'Exact  : {is_exact_match}')
        line_logs.append('\n')

        line_log = "\n".join(line_logs)
        logger.info(line_log)

    avg2 = float(sum2) / float(len(inputs))

    logger.info(f'Sum: {str(sum2)}')
    logger.info(f'Avg: {str(avg2)}')
    logger.info(f'Exact Match: {str(exact_match)}')

    return sum2, avg2, exact_match


def run_training_test(configs, folder_name, csv_file_name, csv_log_file_name, csv_training_history_file_name, max_trials, max_epochs, early_stop_patience, 
                      bleu_source_file, bleu_target_file,
                      start_trial_index = 0, test_bleu_index = TEST_BLEU_INDEX, test_bleu_count = TEST_BLEU_COUNT):
    
    print('Running Training Test With Number of Configs = ', len(configs))
    print('CSV File Name: ', csv_file_name)
    print('CSV Log File Name: ', csv_log_file_name)

    os.makedirs(folder_name, exist_ok=True)

    if (os.path.isfile(csv_file_name) == False):
        row = ['Index', 'Config Type', 'Training Loss', 'Training Masked Accuracy', 'Validation Loss', 'Validation Masked Accuracy', 'Completed Epochs', 'SUM BLEU', 'AVG BLEU', 'Exact Match']
        to_csv([row], csv_file_name)

    for i in range(start_trial_index, max_trials, 1):
        
        print('Index: ', i)

        for j in range(0, len(configs), 1):

            config = configs[j]

            print('Transformer Config: ', config.name)

            config_name = config.name + '_' + str(i)
            checkpoint_path = folder_name + '/' + config.name + '/' + config_name + '/'

            custom_trainer = ssf_trainer.CustomTrainer(get_tokenizers=config.get_tokenizers, get_dataset=config.get_dataset)

            transformer, tokenizers, history = custom_trainer.run_transformer(
                encoder_layers=config.encoder_layers,
                decoder_layers=config.decoder_layers,
                d_model=config.d_model,
                dff=config.dff,
                num_heads=config.num_heads,
                dropout_rate=config.dropout_rate,
                optimizer=config.optimizer,
                loss_function=config.loss_function,
                checkpoint_path=checkpoint_path,
                epoch=max_epochs,
                early_stopping_patience=early_stop_patience,
                activation_type=config.activation_type
            )

            # Access the metrics
            last_index = len(history.history['loss']) - 1 # type: ignore
            loss_values = history.history['loss'][last_index]  # type: ignore # Training loss for each epoch
            masked_accuracy_values = history.history['masked_accuracy'][last_index]  # type: ignore # Training accuracy for each epoch
            val_loss_values = history.history['val_loss'][last_index]  # type: ignore # Validation loss for each epoch
            val_masked_accuracy_values = history.history['val_masked_accuracy'][last_index]  # type: ignore # Validation accuracy for each epoch
            completed_epochs = len(history.history['loss']) # type: ignore

            # Print or analyze the results
            print("Training Loss:", loss_values)
            print("Training Masked Accuracy:", masked_accuracy_values)
            print("Validation Loss:", val_loss_values)
            print("Validation Masked Accuracy:", val_masked_accuracy_values)
            print("Number of completed epochs:", completed_epochs)

            logger.info(history.history) # type: ignore

            export_training_history_to_csv(history.history, csv_training_history_file_name) # type: ignore

            inference_transformer = custom_trainer.create_inference_transformer(
                encoder_layers=config.encoder_layers,
                decoder_layers=config.decoder_layers,
                d_model=config.d_model,
                dff=config.dff,
                num_heads=config.num_heads,
                dropout_rate=config.dropout_rate,
                optimizer=config.optimizer,
                loss_function=config.loss_function,
                checkpoint_path=checkpoint_path,
                activation_type=config.activation_type
            )
            sum_bleu, avg_bleu, exact_match = calculate_bleu_score(inference_transformer, tokenizers, checkpoint_path, csv_log_file_name, i, config.name, 
                                                      bleu_source_file, bleu_target_file,
                                                      test_bleu_index, test_bleu_count)

            row = [ i, config.name, loss_values, masked_accuracy_values, val_loss_values, val_masked_accuracy_values, completed_epochs, sum_bleu, avg_bleu, exact_match ]
            
            logger.info(row)

            to_csv([row], csv_file_name)


        print('Training Finished on ', str(len(configs)), ' Transformer Configs, Training Summary Saved on ', csv_file_name)


def run_once(config, formation_name, bleu_source_file, bleu_target_file,
             max_trials = MAX_TRIALS, max_epochs = MAX_EPOCHS, early_stops_patience = EARLY_STOP_PATIENCE, 
             start_index = START_INDEX, test_bleu_index = TEST_BLEU_INDEX, test_bleu_count = TEST_BLEU_COUNT):

    print('Preparing Transformer Test Training ', formation_name)
    folder_name = 'pretrained'
    csv_file_name = folder_name + '/' + formation_name + '/training_summary.csv'
    csv_log_file_name = folder_name + '/' + formation_name + '/training_logs_' + formation_name + '.csv'
    csv_training_history_file_name = folder_name + '/' + formation_name + '/training_history.csv'
    configs = []

    configs.append(config)

    run_training_test(configs, folder_name, csv_file_name, csv_log_file_name, csv_training_history_file_name, max_trials, max_epochs, early_stops_patience, 
                      bleu_source_file, bleu_target_file,
                      start_index, test_bleu_index, test_bleu_count)
    print('Finished Transformer Test Training ', formation_name)


def run_test(config, folder_name, bleu_source_file, bleu_target_file, test_bleu_index = TEST_BLEU_INDEX, test_bleu_count = TEST_BLEU_COUNT, model_index = 0):
    
    print('Transformer Config: ', config.name)

    csv_log_file_name = folder_name + '/training_logs.csv'

    config_name = config.name + '_' + str(model_index)
    checkpoint_path = folder_name + '/' + config_name + '/'

    print(checkpoint_path)

    custom_trainer = ssf_trainer.CustomTrainer(get_tokenizers=config.get_tokenizers, get_dataset=config.get_dataset)
    inference_transformer = custom_trainer.create_inference_transformer(
        encoder_layers=config.encoder_layers,
        decoder_layers=config.decoder_layers,
        d_model=config.d_model,
        dff=config.dff,
        num_heads=config.num_heads,
        dropout_rate=config.dropout_rate,
        optimizer=config.optimizer,
        loss_function=config.loss_function,
        checkpoint_path=checkpoint_path,
        activation_type=config.activation_type
    )

    tokenizers = config.get_tokenizers()
    sum_bleu, avg_bleu, exact_match = calculate_bleu_score(inference_transformer, tokenizers, checkpoint_path, csv_log_file_name, 0, config.name, 
                                                bleu_source_file, bleu_target_file,
                                                test_bleu_index, test_bleu_count)


def transformer_config_text_to_ssf_0384_Standard():
    config = TransformerConfig(
        get_tokenizers=setup_tokenizer_text_to_ssf_0384,
        get_dataset=download_dataset_text_to_ssf_0384,
        name='text_to_ssf_0384_Standard',
        encoder_layers=ENCODERS,
        decoder_layers=DECODERS,
        d_model=D_MODEL,
        dff=DFF,
        num_heads=HEADS,
        dropout_rate=DROP_OUT_RATE,
        optimizerType=OptimizerType.Adam,
        learningRateType=LearningRateType.Standard,
        activation_type='relu'
    )
    return config

def transformer_config_text_to_json_code_Standard():
    config = TransformerConfig(
        get_tokenizers=setup_tokenizer_text_to_json_code,
        get_dataset=download_dataset_text_to_json_code,
        name='text_to_json_code_Standard',
        encoder_layers=ENCODERS,
        decoder_layers=DECODERS,
        d_model=D_MODEL,
        dff=DFF,
        num_heads=HEADS,
        dropout_rate=DROP_OUT_RATE,
        optimizerType=OptimizerType.Adam,
        learningRateType=LearningRateType.Standard,
        activation_type='relu'
    )
    return config

def transformer_config_text_to_json_ast_Standard():
    config = TransformerConfig(
        get_tokenizers=setup_tokenizer_text_to_json_ast,
        get_dataset=download_dataset_text_to_json_ast,
        name='text_to_json_ast_Standard',
        encoder_layers=ENCODERS,
        decoder_layers=DECODERS,
        d_model=D_MODEL,
        dff=DFF,
        num_heads=HEADS,
        dropout_rate=DROP_OUT_RATE,
        optimizerType=OptimizerType.Adam,
        learningRateType=LearningRateType.Standard,
        activation_type='relu'
    )
    return config

def transformer_config_text_to_ssf_0768_Standard():
    config = TransformerConfig(
        get_tokenizers=setup_tokenizer_text_to_ssf_0768,
        get_dataset=download_dataset_text_to_ssf_0768,
        name='text_to_ssf_0768_Standard',
        encoder_layers=ENCODERS,
        decoder_layers=DECODERS,
        d_model=D_MODEL,
        dff=DFF,
        num_heads=HEADS,
        dropout_rate=DROP_OUT_RATE,
        optimizerType=OptimizerType.Adam,
        learningRateType=LearningRateType.Standard,
        activation_type='relu'
    )
    return config

def transformer_config_text_to_ssf_label_Standard():
    config = TransformerConfig(
        get_tokenizers=setup_tokenizer_text_to_ssf_label,
        get_dataset=download_dataset_text_to_ssf_label,
        name='text_to_ssf_label_Standard',
        encoder_layers=ENCODERS,
        decoder_layers=DECODERS,
        d_model=D_MODEL,
        dff=DFF,
        num_heads=HEADS,
        dropout_rate=DROP_OUT_RATE,
        optimizerType=OptimizerType.Adam,
        learningRateType=LearningRateType.Standard,
        activation_type='relu'
    )
    return config


if __name__ == '__main__':

    print_system_info()


    bleu_source_file = 'dataset/ssf_0384/tx_ssf_0384_0005k.txt'
    bleu_target_file = 'dataset/ssf_0384/wf_ssf_0384_0005k.txt'
    config = transformer_config_text_to_ssf_0384_Standard()
    run_once(config, 'text_to_ssf_0384_Standard', bleu_source_file, bleu_target_file, MAX_TRIALS, MAX_EPOCHS, EARLY_STOP_PATIENCE, TRIAL_INDEX, TEST_BLEU_INDEX, TEST_BLEU_COUNT)
    # run_test(config, 'text_to_ssf_0384_Standard', bleu_source_file, bleu_target_file, TEST_BLEU_INDEX, TEST_BLEU_COUNT, 0)


    bleu_source_file = 'dataset/json_code/tx_json_code_0005k.txt'
    bleu_target_file = 'dataset/json_code/wf_json_code_0005k.txt'
    config = transformer_config_text_to_json_code_Standard()
    run_once(config, 'text_to_json_code_Standard', bleu_source_file, bleu_target_file, MAX_TRIALS, MAX_EPOCHS, EARLY_STOP_PATIENCE, TRIAL_INDEX, TEST_BLEU_INDEX, TEST_BLEU_COUNT)
    # run_test(config, 'pretrained/text_to_json_code_Standard', bleu_source_file, bleu_target_file, TEST_BLEU_INDEX, TEST_BLEU_COUNT, 0)


    bleu_source_file = 'dataset/json_ast/tx_json_ast_0005k.txt'
    bleu_target_file = 'dataset/json_ast/wf_json_ast_0005k.txt'
    config = transformer_config_text_to_json_ast_Standard()
    run_once(config, 'text_to_json_ast_Standard', bleu_source_file, bleu_target_file, MAX_TRIALS, MAX_EPOCHS, EARLY_STOP_PATIENCE, TRIAL_INDEX, TEST_BLEU_INDEX, TEST_BLEU_COUNT)
    # run_test(config, 'text_to_json_ast_Standard', bleu_source_file, bleu_target_file, TEST_BLEU_INDEX, TEST_BLEU_COUNT, 0)


    bleu_source_file = 'dataset/ssf_0768/tx_ssf_0768_0005k.txt'
    bleu_target_file = 'dataset/ssf_0768/wf_ssf_0768_0005k.txt'
    config = transformer_config_text_to_ssf_0768_Standard()
    run_once(config, 'text_to_ssf_0768_Standard', bleu_source_file, bleu_target_file, MAX_TRIALS, MAX_EPOCHS, EARLY_STOP_PATIENCE, TRIAL_INDEX, TEST_BLEU_INDEX, TEST_BLEU_COUNT)
    # run_test(config, 'text_to_ssf_0384_Standard', bleu_source_file, bleu_target_file, TEST_BLEU_INDEX, TEST_BLEU_COUNT, 0)


    bleu_source_file = 'dataset/ssf_label/tx_ssf_label_0005k.txt'
    bleu_target_file = 'dataset/ssf_label/wf_ssf_label_0005k.txt'
    config = transformer_config_text_to_ssf_label_Standard()
    run_once(config, 'text_to_ssf_label_Standard', bleu_source_file, bleu_target_file, MAX_TRIALS, MAX_EPOCHS, EARLY_STOP_PATIENCE, TRIAL_INDEX, TEST_BLEU_INDEX, TEST_BLEU_COUNT)
    # run_test(config, 'text_to_ssf_label_Standard', bleu_source_file, bleu_target_file, TEST_BLEU_INDEX, TEST_BLEU_COUNT, 0)

