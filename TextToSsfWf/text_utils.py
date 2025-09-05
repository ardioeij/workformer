import re


def remove_desc_regex_ndjson(input_file, output_file):
    # Regex pattern to match "Desc": "..." optionally followed by a comma
    pattern = re.compile(r'"Desc"\s*:\s*"[^"]*"\s*,?')

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            cleaned_line = pattern.sub('', line)

            # Clean up extra commas caused by trailing "Desc"
            cleaned_line = re.sub(r',\s*([}\]])', r'\1', cleaned_line)

            outfile.write(cleaned_line.strip() + '\n')



if __name__ == '__main__':

    print()

    remove_desc_regex_ndjson("dataset/trimmed_small_workflows_cleaned.ndjson", "dataset/trimmed_small_workflows_ast.ndjson")