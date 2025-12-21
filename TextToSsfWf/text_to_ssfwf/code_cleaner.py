import csv
from genericpath import isfile
import logging
from ntpath import join
from os import listdir
import random
import sys
import time

import numpy as np
import matplotlib.pyplot as plt

import tensorflow_datasets as tfds
import tensorflow as tf

import tensorflow_datasets.datasets
import tensorflow_text



def progress(current, total, desc):
    sys.stdout.write('\r')
    sys.stdout.write(str(current) + ' / ' + str(total) + ' ' + desc)
    sys.stdout.flush()  

def progress_info(desc):
    sys.stdout.write('\r')
    sys.stdout.write(desc)
    sys.stdout.flush()  


def remove_duplicates(input_file, output_file):
    """
    Remove duplicate lines from a large text file and write the unique lines to a new file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output text file where unique lines will be written.
    """
    seen = set()
    
    with open(input_file, 'r', encoding='utf8') as infile, open(output_file, 'w', encoding='utf8') as outfile:
        for line in infile:
            if line.rstrip().lstrip().strip() == '':
                continue

            # Only write the line if it hasn't been seen before
            if line not in seen:
                outfile.write(line)
                seen.add(line)  # Add the line to the set of seen lines

def merge_text_files(input_files, output_file):
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for input_file in input_files:
            with open(input_file, 'r', encoding='utf-8') as in_file:
                print(in_file)
                for line in in_file:
                    out_file.write(line)    

def to_csv(list, output_file):
    with open(output_file, 'w', encoding='utf8') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')

        for item in list:
            row = [ item[0], item[1], item[2] ]
            wr.writerow(row)


def toTextFile(lines, outputFile, mode='a'):
    outputs = ''
    for line in lines:
        outputs += line + '\n'
    with open(outputFile, mode, encoding='utf8') as f:
        f.write(outputs)


def to_batch(input_file, max_tokens, paddingChar):
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    tokens = []

    for i in range(0, len(lines), 1):
        items = lines[i].split()
        for j in range(0, len(items), 1):
            tokens.append(items[j])
    
    padding_needed = max_tokens - (len(tokens) % max_tokens) if len(tokens) % max_tokens != 0 else 0
    
    #if padding_needed > 0:
    tokens = np.pad(tokens, (0, padding_needed), 'constant', constant_values=(paddingChar,))
    tokens = tokens.reshape(-1, max_tokens)
    
    #string_rows = [''.join(map(str, row)) for row in tokens]

    return tokens


def sliding_windows(input_file, max_tokens, paddingCount, paddingChars, paddingEndChar, paddingAtIndex):
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    tokens = []

    for i in range(0, len(lines), 1):
        items = lines[i].split()
        for j in range(0, len(items), 1):
            tokens.append(items[j])

    for i in range(0, paddingCount, 1):
        n = random.randint(0, len(paddingChars) - 1) 
        tokens.insert((paddingAtIndex + i), paddingChars[n])

    padding_needed = max_tokens - (len(tokens) % max_tokens) if len(tokens) % max_tokens != 0 else 0
    
    #if padding_needed > 0:
    tokens = np.pad(tokens, (0, padding_needed), 'constant', constant_values=(paddingEndChar,))
    tokens = tokens.reshape(-1, max_tokens)
    
    #string_rows = [' '.join(map(str, row)) for row in tokens]

    return tokens


def createSlidingWindowsWfDataset(input_files, output_batch_file, output_sliding_file, max_tokens, paddingCount, paddingSlidingChars, paddingCharEnd, paddingAtIndex):

    batch_lines_tokens = []
    sliding_lines_tokens = []

    for i in range(0, len(input_files), 1):
        
        file = input_files[i]
        print(file)
        batch_tokens = to_batch(file, max_tokens, paddingCharEnd)
        batch_lines = [batch_lines_tokens.append(' '.join(token)) for token in batch_tokens]
        #print(len(batch_lines))
        
        sliding_tokens = sliding_windows(file, max_tokens, paddingCount, paddingSlidingChars, paddingCharEnd, paddingAtIndex)
        sliding_lines = [sliding_lines_tokens.append(' '.join(token)) for token in sliding_tokens]

    if (len(batch_lines_tokens) > len(sliding_lines_tokens)):
        sliding_lines_tokens.append(' '.join([paddingCharEnd for k in range(0, max_tokens, 1)]))
    
    if (len(sliding_lines_tokens) > len(batch_lines_tokens)):
        batch_lines_tokens.append(' '.join([paddingCharEnd for k in range(0, max_tokens, 1)]))

    print(len(batch_lines_tokens))
    print(len(sliding_lines_tokens))

    toTextFile(batch_lines_tokens, output_batch_file)
    toTextFile(sliding_lines_tokens, output_sliding_file)


