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

def convert_expression(expr) -> str:
    """Replace verbose logical expressions with symbolic tokens using regex."""
    patterns = [
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"==",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LEqR'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"(!=)",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LNeR'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"!",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LNoR'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*">",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LGtR'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*">=",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LGeR'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"<",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LLtR'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"<=",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LLeR'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"==",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LEqRAnd'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"!=",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LNeRAnd'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"!",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LNoRAnd'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*">",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LGtRAnd'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*">=",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LGeRAnd'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"<",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LLtRAnd'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"<=",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LLeRAnd'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"==",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LEqROr'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"!=",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LNeROr'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"!",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LNoROr'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*">",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LGtROr'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*">=",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LGeROr'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"<",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LLtROr'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"<=",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LLeROr'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LTrue'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LTrueAnd'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LTrueOr'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"in",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LTrue'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"in",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LTrue'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"in",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"OR"\}', 'LTrue'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*""\}', 'LTrue'),
        (r'\{"Lt":\s*"(.*?)",\s*"Op":\s*"",\s*"Rt":\s*"(.*?)",\s*"Conj":\s*"AND"\}', 'LTrue'),
        (r'^.*$', 'LTrue'),
    ]
    dsl = json.dumps(expr)
        
    for pattern, token in patterns:
        dsl = re.sub(pattern, token, dsl)
        
    return dsl

def convert_node(node):
    """Convert a node recursively to DSL."""
    comp_type = node.get('Comp', '').strip()
    desc = node.get('Desc', '').strip()
    seq = node.get('Seq', [])
    expr = node.get('Exp', [])

    if comp_type not in ['IF', 'LOOP'] or not seq:
        return f"{{ {desc} }}"

    inner_seq = ' '.join([convert_node(child) for child in seq])

    if expr:
        expr_tokens = ' '.join([convert_expression(e) for e in expr])
        return f"{{ {comp_type} Exp [ {expr_tokens} ] Seq [ {inner_seq} ] }}"
    else:
        return f"{{ {comp_type} Seq [ {inner_seq} ] }}"

def convert_workflow_to_ssf_label(workflow):
    inputs = ' '.join([p['Type'] for p in workflow.get('In', [])])
    outputs = ' '.join([p['Type'] for p in workflow.get('Out', [])])
    seq_items = ' '.join([convert_node(node) for node in workflow.get('Seq', [])])
    return f"{{ In [ {inputs} ] Out [ {outputs} ] Seq [ {seq_items} ] }}"

def convert_ndjson_to_ssf_label(input_path, output_path, requirements_input_file, requirements_output_file):
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
        dsl = convert_workflow_to_ssf_label(workflow)
        dsl_lines.append(dsl)

        requirements.append(original_requirements[i])

        if i % 100 == 0:
            print(f"Processed {i}/{len(lines)}")

    with open(output_path, 'w', encoding='utf8') as outfile:
        for line in dsl_lines:
            outfile.write(line + '\n')

    with open(requirements_output_file, 'w', encoding='utf8') as requirement_outfile:
        for line in requirements:
            requirement_outfile.write(line)


if __name__ == '__main__':

    print()

    convert_ndjson_to_ssf_label(
        'dataset/trimmed_small_workflows_label.ndjson',
        'dataset/trimmed_small_workflows_label.txt',
        'dataset/trimmed_small_descriptions_corrected.txt',
        'dataset/trimmed_small_descriptions_label.txt',
    )

    sliceDataset('dataset/trimmed_small_workflows_label.txt', 'dataset/ssf_label/wf_ssf_label_0100k.txt', 0, 100000)
    sliceDataset('dataset/trimmed_small_workflows_label.txt', 'dataset/ssf_label/wf_ssf_label_0020k.txt', 100000, 20000)
    sliceDataset('dataset/trimmed_small_workflows_label.txt', 'dataset/ssf_label/wf_ssf_label_0010k.txt', 120000, 10000)
    sliceDataset('dataset/trimmed_small_workflows_label.txt', 'dataset/ssf_label/wf_ssf_label_0005k.txt', 130000, 5000)
    sliceDataset('dataset/trimmed_small_workflows_label.txt', 'dataset/ssf_label/wf_ssf_label_0120k.txt', 0, 120000)

    sliceDataset('dataset/trimmed_small_descriptions_label.txt', 'dataset/ssf_label/tx_ssf_label_0100k.txt', 0, 100000)
    sliceDataset('dataset/trimmed_small_descriptions_label.txt', 'dataset/ssf_label/tx_ssf_label_0020k.txt', 100000, 20000)
    sliceDataset('dataset/trimmed_small_descriptions_label.txt', 'dataset/ssf_label/tx_ssf_label_0010k.txt', 120000, 10000)
    sliceDataset('dataset/trimmed_small_descriptions_label.txt', 'dataset/ssf_label/tx_ssf_label_0005k.txt', 130000, 5000)
    sliceDataset('dataset/trimmed_small_descriptions_label.txt', 'dataset/ssf_label/tx_ssf_label_0120k.txt', 0, 120000)

