import os
import re
import json
import pyparsing as pp

def find_js_files_in_step_definitions(base_dir):
    step_definitions = []
    for root, dirs, files in os.walk(base_dir):
        for dir_name in dirs:
            if dir_name == "step_definitions":
                step_definitions_path = os.path.join(root, dir_name)
                for file in os.listdir(step_definitions_path):
                    if file.endswith(".js"):
                        print(file)
                        step_definitions.append(os.path.join(step_definitions_path, file))

                dirs.remove(dir_name)
    
    return step_definitions

def glue_code_parser(step_files, parsed_gcode_file):
    step_patterns = {}
    for glue_code_file in step_files:
        with open(glue_code_file, 'r') as f:
            step_definitions_content = f.read()
        
        pattern = re.compile(r'\bthis\.(Given|When|Then|Before|After|And)\(([^,]+),\s*function\(([^)]*)\)\s*{([^}]*)}\s*\)')
        matches = pattern.findall(step_definitions_content.strip())

        for match in matches:
            step_type = match[0]
            regex = match[1].strip()
            params = match[2].strip()
            code = match[3].strip()
            
            step_patterns[regex[1:-1]] = {"Glue Code": code, "Glue Code File": os.path.basename(glue_code_file)}
    
    with open(parsed_gcode_file, 'w') as json_file:
        json.dump(step_patterns, json_file, indent=4)

def function_finder(step_files):
    functions = []
    for step_file in step_files:
        with open(step_file, 'r') as f:
            step_definitions_content = f.read()
        
        pattern = r'this\.(?:Given|Then|When|And)+\([^)]*\)\s*{[^}]*}'
        found_functions = re.findall(pattern, step_definitions_content.strip(), re.DOTALL)

        for fn in found_functions:
            print(fn)
            print("\n --- \n")

        functions.extend(found_functions)
    
    return functions

def function_parser(functions):
    step_patterns = {}
    regex_pattern = re.compile(r'this\.(?:Given|Then|When)\(/(.+?)/')
    type_pattern = re.compile(r'this\.(Given|Then|When)')

    for function in functions:
        match = regex_pattern.search(function)
        if match:
            regex = match.group(1)
            print(f"Regex: {regex}")

            
        else:
            not_found_match = type_pattern.search(function)
            if not_found_match:
                print("No match found for: ", function)
                print("\n --- \n")

def extract_functions(js_code):
    # Define the basic syntax elements
    identifier = pp.Word(pp.alphas, pp.alphanums + "_$").setName("identifier")
    lparen = pp.Literal("(").suppress()
    rparen = pp.Literal(")").suppress()
    lbrace = pp.Literal("{").suppress()
    rbrace = pp.Literal("}").suppress()
    colon = pp.Literal(":").suppress()
    
    # Define the nested braces using nestedExpr
    nested_braces = pp.nestedExpr("{", "}", ignoreExpr=pp.quotedString | pp.cStyleComment).setParseAction(pp.originalTextFor)

    # Define the function signature
    function_signature = (
        pp.Literal("this.")
        + pp.oneOf("Given Then When And")
        + lparen
        + pp.SkipTo(rparen)("params")
        + rparen
        + lbrace
        + nested_braces("body")
        + rbrace
    )
    
    # Scan for all matches in the input string
    functions = []
    for match, start, end in function_signature.scanString(js_code):
        function_name = match[1]
        function_params = match.params
        function_body = match.body
        functions.append({
            "name": function_name,
            "params": function_params,
            "body": function_body
        })
    
    return functions

if __name__ == "__main__":
    features_folder = "./repos/aws-sdk-js/features"
    step_definition_files = find_js_files_in_step_definitions(features_folder)
    parsed_gcode_file = "./data/aws-sdk-js/parsed_stepdefinitions.json"
    
    #glue_code_parser(step_definition_files, parsed_gcode_file)
    #functions = function_finder(step_definition_files)
    #function_parser(functions)

    with open('./repos/aws-sdk-js/features/sns/step_definitions/sns.js', 'r') as f:
        step_definitions_content = f.read()
    
    functions = extract_functions(step_definitions_content)

    for function in functions:
        print(function)
        print("\n --- \n")