def generateSlidingWindowsWorkflowDataset():
    input_files = [
        'data/workflows.txt',
        'data/db_workflows.txt',
    ]

    padding_chars = []
    for i in range(0, 64, 1):
        pad = '{ PROC' + str(i).zfill(3) + ' }'
        padding_chars.append(pad)

    createSlidingWindowsWfDataset(input_files, 'data/db_batch_workflows.txt', 'data/sliding_batch_workflows.txt', 64, 16, padding_chars, '[PAD]', 18)

def shift_array(arr):
    if len(arr) == 0:
        return arr
    return [arr[-1]] + arr[:-1]

def createSlidingWindowsRequirements(mypath='data/requirements/', output_file1='data/requirements01.txt', output_file2='data/requirements02.txt'):

    input_files = [mypath + f for f in listdir(mypath) if isfile(join(mypath, f))]
    merge_text_files(input_files, output_file1)

    with open(output_file1, 'r', encoding='utf-8') as f:
        text = f.read()
    
    source_lines = text.splitlines()
    np.random.shuffle(source_lines)

    toTextFile(source_lines, output_file1)

    #source_lines = shift_array(source_lines)

    #toTextFile(source_lines, output_file2)

    createSlidingWindowsWfDataset([output_file1], output_file1, output_file2, 64, 16, [' '], '[PAD]', 0)

def extractTokens(inputFile, outputFile):
    with open(inputFile, 'r', encoding='utf8') as f:
        inputText = f.read()

    outputs = ''
    sourceList = inputText.splitlines()
    for line in sourceList:
        outputs += str(line.split('~')[1]).rstrip().lstrip() + '\n'

    with open(outputFile, 'w', encoding='utf8') as f:
        f.write(outputs)

def swap_codetokenreg_to_tokencodereq(inputFile, outputFile):
    with open(inputFile, 'r', encoding='utf8') as f:
        inputText = f.read()

    outputs = ''
    sourceList = inputText.splitlines()
    for line in sourceList:
        cols = line.split('~')
        row = cols[1].rstrip().lstrip() + '~' + cols[0].rstrip().lstrip() + '~' + cols[2].rstrip().lstrip()
        outputs += row + '\n'

    with open(outputFile, 'w', encoding='utf8') as f:
        f.write(outputs)

def swap_codetoken_to_tokencode(inputFile, outputFile):
    with open(inputFile, 'r', encoding='utf8') as f:
        inputText = f.read()

    outputs = ''
    sourceList = inputText.splitlines()
    count = len(sourceList)
    print('swap_codetoken_to_tokencode() Total lines:', count)

    i=1
    for line in sourceList:
        cols = line.split('~')
        row = cols[1].rstrip().lstrip() + ' ~ ' + cols[0].rstrip().lstrip()
        outputs += row + '\n'
        progress(i, count, '')
        i = i + 1

    with open(outputFile, 'w', encoding='utf8') as f:
        f.write(outputs)
    
    print('Written:', outputFile)


