import json
import re


def toTextFile(lines, outputFile):
    outputs = ''
    for line in lines:
        outputs += line + '\n'
    with open(outputFile, 'w', encoding='utf8') as f:
        f.write(outputs)

def sliceDataset(inputFile, outputFile, fromIndex, count):
    print('Slicing: ' + inputFile + ' to ' + outputFile)

    with open(inputFile, 'r', encoding='utf8') as f:
        inputText = f.read()

    sourceList = inputText.splitlines()

    print('Slicing ', len(sourceList), ' from ', fromIndex, ' count ', count)

    toIndex = fromIndex + count
    if (toIndex >= len(sourceList)):
        toIndex = len(sourceList) - 1

    slicesList = sourceList[fromIndex:toIndex]

    print(len(slicesList))

    toTextFile(slicesList, outputFile)


def remove_json_empty_sequence(input_path, output_path, requirements_input_file, requirements_output_file):
    with open(input_path, 'r', encoding='utf8') as infile:
        lines = infile.readlines()

    with open(requirements_input_file, 'r', encoding='utf8') as req_in_file:
        original_requirements = req_in_file.readlines()

    requirements = []
    dsl_lines = []
    
    for i, line in enumerate(lines):
        workflow = json.loads(line)
        if 'Seq' not in workflow or not workflow['Seq']:
            continue

        dsl_lines.append(line)
        requirements.append(original_requirements[i])

        if i % 100 == 0:
            print(f"Processed {i}/{len(lines)}")

    with open(output_path, 'w', encoding='utf8') as outfile:
        for line in dsl_lines:
            outfile.write(line)

    with open(requirements_output_file, 'w', encoding='utf8') as requirement_outfile:
        for line in requirements:
            requirement_outfile.write(line)


if __name__ == '__main__':

    print()

    remove_json_empty_sequence(
        'dataset/trimmed_small_workflows_ast.ndjson',
        'dataset/trimmed_small_workflows_ast_clean.txt',
        'dataset/trimmed_small_descriptions_corrected.txt',
        'dataset/trimmed_small_descriptions_ast.txt',
    )

    sliceDataset('dataset/trimmed_small_workflows_ast_clean.txt', 'dataset/json_ast/wf_json_ast_0100k.txt', 0, 100000)
    sliceDataset('dataset/trimmed_small_workflows_ast_clean.txt', 'dataset/json_ast/wf_json_ast_0020k.txt', 100000, 20000)
    sliceDataset('dataset/trimmed_small_workflows_ast_clean.txt', 'dataset/json_ast/wf_json_ast_0010k.txt', 120000, 10000)
    sliceDataset('dataset/trimmed_small_workflows_ast_clean.txt', 'dataset/json_ast/wf_json_ast_0005k.txt', 130000, 5000)
    sliceDataset('dataset/trimmed_small_workflows_ast_clean.txt', 'dataset/json_ast/wf_json_ast_0120k.txt', 0, 120000)

    sliceDataset('dataset/trimmed_small_descriptions_ast.txt', 'dataset/json_ast/tx_json_ast_0100k.txt', 0, 100000)
    sliceDataset('dataset/trimmed_small_descriptions_ast.txt', 'dataset/json_ast/tx_json_ast_0020k.txt', 100000, 20000)
    sliceDataset('dataset/trimmed_small_descriptions_ast.txt', 'dataset/json_ast/tx_json_ast_0010k.txt', 120000, 10000)
    sliceDataset('dataset/trimmed_small_descriptions_ast.txt', 'dataset/json_ast/tx_json_ast_0005k.txt', 130000, 5000)
    sliceDataset('dataset/trimmed_small_descriptions_ast.txt', 'dataset/json_ast/tx_json_ast_0120k.txt', 0, 120000)


    remove_json_empty_sequence(
        'dataset/trimmed_small_workflows_code.ndjson',
        'dataset/trimmed_small_workflows_code_clean.txt',
        'dataset/trimmed_small_descriptions_corrected.txt',
        'dataset/trimmed_small_descriptions_code.txt',
    )

    sliceDataset('dataset/trimmed_small_workflows_code_clean.txt', 'dataset/json_code/wf_json_code_0100k.txt', 0, 100000)
    sliceDataset('dataset/trimmed_small_workflows_code_clean.txt', 'dataset/json_code/wf_json_code_0020k.txt', 100000, 20000)
    sliceDataset('dataset/trimmed_small_workflows_code_clean.txt', 'dataset/json_code/wf_json_code_0010k.txt', 120000, 10000)
    sliceDataset('dataset/trimmed_small_workflows_code_clean.txt', 'dataset/json_code/wf_json_code_0005k.txt', 130000, 5000)
    sliceDataset('dataset/trimmed_small_workflows_code_clean.txt', 'dataset/json_code/wf_json_code_0120k.txt', 0, 120000)

    sliceDataset('dataset/trimmed_small_descriptions_code.txt', 'dataset/json_code/tx_json_code_0100k.txt', 0, 100000)
    sliceDataset('dataset/trimmed_small_descriptions_code.txt', 'dataset/json_code/tx_json_code_0020k.txt', 100000, 20000)
    sliceDataset('dataset/trimmed_small_descriptions_code.txt', 'dataset/json_code/tx_json_code_0010k.txt', 120000, 10000)
    sliceDataset('dataset/trimmed_small_descriptions_code.txt', 'dataset/json_code/tx_json_code_0005k.txt', 130000, 5000)
    sliceDataset('dataset/trimmed_small_descriptions_code.txt', 'dataset/json_code/tx_json_code_0120k.txt', 0, 120000)
