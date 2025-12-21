from datetime import datetime
import json
import logging
import os
import re
import sys

from ssf_parser_cluster_to_json import reverse_ssf_to_json, check_and_fix_brackets
from ssf_parser_label_to_json import reverse_ssf_label_to_json


def progress(index, count):
    sys.stdout.write('\r')
    sys.stdout.write(str(index) + ' / ' + str(count) + ' ')
    sys.stdout.flush()  

def init_logger(log_filename, log_dir='logs'):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)    

    output_file = os.path.join(log_dir, f"{log_filename}_{datetime.now().strftime('%Y%m%d_%H%M')}.log")
    ### Create a logger
    logger = logging.getLogger("trainer_logger")
    logger.setLevel(logging.INFO)  # Set the logging level
    # Create a formatter for log messages
    log_format = logging.Formatter('%(message)s')
    # Create a file handler (writes logs to a file)
    file_handler = logging.FileHandler(output_file)
    file_handler.setFormatter(log_format)
    # Add both handlers to the logger
    logger.addHandler(file_handler)
    #########
    return logger
    
def read_lines(input_file):
    with open(input_file, 'r', encoding='utf8') as f:
        inputText = f.read()
        sourceList = inputText.splitlines()
    return sourceList


def count_json_seq_nodes(json_obj):
    """Recursively counts all nodes under the 'Seq' section of the JSON object."""
    def recurse(seq_list):
        count = 0
        for item in seq_list:
            count += 1
            if isinstance(item, dict) and 'Seq' in item:
                count += recurse(item['Seq'])
        return count

    return recurse(json_obj.get('Seq', []))

def count_ssf_cluster_seq_nodes(ssf_str):

    try:
        parsed_json = reverse_ssf_to_json(ssf_str)
        [parsed_json, is_correct, info] = check_and_fix_brackets(parsed_json, True)
        json_output = json.loads(parsed_json)
        #json_output = json.dumps(parsed_json)
        #print(parsed_json)
    except ValueError as e:
        print(parsed_json)
        return 0

    count = count_json_seq_nodes(json_output)

    return count

def count_ssf_label_seq_nodes(ssf_str):

    try:
        parsed_json = reverse_ssf_label_to_json(ssf_str)
        [parsed_json, is_correct, info] = check_and_fix_brackets(parsed_json, True)
        json_output = json.loads(parsed_json)
        #json_output = json.dumps(parsed_json)
        #print(parsed_json)
    except ValueError as e:
        print(parsed_json)
        return 0

    count = count_json_seq_nodes(json_output)

    return count

def compare_node_cluster_counts(json_str, ssf_str):
    """Compare node count between JSON and SSF representations."""
    try:
        json_obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return False

    json_count = count_json_seq_nodes(json_obj)
    ssf_count = count_ssf_cluster_seq_nodes(ssf_str)

    return json_count == ssf_count, json_count, ssf_count

def compare_node_label_counts(json_str, ssf_str):
    """Compare node count between JSON and SSF representations."""
    try:
        json_obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return False

    json_count = count_json_seq_nodes(json_obj)
    ssf_count = count_ssf_label_seq_nodes(ssf_str)

    return json_count == ssf_count, json_count, ssf_count

def compare_node_json_counts(json1_str, json2_str):
    """Compare node count between JSON and SSF representations."""
    try:
        json1_obj = json.loads(json1_str)
        json2_obj = json.loads(json2_str)
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return False

    json1_count = count_json_seq_nodes(json1_obj)
    json2_count = count_json_seq_nodes(json2_obj)

    return json1_count == json2_count, json1_count, json2_count


def test():
    jsonstr = '{"In": [], "Out": [{"Prm": "", "Type": "Object"}], "Seq": [{"Comp": "PROC0042"}]}'
    sffstr = '{ In [  ] Out [ Object ] Seq [ { PROC0042 } ] }'
    match, json_cnt, ssf_cnt = compare_node_cluster_counts(jsonstr, sffstr) # type: ignore

    print(f"JSON count = {json_cnt}, SSF count = {ssf_cnt}")