def trimmed_dataset(source_input_file, target_input_file, source_output_file, target_output_file):
    source_input_lines = []
    target_input_lines = []
    
    source_output_lines = []
    target_output_lines = []

    temps=[]

    with open(source_input_file, 'r', encoding='utf-8') as src_in_file:
        source_input_text = src_in_file.read()
        source_input_lines = source_input_text.splitlines()

    with open(target_input_file, 'r', encoding='utf-8') as src_out_file:
        target_input_text = src_out_file.read()
        target_input_lines = target_input_text.splitlines()

    count = min(len(source_input_lines), len(target_input_lines))

    print('Total Lines: ', count)

    for i in range(0, count, 1):
        source = source_input_lines[i].strip()
        target = target_input_lines[i].strip()
        temp = source + '~' + target
        if (temp not in temps):
            temps.append(temp)
            source_output_lines.append(source)
            target_output_lines.append(target)
            progress(i, count, '/ ' + str(len(source_output_lines)) + ' / ' + str(len(target_output_lines)))
    
    print('toTextFile: ', source_output_file)
    toTextFile(source_output_lines, source_output_file, 'w')

    print('toTextFile: ', target_output_file)
    toTextFile(target_output_lines, target_output_file, 'w')
    

def swap_trim_codetoken_to_tokencode(inputFile, outputFile):
    with open(inputFile, 'r', encoding='utf8') as f:
        inputText = f.read()

    temps=[]

    outputs = ''
    sourceList = inputText.splitlines()
    count = len(sourceList)
    print('swap_trim_codetoken_to_tokencode() Total lines:', count)

    i=1
    for line in sourceList:
        cols = line.split('~')
        row = cols[1].rstrip().lstrip() + ' ~ ' + cols[0].rstrip().lstrip()

        if (row not in temps):
            temps.append(row)
            progress(i, count, '/ ' + str(len(temps)))
            outputs += row + '\n'
        
        i = i + 1

    with open(outputFile, 'w', encoding='utf8') as f:
        f.write(outputs)
    
    print('Written:', outputFile)


def trim_lines(inputFile, outputFile):
    with open(inputFile, 'r', encoding='utf8') as f:
        inputText = f.read()

    temps=[]

    outputs = ''
    sourceList = inputText.splitlines()
    count = len(sourceList)
    print('trim_lines() Total lines:', count)

    i=1
    for row in sourceList:
        if (row not in temps):
            temps.append(row)
            progress(i, count, '/ ' + str(len(temps)))
            outputs += row + '\n'
        
        i = i + 1

    with open(outputFile, 'w', encoding='utf8') as f:
        f.write(outputs)
    
    print('Written:', outputFile)


def read_lines(input_file):
    with open(input_file, 'r', encoding='utf8') as f:
        inputText = f.read()
        sourceList = inputText.splitlines()
    
    return sourceList

def read_csv_to_array_list(csv_file):
    """
    Reads a CSV file and returns its contents as a list of arrays (rows).

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        list: A list of arrays, where each array represents a row in the CSV.
    """
    array_list = []
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            array_list.append(row)
    return array_list


def read_included_clusters(csv_file):

    normal_dist_included_index = 7
    cluster_index = 0

    clusters=[]

    with open(csv_file, 'r', encoding='utf8') as csvfile:

        csv_reader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
        for row in csv_reader:
            
            is_included = int(row[normal_dist_included_index])
            if (is_included != 0):
                cluster = row[cluster_index]
                print(cluster)
                clusters.append(cluster)
    
    return clusters


def read_excluded_clusters(csv_file):

    normal_dist_included_index = 7
    cluster_index = 0

    clusters=[]

    with open(csv_file, 'r', encoding='utf8') as csvfile:

        csv_reader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
        for row in csv_reader:
            
            is_excluded = int(row[normal_dist_included_index])
            if (is_excluded == 0):
                cluster = row[cluster_index]
                print(cluster)
                clusters.append(cluster)
    
    return clusters


def get_cluster_patterns(must_included_tokens, csv_file):
    
    token_code_index = 0
    is_included_index = 3

    patterns = []

    with open(csv_file, 'r', encoding='utf8') as csvfile:
        i = 0
        csv_reader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
        for row in csv_reader:
            
            token_code = row[token_code_index]
            is_include = row[is_included_index]
            
            token = token_code.split('~')[0].rstrip().lstrip().strip()

            if (int(is_include) == 1):
                if (token not in patterns):
                    patterns.append(token)
                    progress(i, 0, str('Append Regular Token ' + token))
                    i = i + 1

            elif (int(is_include) == 0):
                tokens = token.split()
                if any(item in tokens for item in must_included_tokens):
                    if (token not in patterns):
                        patterns.append(token)
                        progress(i, 0, str('Append Mandatory Token ' + token))
                        i = i + 1

    return patterns


