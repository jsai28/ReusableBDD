import re
import json

def parse_step_definitions(glue_code_file, parsed_gcode_file):
    with open(glue_code_file, 'r') as f:
        step_definitions_content = f.read()

    step_patterns = {}
    # find certain multiline steps
    for step_content in re.split(r'#\s*\n', step_definitions_content):
        match = re.match(r'(Given|When|Then)\(%r!(.*?)!\) do\n(.*?)\nend', step_content.strip(), re.DOTALL)
        
        if match:
            step_type, step_pattern, glue_code = match.groups()
            step_patterns[step_pattern] = {"Type": step_type, "Glue Code": glue_code}

    # find the rest of the steps
    matches = re.findall(r'(Given|When|Then|And)\(%r!(.*?)!\) do \|.*?\|\s+(.*?)\s+end', step_definitions_content, re.DOTALL)
    for step_type, step_pattern, glue_code in matches:
        step_patterns[step_pattern.strip()] = {'Type': step_type, 'Glue Code': glue_code}
    
    with open(parsed_gcode_file, 'w') as json_file:
        json.dump(step_patterns, json_file, indent=4)

def parser_updated(glue_code_file, parsed_gcode_file):
    with open(glue_code_file, 'r') as f:
        step_definitions_content = f.read()

    step_definitions = re.split(r'#\s*\n', step_definitions_content)

    step_patterns = {}
    for step_definition in step_definitions:
        match = re.search(r'\(%r!(.*?)!\)', step_definition)
        if match:
            step_patterns[match.group(1).strip()] = {"Glue Code": step_definition}
        else:
            print("MATCH NOT FOUND FOR: ")
            print(step_definition)
            print("--------------------")
    
    with open(parsed_gcode_file, 'w') as json_file:
        json.dump(step_patterns, json_file, indent=4)


if __name__ == "__main__":
    glue_code_file = './repos/jekyll/features/step_definitions.rb'
    parsed_gcode_file = 'parsed_stepdefinitions2.json'

    #parse_step_definitions(glue_code_file, parsed_gcode_file)
    parser_updated(glue_code_file, parsed_gcode_file)


