import os
import re
import json

def find_js_files_in_step_definitions(base_dir):
    step_definitions = []
    for root, dirs, files in os.walk(base_dir):
        for dir_name in dirs:
            if dir_name == "step_definitions":
                step_definitions_path = os.path.join(root, dir_name)
                for file in os.listdir(step_definitions_path):
                    if file.endswith(".js"):
                        step_definitions.append(os.path.join(step_definitions_path, file))

                dirs.remove(dir_name)
    
    return step_definitions

def glue_code_parser(step_files, parsed_gcode_file):
    step_patterns = {}
    for glue_code_file in step_files:
        with open(glue_code_file, 'r') as f:
            step_definitions_content = f.read()
        
        pattern = re.compile(r'\bthis\.(Given|When|Then|Before|After|And)\(([^,]+),\s*function\(([^)]*)\)\s*{([^}]*)}\s*\)')
        matches = pattern.findall(step_definitions_content)

        for match in matches:
            step_type = match[0]
            regex = match[1].strip()
            params = match[2].strip()
            code = match[3].strip()
            
            step_patterns[regex[1:-1]] = {"Glue Code": code}
    
    with open(parsed_gcode_file, 'w') as json_file:
        json.dump(step_patterns, json_file, indent=4)

if __name__ == "__main__":
    features_folder = "./repos/aws-sdk-js/features"
    step_definition_files = find_js_files_in_step_definitions(features_folder)
    parsed_gcode_file = "./data/aws-sdk-js/parsed_stepdefinitions.json"
    
    glue_code_parser(step_definition_files, parsed_gcode_file)