def trim_tokens_pattern(csv_file):
    
    token_code_index = 0

    patterns = []

    progress_info('Trim Tokens ...')
    with open(csv_file, 'r', encoding='utf8') as csvfile:

        csv_reader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
        for row in csv_reader:
            
            token_code = row[token_code_index]
            token = token_code.split('~')[0].rstrip().lstrip().strip()
            if (token not in patterns):
                patterns.append(token)

    return patterns

def trim_tokens_pattern_txt(txt_file):
    
    cs_ast = read_lines('data/uswf/token_vocab.txt')
    # rejected_codes = [
    #     'foreach',
    #     'while',
    #     'public',
    #     'private',
    #     'protected',
    #     'class'
    # ]

    patterns = []

    print('Trim Tokens ...')

    lines = read_lines(txt_file)
    for i in range(0, len(lines), 1):
        token_code = lines[i].split('~')
        code = token_code[1].rstrip().lstrip().strip()
        token = token_code[0].rstrip().lstrip().strip()
        
        parts = token.split()
        invalid_tokens = [item for item in parts if item not in cs_ast]
        if (len(invalid_tokens) > 0 or code == ''):
            print('contains invalid token or invalid code ', token, ' ', code)
        else:
            if (token not in patterns):
                patterns.append(token)

        #codes = code.split()
        # found = [item for item in codes if item in rejected_codes]
        # if (code == '' or len(found) > 0):
        #     print('skip rejected word', code)
        # else:
        #     parts = token.split()
        #     if len(parts) >= 1 :
        #         if (parts[0] not in cs_ast):
        #             print('invalid token ', parts[0])
        #         else:
        #             if (token not in patterns):
        #                 patterns.append(token)
            
    return patterns

def get_cluster_patterns_txt(txt_file):
    
    cs_ast = read_lines('data/uswf/token_vocab.txt')

    patterns = []

    lines = read_lines(txt_file)

    for i in range(0, len(lines), 1):
        
        token_code = lines[0]
        token = token_code.split('~')[0].rstrip().lstrip().strip()
        parts = token.split()
        if len(parts) > 1:
            if (parts[0] not in cs_ast):
                print('invalid token ', parts[0])
            else:
                if (token not in patterns):
                    patterns.append(token)
                    progress(i, 0, str('Append Regular Token ' + token))
                    i = i + 1

    return patterns


def count_token_patterns(patterns, csv_file, output_file):
    
    token_code_index = 0

    pattern_dictionary = {}

    for i in range(0, len(patterns), 1):
        pattern_dictionary[patterns[i]] = 0

    progress_info('Reading code file count_token_patterns ' + str(len(patterns)))

    with open(csv_file, 'r', encoding='utf8') as csvfile:

        csv_reader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
        for row in csv_reader:
            
            token_code = row[token_code_index]
            token = token_code.split('~')[0].rstrip().lstrip()
            if (token in patterns):
                pattern_dictionary[token] = int(pattern_dictionary[token]) + 1

    progress_info('Writing to CSV')
    with open(output_file, 'w', encoding='utf8') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')

        for i in range(0, len(patterns), 1):
            row = [ patterns[i], pattern_dictionary[patterns[i]] ]
            wr.writerow(row)
            progress(i, len(patterns), ' Writing Token Pattern')

    return patterns

def count_token_patterns_txt(patterns, txt_file, output_file, csv_output2):
    
    def myFunc(e):
        return e[2]
    
    pattern_dictionary = {}
    token_index = []

    list_token_code_index = []

    for i in range(0, len(patterns), 1):
        pattern_dictionary[patterns[i]] = 0
        token_index.append([ patterns[i], i])

    lines = read_lines(txt_file)
    count = len(lines)

    progress_info('Reading code file count_token_patterns ' + str(len(patterns)))

    for i in range(0, count, 1):
        row = lines[i].split('~')
        token = row[0].rstrip().lstrip().strip()
        code = row[1].rstrip().lstrip().strip()
        
        if (token in patterns):
            pattern_dictionary[token] = int(pattern_dictionary[token]) + 1
            item = [ token, code, list(pattern_dictionary.keys()).index(token) ]
            list_token_code_index.append(item)

    progress_info('Writing to CSV 1')
    with open(output_file, 'w', encoding='utf8') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')

        for i in range(0, len(patterns), 1):
            row = [ patterns[i], pattern_dictionary[patterns[i]] ]
            wr.writerow(row)
            progress(i, len(patterns), ' Writing Token Pattern')

    list_token_code_index.sort(key=myFunc)
    progress_info('Writing to CSV 2')
    with open(csv_output2, 'w', encoding='utf8') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, dialect='excel', lineterminator='\n')
        wr.writerows(list_token_code_index)

    return patterns


