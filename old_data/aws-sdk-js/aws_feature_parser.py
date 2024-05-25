import os
import re
import json
import csv
from behave.parser import parse_file

def find_feature_files(base_dir):
    feature_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".feature"):
                print(file)
                feature_files.append(os.path.join(root, file))
    
    return feature_files

def pattern_search(step_name, step_patterns):
    for pattern, definition in step_patterns.items():
        if re.match(pattern, step_name):
            return definition["Glue Code"]
    return None

def feature_parser(feature_files, parsed_gcode_file, combined_directory, combined_data_filename, language):
    with open(parsed_gcode_file, 'r') as json_file:
        step_patterns = json.load(json_file)

    combined_json = []
    total_test_cases = 0
    for feature_file in feature_files:
        print("----------------------------------------------------")
        print("Processing file: ", feature_file)
        feature = parse_file(feature_file)

        if feature is None:
            continue

        matched_steps = []
        total_step_count = 0

        for scenario in feature.scenarios:
            total_test_cases += 1
            matched_scenario = {}
            step_num = 0
            steps = []
            # find the glue code for each step
            for step in scenario.steps:
                total_step_count += 1
                step_num += 1
                glue_code = pattern_search(step.name, step_patterns)

                if glue_code is None:
                    glue_code = pattern_search(step.name+":", step_patterns)

                matched_scenario[step.name] = glue_code
                
                if step.name in matched_scenario:
                    steps.append({
                        "step_num": step_num,
                        "step_name": step.name,
                        "glue_code": matched_scenario[step.name],
                        "language": language
                    })
                else:
                    print(f"Step number {step_num} with Step name {step.name} not matched.")
            
            matched_steps.append({
                        "feature_file": os.path.basename(feature_file),
                        "test_num": total_test_cases,
                        "test_case": scenario.name,
                        "steps": steps
                    })
            
        combined_json.extend(matched_steps)
        
        print(f"FINISHED PARSING '{feature_file}' FEATURE FILE")
        print("Feature Steps: ",total_step_count)
        print("Steps Parsed: ", len(matched_steps))
        print("Test Cases Parsed: ", len(feature.scenarios))
        print("----------------------------------------------------")
        print("\n")
    
    json_file_path = os.path.join(combined_directory, f'{combined_data_filename}.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(combined_json, json_file, indent=4)

if __name__ == "__main__":
    # feature file paths
    feature_directory = './repos/aws-sdk-js/features'
    combined_directory = "./data/aws-sdk-js"
    combined_data_filename = "aws-sdk-js_data"
    parsed_gcode_file = './data/aws-sdk-js/parsed_stepdefinitions.json'
    language = "js"

    feature_files = find_feature_files(feature_directory)

    feature_parser(feature_files, parsed_gcode_file, combined_directory, combined_data_filename, language)