import json
import re
import sys
from ssf_clustering import SourceCodeClusterization


def progress(index, count):
    sys.stdout.write('\r')
    sys.stdout.write(str(index) + ' / ' + str(count) + ' ')
    sys.stdout.flush()        
    
def read_lines(input_file):
    with open(input_file, 'r', encoding='utf8') as f:
        inputText = f.read()
        sourceList = inputText.splitlines()
    return sourceList

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


cs_ast = read_lines('dataset/token_vocab.txt')

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


def getWorkflowEmbeddingsDictionary(max_clusters):
    embeddings = {} 

    embeddings['\[PAD\]'] = '[PAD]', len(embeddings) # type: ignore
    embeddings['\[UNK\]'] = '[UNK]', len(embeddings) # type: ignore
    embeddings['\[START\]'] = '[START]', len(embeddings) # type: ignore
    embeddings['\[END\]'] = '[END]', len(embeddings) # type: ignore

    embeddings['Comp:IF'] = 'IF', len(embeddings)
    embeddings['Comp:ELSE'] = 'ELSE', len(embeddings)
    embeddings['Comp:LOOP'] = 'LOOP', len(embeddings)
    
    for i in range(0, max_clusters + 1, 1):
        comp_proc = 'Comp:PROC' + str(i).zfill(4)
        proc = 'PROC' + str(i).zfill(4)
        embeddings[comp_proc] = proc, len(embeddings)

    embeddings['{Lt:\s*((?:.|\n)*?),Op:==,Rt:\s*((?:.|\n)*?),Conj:}'] = 'LEqR', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:!=,Rt:\s*((?:.|\n)*?),Conj:}'] = 'LNeR', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:!,Rt:\s*((?:.|\n)*?),Conj:}'] = 'LNoR', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:>,Rt:\s*((?:.|\n)*?),Conj:}'] = 'LGtR', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:>=,Rt:\s*((?:.|\n)*?),Conj:}'] = 'LGeR', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:<,Rt:\s*((?:.|\n)*?),Conj:}'] = 'LLtR', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:<=,Rt:\s*((?:.|\n)*?),Conj:}'] = 'LLeR', len(embeddings)  # type: ignore

    embeddings['{Lt:\s*((?:.|\n)*?),Op:==,Rt:\s*((?:.|\n)*?),Conj:AND}'] = 'LEqRAnd', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:!=,Rt:\s*((?:.|\n)*?),Conj:AND}'] = 'LNeRAnd', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:!,Rt:\s*((?:.|\n)*?),Conj:AND}'] = 'LNoRAnd', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:>,Rt:\s*((?:.|\n)*?),Conj:AND}'] = 'LGtRAnd', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:>=,Rt:\s*((?:.|\n)*?),Conj:AND}'] = 'LGeRAnd', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:<,Rt:\s*((?:.|\n)*?),Conj:AND}'] = 'LLtRAnd', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:<=,Rt:\s*((?:.|\n)*?),Conj:AND}'] = 'LLeRAnd', len(embeddings)  # type: ignore

    embeddings['{Lt:\s*((?:.|\n)*?),Op:==,Rt:\s*((?:.|\n)*?),Conj:OR}'] = 'LEqROr', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:!=,Rt:\s*((?:.|\n)*?),Conj:OR}'] = 'LNeROr', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:!,Rt:\s*((?:.|\n)*?),Conj:OR}'] = 'LNoROr', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:>,Rt:\s*((?:.|\n)*?),Conj:OR}'] = 'LGtROr', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:>=,Rt:\s*((?:.|\n)*?),Conj:OR}'] = 'LGeROr', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:<,Rt:\s*((?:.|\n)*?),Conj:OR}'] = 'LLtROr', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:<=,Rt:\s*((?:.|\n)*?),Conj:OR}'] = 'LLeROr', len(embeddings)  # type: ignore

    embeddings['{Lt:\s*((?:.|\n)*?),Op:,Rt:\s*((?:.|\n)*?),Conj:}'] = 'LTrue', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:,Rt:\s*((?:.|\n)*?),Conj:AND}'] = 'LTrueAnd', len(embeddings)  # type: ignore
    embeddings['{Lt:\s*((?:.|\n)*?),Op:,Rt:\s*((?:.|\n)*?),Conj:OR}'] = 'LTrueOr', len(embeddings)  # type: ignore
    
    embeddings['{Prm:\s*((?:.|\n)*?),Type:String}'] = 'String', len(embeddings)  # type: ignore
    embeddings['{Prm:\s*((?:.|\n)*?),Type:Integer}'] = 'Integer', len(embeddings)  # type: ignore
    embeddings['{Prm:\s*((?:.|\n)*?),Type:Decimal}'] = 'Decimal', len(embeddings)  # type: ignore
    embeddings['{Prm:\s*((?:.|\n)*?),Type:Boolean}'] = 'Boolean', len(embeddings)  # type: ignore
    embeddings['{Prm:\s*((?:.|\n)*?),Type:DateTime}'] = 'DateTime', len(embeddings)  # type: ignore
    embeddings['{Prm:\s*((?:.|\n)*?),Type:Object}'] = 'Object', len(embeddings)  # type: ignore

    embeddings['Seq:'] = 'Seq', len(embeddings)
    embeddings['In:'] = 'In', len(embeddings)
    embeddings['Out:'] = 'Out', len(embeddings)
    embeddings['Exp:'] = 'Exp', len(embeddings)

    embeddings['\['] = '[', len(embeddings)  # type: ignore
    embeddings['\]'] = ']', len(embeddings)  # type: ignore
    embeddings['{'] = '{', len(embeddings)
    embeddings['}'] = '}', len(embeddings)
    
    embeddings['Comp:WF'] = 'WF', len(embeddings)

    return embeddings