def remove_line_with_patterns_and_append_with_logs(included_patterns, excluded_patterns, inputFile, outputFile):
    
    cs_ast = read_lines('data/uswf/token_vocab.txt')

    rejected_codes = [
        'foreach',
        'while',
        'public',
        'private',
        'protected',
        'class'
    ]

    """
    Remove lines that start with any of the given patterns from the input file, 
    check for duplicates, and append the rest to the output file, with logging.

    Args:
        patterns (list): A list of string patterns to check.
        inputFile (str): Path to the input file.
        outputFile (str): Path to the output file.
    """
    # Read existing lines from the output file to avoid duplicates
    try:
        with open(outputFile, 'r', encoding='utf8') as outfile:
            existing_lines = set(outfile.readlines())
        progress_info(f"Loaded {len(existing_lines)} existing lines from {outputFile}.")
    except FileNotFoundError:
        # If the output file doesn't exist, initialize an empty set
        existing_lines = set()
        progress_info(f"{outputFile} does not exist. Creating a new one.")

    # Read input file and process lines
    with open(inputFile, 'r', encoding='utf8') as infile:
        lines = infile.readlines()
    progress_info(f"Loaded {len(lines)} lines from {inputFile}.")

    written = 0
    # Open the output file for appending
    with open(outputFile, 'w', encoding='utf8') as outfile:
        total = len(lines)
        for idx, line in enumerate(lines, start=1):
            try:

                token_code = line.split('~')
                token_line = token_code[0].rstrip().lstrip().strip()
                code = token_code[1].rstrip().lstrip().strip()

                codes = code.split()
                found = [item for item in codes if item in rejected_codes]

                if (code == '' or len(found) > 0):
                    print('skip rejected word', code)
                    continue

                if (token_line == 'IdentifierName SimpleMemberAccessExpression'):
                    print('skip IdentifierName SimpleMemberAccessExpression')
                    continue

                if (token_line.startswith('VariableDeclaration') and len(token_line.split()) <= 2):
                    if ('InvocationExpression' not in token_line):
                        print('skip simple VariableDeclaration ', idx, ' ', token_line)
                        continue
                #VariableDeclaration IdentifierName NullLiteralExpression
                #VariableDeclaration IdentifierName NullLiteralExpression VariableDeclarator
                if (token_line == 'VariableDeclaration IdentifierName NumericLiteralExpression'):
                    print('skip simple VariableDeclaration IdentifierName NumericLiteralExpression ', idx, ' ', token_line)
                    continue

                if ('IdentifierName' in token_line and 'InvocationExpression' not in token_line and len(token_line.split()) <= 2):
                    print('skip simple VariableDeclaration ', idx, ' ', token_line)
                    continue

                if (len(token_line.split()) <= 2 and idx > 100000):
                    if ('InvocationExpression' not in token_line):
                        print('skip simple <= 2 ', idx, ' ', token_line)
                        continue

                if (token_line.startswith('VariableDeclaration') and len(token_line.split()) <= 3 and idx > 100000):
                    if ('InvocationExpression' not in token_line):
                        print('skip simple VariableDeclaration ', idx, ' ', token_line)
                        continue

                if ('IdentifierName' in token_line and 'InvocationExpression' not in token_line and len(token_line.split()) <= 3 and idx > 100000):
                    print('skip simple VariableDeclaration ', idx, ' ', token_line)
                    continue

                if (len(token_line.split()) <= 3 and idx > 100000):
                    if ('InvocationExpression' not in token_line):
                        print('skip simple <= 3 ', idx, ' ', token_line)
                        continue

                parts = token_line.split()
                if len(parts) > 1:
                    if (parts[0] not in cs_ast):
                        print('invalid token ', parts[0])
                        continue
                else:
                    if ('InvocationExpression' not in token_line):
                        continue

                if any(token_line == pattern for pattern in excluded_patterns):
                    progress_info(f"Skipped line {idx}: Equal with excluded pattern.")
                    continue

                if line in existing_lines:
                    progress_info(f"Skipped line {idx}: Duplicate line.")
                    continue

                if any(token_line == pattern for pattern in included_patterns):
                    # Write to the output file and log the action
                    outfile.write(line)
                    progress_info(f"Appended line {idx} to {outputFile}.")
                    written = written + 1
                
                # Update progress
                progress(written, total, "Processing lines")
            
            except:
                progress_info('Error, Skip')
                continue

    print("Processing complete! Written ", written)


