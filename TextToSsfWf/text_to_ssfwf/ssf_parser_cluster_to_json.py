import re
import json


def read_input_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().splitlines()


def reverse_ssf_to_json(expr: str) -> str:
    """Convert SSF symbolic tokens and PROCxxxx back to JSON format."""
    
    expr = expr.replace('\n', ' ')
    expr = re.sub(r'\s+', ' ', expr).strip()

    # Step 1: reverse symbolic logic tokens
    patterns = [
        
        (r'\bIn\b', '"In":'),
        (r'\bOut\b', '"Out":'),
        (r'\bSeq\b', '"Seq":'),
        (r'\bExp\b', '"Exp":'),

        (r'\bIF\b', '"Comp":"IF"'),
        (r'\bELSE\b', '"Comp":"ELSE"'),
        (r'\bLOOP\b', '"Comp":"LOOP"'),
        (r'\bPROC(\d{4})\b', r'"Comp":"PROC\1"'),

        ('LEqRAnd', '{"Lt": "LEqRAnd", "Op": "==", "Rt": "", "Conj": "AND"}'),
        ('LNeRAnd', '{"Lt": "LNeRAnd", "Op": "!=", "Rt": "", "Conj": "AND"}'),
        ('LNoRAnd', '{"Lt": "LNoRAnd", "Op": "!", "Rt": "", "Conj": "AND"}'),
        ('LGtRAnd', '{"Lt": "LGtRAnd", "Op": ">", "Rt": "", "Conj": "AND"}'),
        ('LGeRAnd', '{"Lt": "LGeRAnd", "Op": ">=", "Rt": "", "Conj": "AND"}'),
        ('LLtRAnd', '{"Lt": "LLtRAnd", "Op": "<", "Rt": "", "Conj": "AND"}'),
        ('LLeRAnd', '{"Lt": "LLeRAnd", "Op": "<=", "Rt": "", "Conj": "AND"}'),

        ('LEqROr', '{"Lt": "LEqROr", "Op": "==", "Rt": "", "Conj": "OR"}'),
        ('LNeROr', '{"Lt": "LNeROr", "Op": "!=", "Rt": "", "Conj": "OR"}'),
        ('LNoROr', '{"Lt": "LNoROr", "Op": "!", "Rt": "", "Conj": "OR"}'),
        ('LGtROr', '{"Lt": "LGtROr", "Op": ">", "Rt": "", "Conj": "OR"}'),
        ('LGeROr', '{"Lt": "LGeROr", "Op": ">=", "Rt": "", "Conj": "OR"}'),
        ('LLtROr', '{"Lt": "LLtROr", "Op": "<", "Rt": "", "Conj": "OR"}'),
        ('LLeROr', '{"Lt": "LLeROr", "Op": "<=", "Rt": "", "Conj": "OR"}'),

        ('LEqR', '{"Lt": "LEqR", "Op": "==", "Rt": "", "Conj": ""}'),
        ('LNeR', '{"Lt": "LNeR", "Op": "!=", "Rt": "", "Conj": ""}'),
        ('LNoR', '{"Lt": "LNoR", "Op": "!", "Rt": "", "Conj": ""}'),
        ('LGtR', '{"Lt": "LGtR", "Op": ">", "Rt": "", "Conj": ""}'),
        ('LGeR', '{"Lt": "LGeR", "Op": ">=", "Rt": "", "Conj": ""}'),
        ('LLtR', '{"Lt": "LLtR", "Op": "<", "Rt": "", "Conj": ""}'),
        ('LLeR', '{"Lt": "LLeR", "Op": "<=", "Rt": "", "Conj": ""}'),

        ('LTrueAnd', '{"Lt": "LTrueAnd", "Op": "", "Rt": "", "Conj": "AND"}'),
        ('LTrueOr',  '{"Lt": "LTrueOr", "Op": "", "Rt": "", "Conj": "OR"}'),
        ('LTrue',    '{"Lt": "LTrue", "Op": "", "Rt": "", "Conj": ""}'),

        (r'\bString\b',   '{"Prm": "", "Type":"String"}'),
        (r'\bInteger\b',  '{"Prm": "", "Type":"Integer"}'),
        (r'\bDecimal\b',  '{"Prm": "", "Type":"Decimal"}'),
        (r'\bBoolean\b',  '{"Prm": "", "Type":"Boolean"}'),
        (r'\bDateTime\b', '{"Prm": "", "Type":"DateTime"}'),
        (r'\bObject\b',   '{"Prm": "", "Type":"Object"}'),
    ]

    for token, replacement in patterns:
        expr = re.sub(token, replacement, expr, flags=re.IGNORECASE)
    
    expr = expr.replace('} {', '}, {')
    expr = expr.replace('] "', '], "')
    expr = expr.replace('" "', '", "')

    return expr