def getCluster(code, token, max_tokens, max_clusters, clusterer):
    if (code.startswith('"') and len(code) > 1):
        code = code[:0] + code[1:]

    if (code.endswith('"')):
        code = code[:(len(code)-1)] + code[(len(code)):]

    if (token.startswith('"') and len(token) > 1):
        token = token[:0] + token[1:]

    if (token.endswith('"')):
        token = token[:(len(token)-1)] + token[(len(token)):]

    tokens = token.split()
    codes = code.split()

    is_proceed = False

    if (len(tokens) <= 1 or len(codes) <= 1):
        is_proceed = False

    invalid_tokens = [item for item in tokens if item not in cs_ast]
    
    mandatory_tokens = [item for item in tokens if item in included_ast_tokens]

    rejected_tokens = [item for item in tokens if item in excluded_ast_tokens]

    rejected_codes = [item for item in codes if item in excluded_codes]

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
        return -1
    
    line = code + ' ~ ' + token + ' ~ '
    D, I = clusterer.search(line, max_tokens, max_clusters)

    return I[0]

def recursiveNodes(max_tokens, max_clusters, clusterer, node, parent=None, index=None):
    if ('Seq' in node and node['Seq'] != None and len(node['Seq']) > 0):
        for i in range(len(node['Seq']) - 1, -1, -1):
            recursiveNodes(max_tokens, max_clusters, clusterer, node['Seq'][i], node['Seq'], i)

    if (node['Desc'] != None and node['Comp'] != None and node['Token'] != None):
        if (node['Comp'] == 'PROC'):
            cluster = getCluster(node['Desc'], node['Token'], max_tokens, max_clusters, clusterer)
            if (cluster == -1):
                # Remove the node from the parent's sequence if applicable
                if parent is not None and index is not None:
                    del parent[index]
                return  # Stop further processing of this node

            node['Comp'] = 'PROC' + str(cluster[0]).zfill(4)

        node['Desc'] = ''
        del node['Desc']
        del node['Token']