def remove_line_with_patterns_and_append_txt(included_ast_tokens, must_excluded_ast_patterns, inputFile, outputFile):
    
    cs_ast = read_lines('data/uswf/token_vocab.txt')

    rejected_codes = [
        'foreach',
        'while',
        'public',
        'private',
        'protected',
        'class',
        'SuppressMessage',
        'Deprecated',
        'Obselete'
    ]

    # Read input file and process lines
    with open(inputFile, 'r', encoding='utf8') as infile:
        lines = infile.readlines()
    progress_info(f"Loaded {len(lines)} lines from {inputFile}.")

    written = 0
    # Open the output file for appending
    with open(outputFile, 'w', encoding='utf8') as outfile:
        total = len(lines)
        for idx, line in enumerate(lines, start=1):
            token_code = line.split('~')
            token = token_code[0].rstrip().lstrip().strip()
            code = token_code[1].rstrip().lstrip().strip()

            tokens = token.split()
            codes = code.split()

            invalid_tokens = [item for item in tokens if item not in cs_ast]
            if (token == '' or len(invalid_tokens) > 0 or code == ''):
                print('contains invalid token or invalid code ', token, ' ', code)
                continue
            
            mandatory_tokens = [item for item in tokens if item in included_ast_tokens]

            if (len(mandatory_tokens) < 1):
                print('skip unexpected  ', idx, ' ', token)
                continue

            if (len(tokens) < 2 and len(mandatory_tokens) < 1):
                print('skip simple < 2 ', idx, ' ', token)
                continue

            if (token in must_excluded_ast_patterns and 'InvocationExpression' not in token):
                print('skip simple must_excluded_ast_patterns ', idx, ' ', token)
                continue

            rejected_code_found = [item for item in codes if item in rejected_codes]
            if ((code == '' or len(rejected_code_found) > 0) and 'InvocationExpression' not in token):
                print('skip rejected word', code)
                continue

            # Write to the output file and log the action
            outfile.write(line)
            progress_info(f"Appended line {idx} to {outputFile}.")
            written = written + 1
            
            # Update progress
            progress(written, total, "Processing lines")
        
    print("Processing complete! Written ", written)


def remove_lines_with_excluded_included_combination(inputFile, outputFile):
    
    # Read input file and process lines
    with open(inputFile, 'r', encoding='utf8') as infile:
        lines = infile.readlines()
    progress_info(f"Loaded {len(lines)} lines from {inputFile}.")

    written = 0
    # Open the output file for appending
    with open(outputFile, 'w', encoding='utf8') as outfile:
        total = len(lines)
        for idx, line in enumerate(lines, start=1):
            token_code = line.split('~')
            token = token_code[0].rstrip().lstrip().strip()
            code = token_code[1].rstrip().lstrip().strip()

            if (token == '' or code == ''):
                continue

            tokens = token.split()
            codes = code.split()

            if (len(tokens) <= 1 or len(codes) <= 1):
                continue

            invalid_tokens = [item for item in tokens if item not in cs_ast]
            
            mandatory_tokens = [item for item in tokens if item in included_ast_tokens]

            rejected_tokens = [item for item in tokens if item in excluded_ast_tokens]

            rejected_codes = [item for item in codes if item in excluded_codes]

            is_proceed = False
            if (len(mandatory_tokens) > 0 and len(rejected_codes) == 0 and len(rejected_tokens) == 0):
                is_proceed = True
            elif (len(invalid_tokens) > 0):
                is_proceed = False
            elif (len(rejected_tokens) > 0):
                is_proceed = False
            elif (len(rejected_codes) > 0):
                is_proceed = False
            elif (token in excluded_ast_patterns):
                is_proceed = False
            else:
                is_proceed = True

            if (is_proceed == False):
                progress_info(f"Skip line {idx} {token}.")
                continue

            # Write to the output file and log the action
            outfile.write(line)
            progress_info(f"Appended line {idx} to {outputFile}.")
            written = written + 1
            
            # Update progress
            progress(written, total, "Processing lines")
        
    print("Processing complete! Written ", written)