def check_and_fix_brackets(text: str, auto_fix: bool = True) -> tuple[str, bool, str]:
    """
    Checks and optionally fixes unbalanced { } and [ ] brackets.

    Returns:
        fixed_text (str): the possibly fixed version of the text
        is_balanced (bool): whether the original text was balanced
        message (str): diagnostic message
    """
    stack = []
    bracket_pairs = {'{': '}', '[': ']'}
    opening = set(bracket_pairs.keys())
    closing = set(bracket_pairs.values())
    inverse = {v: k for k, v in bracket_pairs.items()}
    position_map = []

    for idx, char in enumerate(text):
        if char in opening:
            stack.append((char, idx))
        elif char in closing:
            if not stack:
                return text, False, f"Unmatched closing bracket '{char}' at index {idx}"
            last_open, open_idx = stack.pop()
            if inverse[char] != last_open:
                return text, False, f"Mismatched bracket: '{last_open}' at {open_idx} vs '{char}' at {idx}"

    if stack:
        missing = ''.join(bracket_pairs[char] for char, _ in reversed(stack))
        message = f"Missing {len(stack)} closing bracket(s): {missing}"
        if auto_fix:
            return text + missing, False, f"{message} — Auto-fixed."
        else:
            return text, False, message

    return text, True, "All brackets are balanced"


def main():
    file_path = "dataset/trimmed_small_workflows_ssf_0384.txt"
    input_strings = read_input_file(file_path)

    error_count = 0
    for i, input_string in enumerate(input_strings):
        try:
            parsed_json = reverse_ssf_to_json(input_string)
            json_output = json.loads(parsed_json)
        except ValueError as e:
            [text, correct, info] = check_and_fix_brackets(parsed_json, True)
            if (correct == False):
                print(f"Error line {i + 1}: {e}")
                print(input_string)
                print(parsed_json)
                print(info)
                error_count += 1
            continue

    percent_error = round(float(error_count) / float(len(input_strings)), 4) * 100
    print(f"Total: {len(input_strings)} | Errors: {error_count} | Percent Error: {percent_error}%")


def test():
    input_text = """
    { In [ String Object Object Object ] Out [ Object ] Seq [
        { LOOP Seq [ { PROC0933 } ] Exp [ ] }
        { LOOP Seq [ ] Exp [ LNoR ] }
        { LOOP Seq [ { PROC0933 } { PROC0324 } { PROC0877 } ] Exp [ LNoR ] }
        { IF Seq [ { ELSE Seq [ { PROC0254 } ] Exp [ LTrue ] } ] }
        { IF Seq [ { ELSE Seq [ { PROC0053 } { PROC0304 } { PROC0981 } { PROC1210 } { PROC1160 } { PROC0895 } ] Exp [ LTrue ] } ] }
        { 
            IF Seq [ 
                { ELSE Seq [ { PROC0163 } ] Exp [ LTrue ] } 
                { ELSE Seq [ { PROC0513 } { PROC1137 } ] Exp [ LTrue LNoR ] } 
                { ELSE Seq [ { PROC0163 } ] Exp [ ] } 
            ] 
        }
    ] }
    """

    input_text = "{ In [ Integer Object Object Object Object ] Out [ Integer ] Seq [ { IF Seq [ { ELSE Exp [ LTrue ] Seq [  ] } ] Exp [ ] } { PROC0124 } ] }"

    input_text = "{ In [ String Object ] Out [ Boolean ] Seq [ { PROC0314 } { IF Seq [ { ELSE Exp [ LTrue ] Seq [ { PROC0124 } ] } ] Exp [ ] } { PROC0348 } { PROC0314 } { PROC0314 } { IF Seq [ { ELSE Exp [ LTrue ] Seq [ { IF Seq [ { ELSE Exp [ LTrue ] Seq [ { PROC0124 } ] } ] Exp [ ] } { PROC0080 } ] } ] Exp [ ] } { LOOP Seq [ { IF Seq [ { ELSE Exp [ LTrue ] Seq [ { PROC0124 } ] } ] Exp [ ] } { IF Seq [ { ELSE Exp [ LTrue ] Seq [ { PROC0124 } ] } ] Exp [ ] } { PROC0348 } ] Exp [ ] } { PROC0124 } { PROC0124 } ] }"

    parsed_output = reverse_ssf_to_json(input_text.strip())
    print(parsed_output)
    parsed_json = json.loads(parsed_output)
    print(json.dumps(parsed_json, indent=2))



if __name__ == "__main__":
    
    #test()
    
    main()