def createWorkflowNormalizeEmbeddings(clusterer, max_tokens, max_clusters, wf_json_input_file, wf_json_output_file, requirements_input_file, requirements_output_file):
    print('createWorkflowNormalizeEmbeddings ' + wf_json_input_file + ' => ' + wf_json_output_file)

    with open(wf_json_input_file, 'r', encoding='utf8') as wf_file:
        text = wf_file.read()

    text = text.replace('  ', '')

    original_requirements = read_lines(requirements_input_file)

    requirements = []

    newlines=[]
    lines = text.splitlines()
    count = len(lines)
    for i in range(0, count, 1):

        line = lines[i]

        progress(i, count)
        
        wf = json.loads(line)
        recursiveNodes(max_tokens, max_clusters, clusterer, wf)

        del wf["Comp"]

        if (len(wf['Seq']) == 0):
            continue

        line = json.dumps(wf)

        newlines.append(line)

        requirements.append(original_requirements[i])

    toTextFile(newlines, wf_json_output_file)

    toTextFile(requirements, requirements_output_file)


def convert_expression(expr, max_clusters) -> str:
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

    for i in range(max_clusters + 1):
        proc_id = f'PROC{str(i).zfill(4)}'
        pattern = rf'\{{"Comp":\s*"{proc_id}"\}}'
        patterns.append((pattern, proc_id))

    dsl = json.dumps(expr)
        
    for pattern, token in patterns:
        dsl = re.sub(pattern, token, dsl)
        
    return dsl

def convert_node(node, max_clusters):
    """Convert a node recursively to SSF."""
    comp_type = node.get('Comp', '').strip()
    seq = node.get('Seq', [])
    expr = node.get('Exp', [])

    inner_seq = ' '.join([convert_node(child, max_clusters) for child in seq])

    if expr:
        expr_tokens = ' '.join([convert_expression(e, max_clusters) for e in expr])
        if (inner_seq.strip() != '' or comp_type in ['IF', 'ELSE', 'LOOP']):
            return f"{{ {comp_type} Exp [ {expr_tokens} ] Seq [ {inner_seq} ] }}"
        else:
            return f"{{ {comp_type} Exp [ {expr_tokens} ] }}"
    else:
        if (inner_seq.strip() != '' and comp_type not in ['IF', 'ELSE', 'LOOP']):
            return f"{{ {comp_type} Seq [ {inner_seq} ] }}"
        elif (inner_seq.strip() != '' and comp_type in ['IF', 'ELSE', 'LOOP']):
            return f"{{ {comp_type} Seq [ {inner_seq} ] Exp [ ] }}"
        elif (inner_seq.strip() == '' and comp_type in ['IF', 'ELSE', 'LOOP']):
            return f"{{ {comp_type} Seq [ ] Exp [ ] }}"
        else:
            return f"{{ {comp_type} }}"

def convert_workflow_to_ssf(workflow, max_clusters):
    inputs = ' '.join([p['Type'] for p in workflow.get('In', [])])
    outputs = ' '.join([p['Type'] for p in workflow.get('Out', [])])
    seq_items = ' '.join([convert_node(node, max_clusters) for node in workflow.get('Seq', [])])
    return f"{{ In [ {inputs} ] Out [ {outputs} ] Seq [ {seq_items} ] }}"

def convert_ndjson_to_ssf(max_clusters, input_path, output_path, requirements_input_file, requirements_output_file):
    print('Convert NDJSON to SSF ' + input_path + ' => ' + output_path)

    with open(input_path, 'r', encoding='utf8') as infile:
        lines = infile.readlines()

    with open(requirements_input_file, 'r', encoding='utf8') as req_in_file:
        original_requirements = req_in_file.readlines()

    count = len(lines)
    requirements = []
    ssf_lines = []
    for i, line in enumerate(lines):
        workflow = json.loads(line)
        if 'Seq' not in workflow or not workflow['Seq']:
            continue
        
        ssf = convert_workflow_to_ssf(workflow, max_clusters)
        ssf_lines.append(ssf)

        requirements.append(original_requirements[i])
        
        progress(i, count)

    with open(output_path, 'w', encoding='utf8') as outfile:
        for line in ssf_lines:
            outfile.write(line + '\n')

    with open(requirements_output_file, 'w', encoding='utf8') as requirement_outfile:
        for line in requirements:
            requirement_outfile.write(line)