def sliceDataset(inputFile, outputFile, fromIndex, count):
    print(f'Slicing: {inputFile} to {outputFile}')

    slicesList = []
    toIndex = fromIndex + count
    currentIndex = 0

    with open(inputFile, 'r', encoding='utf8') as f:
        for line in f:
            if fromIndex <= currentIndex < toIndex:
                slicesList.append(line.rstrip('\n'))
            elif currentIndex >= toIndex:
                break
            currentIndex += 1

    print('Total sliced:', len(slicesList))

    toTextFile(slicesList, outputFile, mode='w')


cs_ast = read_lines('data/uswf/token_vocab.txt')

excluded_codes = [
    'foreach',
    'while',
    'public',
    'private',
    'protected',
    'internal',
    'abstract',
    'class',
    'for',
    'if',
    'do'
]

excluded_ast_patterns = [
    'SimpleMemberAccessExpression IdentifierName ThisExpression QualifiedName NumericLiteralExpression',
    'VariableDeclaration IdentifierName VariableDeclarator SimpleMemberAccessExpression',
    'TypeArgumentList IdentifierName NullableType PredefinedType',
    'IdentifierName SimpleMemberAccessExpression',
    'VariableDeclaration IdentifierName NullLiteralExpression',
    'VariableDeclaration IdentifierName NullLiteralExpression VariableDeclarator',
    'SimpleAssignmentExpression IdentifierName',
    'SimpleAssignmentExpression IdentifierName SimpleMemberAccessExpression',
    'VariableDeclaration IdentifierName ObjectCreationExpression',
    'SimpleAssignmentExpression IdentifierName StringLiteralExpression',
    'SimpleAssignmentExpression IdentifierName NumericLiteralExpression',
    'IdentifierName ExpressionStatement SimpleMemberAccessExpression NumericLiteralExpression',
    'SimpleAssignmentExpression IdentifierName ArgumentList',
    'SimpleAssignmentExpression IdentifierName TrueLiteralExpression',
    'SimpleAssignmentExpression IdentifierName NullLiteralExpression',
    'PredefinedType ParameterList',
    'TypeArgumentList PredefinedType',
    'VariableDeclaration PredefinedType VariableDeclarator',
    'IdentifierName SimpleMemberAccessExpression StringLiteralExpression',
    'VariableDeclaration IdentifierName SimpleMemberAccessExpression',
    'PredefinedType IdentifierName',
    'VariableDeclaration IdentifierName VariableDeclarator',
    'SimpleMemberAccessExpression IdentifierName',
    'IdentifierName PointerType VariableDeclarator',
    'IdentifierName StringLiteralExpression',
    'SimpleAssignmentExpression IdentifierName FalseLiteralExpression',
    'SimpleAssignmentExpression IdentifierName TrueLiteralExpression'
]

excluded_ast_tokens = [
    'Attribute',
]