def find_original_pairs(wf_ssf_file_path, tx_ssf_file_path, master_json_file_path, master_desc_file_path, log_file_path, mode='label'):

    log = init_logger(log_file_path)

    mismatch_count = 0
    total = 0

    wf_ssf_lines = read_lines(wf_ssf_file_path)
    tx_ssf_lines = read_lines(tx_ssf_file_path)

    wf_master_json_lines = read_lines(master_json_file_path)
    tx_master_desc_lines = read_lines(master_desc_file_path)

    count = len(wf_ssf_lines)
    for x in range(0, count, 1):
        wf_ssf = wf_ssf_lines[x]
        tx_ssf = tx_ssf_lines[x]

        progress(x, count)

        total += 1
        indices = [i for i, line in enumerate(tx_master_desc_lines) if line.lower().strip() == tx_ssf.lower().strip()]

        is_match = False
        for j in indices:

            wf_json = wf_master_json_lines[j]

            if (mode == 'label'):
                match, json_cnt, ssf_cnt = compare_node_label_counts(wf_json, wf_ssf) # type: ignore
            elif (mode == 'json'):
                match, json_cnt, ssf_cnt = compare_node_json_counts(wf_json, wf_ssf) # type: ignore
            else:
                match, json_cnt, ssf_cnt = compare_node_cluster_counts(wf_json, wf_ssf) # type: ignore

            if match == False:
                continue
            else:
                is_match = True
                log.info(tx_ssf)
                log.info(wf_ssf)
                log.info(wf_json)
                log.info(f"[Match] Line {total}: JSON count = {json_cnt}, SSF count = {ssf_cnt}")
                log.info('')
                break
        
        if (is_match == False):
            log.info(tx_ssf)
            log.info(wf_ssf)
            log.info(wf_json)
            log.info(f"[Mismatch] Line {total}: JSON count = {json_cnt}, SSF count = {ssf_cnt}")            
            log.info('')
            mismatch_count += 1
            continue

    log.info("\nComparison Complete")
    log.info(f"Total Pairs Checked: {total}")
    log.info(f"Mismatches Found: {mismatch_count}")
    log.info(f"Match Rate: {(total - mismatch_count) / total * 100:.2f}%")

    print("\nComparison Complete")
    print(f"Total Pairs Checked: {total}")
    print(f"Mismatches Found: {mismatch_count}")
    print(f"Match Rate: {(total - mismatch_count) / total * 100:.2f}%")


if __name__ == '__main__':
    print()

    #test()

    master_json_file_path = 'dataset/trimmed_small_workflows_0384.ndjson'
    master_desc_file_path = 'dataset/trimmed_small_descriptions_corrected.txt'
    tx_ssf_file_path      = 'dataset/trimmed_small_descriptions_ssf_0384.txt'
    wf_ssf_file_path      = 'dataset/trimmed_small_workflows_ssf_0384.txt'
    find_original_pairs(wf_ssf_file_path, tx_ssf_file_path, master_json_file_path, master_desc_file_path, 'validations_0384', 'cluster')

    master_json_file_path = 'dataset/trimmed_small_workflows_0768.ndjson'
    master_desc_file_path = 'dataset/trimmed_small_descriptions_corrected.txt'
    tx_ssf_file_path      = 'dataset/trimmed_small_descriptions_ssf_0768.txt'
    wf_ssf_file_path      = 'dataset/trimmed_small_workflows_ssf_0768.txt'
    find_original_pairs(wf_ssf_file_path, tx_ssf_file_path, master_json_file_path, master_desc_file_path, 'validations_0768', 'cluster')

    master_json_file_path = 'dataset/trimmed_small_workflows.ndjson'
    master_desc_file_path = 'dataset/trimmed_small_descriptions_corrected.txt'
    tx_ssf_file_path      = 'dataset/trimmed_small_descriptions_code.txt'
    wf_ssf_file_path      = 'dataset/trimmed_small_workflows_code_clean.txt'
    find_original_pairs(wf_ssf_file_path, tx_ssf_file_path, master_json_file_path, master_desc_file_path, 'validations_json_code', 'json')

    master_json_file_path = 'dataset/trimmed_small_workflows.ndjson'
    master_desc_file_path = 'dataset/trimmed_small_descriptions_corrected.txt'
    tx_ssf_file_path      = 'dataset/trimmed_small_descriptions_ast.txt'
    wf_ssf_file_path      = 'dataset/trimmed_small_workflows_ast_clean.txt'
    find_original_pairs(wf_ssf_file_path, tx_ssf_file_path, master_json_file_path, master_desc_file_path, 'validations_json_ast', 'json')

    master_json_file_path = 'dataset/trimmed_small_workflows.ndjson'
    master_desc_file_path = 'dataset/trimmed_small_descriptions_corrected.txt'
    tx_ssf_file_path      = 'dataset/trimmed_small_descriptions_label.txt'
    wf_ssf_file_path      = 'dataset/trimmed_small_workflows_label.txt'
    find_original_pairs(wf_ssf_file_path, tx_ssf_file_path, master_json_file_path, master_desc_file_path, 'validations_label', 'label')