def build_slice_ssf_dataset(max_clusters, max_tokens = 128):
    
    vocab_dataset_file = 'dataset/vocab/vocab_ssf_' + str(max_clusters).zfill(4) + '.txt'
    cluster_output_index_file = 'clusters/token_code_' + str(max_clusters).zfill(4) + '.index'
    
    wf_ndjson_input  = 'dataset/trimmed_small_workflows.ndjson'
    wf_ndjson_output = 'dataset/trimmed_small_workflows_' + str(max_clusters).zfill(4) + '.ndjson'
    tx_desc_input    = 'dataset/trimmed_small_descriptions_corrected.txt'
    tx_desc_output   = 'dataset/trimmed_small_descriptions_ssf_' + str(max_clusters).zfill(4) + '.txt'

    wf_ssf_output   = 'dataset/trimmed_small_workflows_ssf_' + str(max_clusters).zfill(4) + '.txt'

    clusterer = SourceCodeClusterization(vocab_dataset_file, max_tokens, [], cluster_output_index_file)

    print('Build SSF: ', max_clusters)
    print('wf_ndjson_input: ', wf_ndjson_input)
    print('wf_ndjson_output: ', wf_ndjson_output)
    print('tx_desc_input: ', tx_desc_input)
    print('tx_desc_output: ', tx_desc_output)

    createWorkflowNormalizeEmbeddings(clusterer, max_tokens, max_clusters,
        wf_ndjson_input, 
        wf_ndjson_output,
        tx_desc_input,
        tx_desc_output
    )
    
    convert_ndjson_to_ssf(max_clusters,
        wf_ndjson_output,
        wf_ssf_output,
        tx_desc_input,
        tx_desc_output,
    )

    ssf_folder   = 'dataset/ssf_' + str(max_clusters).zfill(4) + '/'

    ssf_wf_prefix = 'wf_ssf_' + str(max_clusters).zfill(4) + '_'
    sliceDataset(wf_ssf_output, ssf_folder + ssf_wf_prefix + '0100k.txt', 0, 100000)
    sliceDataset(wf_ssf_output, ssf_folder + ssf_wf_prefix + '0020k.txt', 100000, 20000)
    sliceDataset(wf_ssf_output, ssf_folder + ssf_wf_prefix + '0010k.txt', 120000, 10000)
    sliceDataset(wf_ssf_output, ssf_folder + ssf_wf_prefix + '0005k.txt', 130000, 5000)
    sliceDataset(wf_ssf_output, ssf_folder + ssf_wf_prefix + '0120k.txt', 0, 120000)

    ssf_tx_prefix = 'tx_ssf_' + str(max_clusters).zfill(4) + '_'
    sliceDataset(tx_desc_output, ssf_folder + ssf_tx_prefix + '0100k.txt', 0, 100000)
    sliceDataset(tx_desc_output, ssf_folder + ssf_tx_prefix + '0020k.txt', 100000, 20000)
    sliceDataset(tx_desc_output, ssf_folder + ssf_tx_prefix + '0010k.txt', 120000, 10000)
    sliceDataset(tx_desc_output, ssf_folder + ssf_tx_prefix + '0005k.txt', 130000, 5000)
    sliceDataset(tx_desc_output, ssf_folder + ssf_tx_prefix + '0120k.txt', 0, 120000)



if __name__ == '__main__':

    print()

    build_slice_ssf_dataset(384)

    print()

    build_slice_ssf_dataset(768)

    print()