included_ast_tokens = [
    'InterpolatedStringStartToken',
    'InterpolatedStringEndToken',
    'InterpolatedVerbatimStringStartToken',
    'InterpolatedStringToken',
    'InterpolatedStringTextToken',
    'SingleLineRawStringLiteralToken',
    'MultiLineRawStringLiteralToken',
    'Utf8StringLiteralToken',
    'Utf8SingleLineRawStringLiteralToken',
    'Utf8MultiLineRawStringLiteralToken',
    'ConditionalExpression',
    'InvocationExpression',
    'AnonymousMethodExpression',
    'SimpleLambdaExpression',
    'InterpolatedStringExpression',
    'RangeExpression',
    'AddExpression',
    'SubtractExpression',
    'MultiplyExpression',
    'DivideExpression',
    'ModuloExpression',
    'LeftShiftExpression',
    'RightShiftExpression',
    'LogicalOrExpression',
    'LogicalAndExpression',
    'BitwiseOrExpression',
    'BitwiseAndExpression',
    'ExclusiveOrExpression',
    'AddAssignmentExpression',
    'SubtractAssignmentExpression',
    'MultiplyAssignmentExpression',
    'DivideAssignmentExpression',
    'ModuloAssignmentExpression',
    'AndAssignmentExpression',
    'ExclusiveOrAssignmentExpression',
    'OrAssignmentExpression',
    'LeftShiftAssignmentExpression',
    'RightShiftAssignmentExpression',
    'CoalesceAssignmentExpression',
    'UnsignedRightShiftAssignmentExpression',
    'TypeOfExpression',
    'SizeOfExpression',
    'CheckedExpression',
    'UncheckedExpression',
    'DefaultExpression',
    'MakeRefExpression',
    'RefValueExpression',
    'RefTypeExpression',
    'QueryExpression',
    'QueryBody',
    'FromClause',
    'LetClause',
    'JoinClause',
    'JoinIntoClause',
    'WhereClause',
    'OrderByClause',
    'AscendingOrdering',
    'DescendingOrdering',
    'SelectClause',
    'GroupClause',
    'QueryContinuation',
    'Interpolation',
    'InterpolatedStringText',
    'InterpolationAlignmentClause',
    'InterpolationFormatClause',
    'FunctionPointerType',
    'FunctionPointerParameter',
    'FunctionPointerParameterList',
    'FunctionPointerCallingConvention',
    'InitAccessorDeclaration',
    'FunctionPointerUnmanagedCallingConventionList',
    'FunctionPointerUnmanagedCallingConvention',
    'InterpolatedSingleLineRawStringStartToken',
    'InterpolatedMultiLineRawStringStartToken',
    'InterpolatedRawStringEndToken',
    'MinusMinusToken',
    'PlusPlusToken',
    'SlashEqualsToken',
    'AsteriskEqualsToken',
    'BarEqualsToken',
    'AmpersandEqualsToken',
    'PlusEqualsToken',
    'MinusEqualsToken',
    'CaretEqualsToken',
    'PercentEqualsToken',
    'EventKeyword',
    'UsingKeyword',
    'AddKeyword',
    'RemoveKeyword',
    'WhereKeyword',
    'FromKeyword',
    'GroupKeyword',
    'JoinKeyword',
    'IntoKeyword',
    'SelectKeyword',
    'OrderByKeyword',
    'OnKeyword',
    'EqualsKeyword',
    'AscendingKeyword',
    'DescendingKeyword',
    'LoadKeyword',
    'CastExpression',
    'ObjectInitializerExpression',
    'ObjectCreationExpression',
    'ImplicitObjectCreationExpression',
    'ComplexElementInitializerExpression',
    'EqualsExpression',
    'NotEqualsExpression',
    'LessThanExpression',
    'LessThanOrEqualExpression',
    'GreaterThanExpression',
    'GreaterThanOrEqualExpression',
    'IsExpression',
    'AsExpression',
    'CoalesceExpression',
    'ExpressionStatement',
    'UsingStatement'
]


if __name__ == '__main__':

    remove_lines_with_excluded_included_combination('clusters/small_token_code_lines_01.txt', 'clusters/small_token_code_lines_01_a.txt')

    remove_duplicates('clusters/small_token_code_lines_01_a.txt', 'clusters/small_token_code_lines_01_b.txt')

    sliceDataset('clusters/small_token_code_lines_01_b.txt', 'clusters/token_code_lines_0500k.txt', 0, 500000)

    disticted_tokens = trim_tokens_pattern_txt('clusters/token_code_lines_0500k.txt')
    count_token_patterns_txt(disticted_tokens, 
                             'clusters/token_code_lines_0500k.txt', 
                             'clusters/token_code_lines_0500k_summary.csv', 
                             'clusters/token_code_lines_0500k_details.csv')
