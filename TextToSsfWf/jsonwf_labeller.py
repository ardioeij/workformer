
import csv
import json
import subprocess
import sys

from codet5 import Codet5


def progress(current, total, desc):
    sys.stdout.write('\r')  # Move back to the beginning of the line
    sys.stdout.write(f'{current} / {total} {desc}')
    sys.stdout.flush()


def read_lines(input_file):
    with open(input_file, 'r', encoding='utf8') as f:
        inputText = f.read()
        sourceList = inputText.splitlines()
    
    return sourceList


def recursiveNodes(codet5Transformer, node, parent=None, index=None):
          
    if ('Seq' in node and node['Seq'] != None and len(node['Seq']) > 0):
        for i in range(len(node['Seq']) - 1, -1, -1):
            recursiveNodes(codet5Transformer, node['Seq'][i], node['Seq'], i)

    if (node['Desc'] != None and node['Comp'] != None):

        if (node['Desc'] != ''):
            
            text = codet5Transformer.generate(node['Desc'], 16)
            if (text != ''):
                node['Desc'] = text.replace('  ', ' ')

            del node['Token']
            

def label_json_node(input_file, output_file, start_index=0, count = None):
    codet5Transformer = Codet5()

    default_ndjsons = read_lines(input_file)
    if count == None:
        count = len(default_ndjsons)
    
    lines = default_ndjsons[start_index: count]
    count = len(lines)
    print('count ', count)

    with open(output_file, "a", encoding="utf-8") as outfile:
    
        for i in range(0, count, 1):
            progress(i, count, '')

            line = lines[i]
            wf = json.loads(line)

            recursiveNodes(codet5Transformer, wf)
            del wf['Desc']
            del wf['Token']
            del wf['Comp']

            json_output = json.dumps(wf)
            json_output = json_output.replace('  ', '').replace(' .', '')
            print(json_output)
            outfile.write(json_output + "\n")
            outfile.flush()


if __name__ == "__main__":
    
    print()

    label_json_node('dataset/trimmed_small_workflows.ndjson', 'dataset/trimmed_small_workflows_label.ndjson')
