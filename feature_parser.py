import os
import re
import json
import csv
from behave.parser import parse_file

def feature_parser(parsed_gcode_file, feature, write_directory, glue_code_file):
    with open(parsed_gcode_file, 'r') as json_file:
        step_patterns = json.load(json_file)

    def pattern_search(step_name):
        for pattern, definition in step_patterns.items():
            if re.match(pattern, step_name):
                return definition["Glue Code"]
        return None

    matched_steps = []
    total_step_count = 0
    for scenario in feature.scenarios:
        matched_scenario = {}
        step_num = 0
        steps = []
        # find the glue code for each step
        for step in scenario.steps:
            total_step_count += 1
            step_num += 1
            glue_code = pattern_search(step.name)

            if glue_code is None:
                glue_code = pattern_search(step.name+":")

            matched_scenario[step.name] = glue_code
            
            if step.name in matched_scenario:
                steps.append({
                    "step_num": step_num,
                    "step_name": step.name,
                    "glue_code": matched_scenario[step.name],
                    "glue_code_file": os.path.basename(glue_code_file),
                    "language": language
                })
            else:
                print(f"Step number {step_num} with Step name {step.name} not matched.")
        
        matched_steps.append({
                    "feature_file": os.path.basename(feature_file),
                    "test_case": scenario.name,
                    "steps": steps
                })

    feature_name = os.path.splitext(os.path.basename(feature_file))[0]
    #file_path = os.path.join(write_directory, f'{feature_name}_feature.json')
    #with open(file_path, 'w') as json_file:
    #    json.dump(matched_steps, json_file, indent=4)
    
    print(f"FINISHED PARSING '{feature_name}' FEATURE FILE")
    print("Feature Steps: ",total_step_count)
    print("Steps Parsed: ", len(matched_steps))
    print("Test Cases Parsed: ", len(feature.scenarios))
    print("----------------------------------------------------")
    print("\n")

    return matched_steps, total_step_count, len(matched_steps), len(feature.scenarios)

def json_to_csv(data, csv_file_path):
    fieldnames = ['feature_file', 'test_case', 'steps']
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each JSON object as a row in the CSV file
        for item in data:
            writer.writerow(item)

    print(f"CSV file written to {csv_file_path}")

if __name__ == "__main__":
    # feature file paths
    feature_directory = './repos/jekyll/features'
    combined_directory = "./data/jekyll"
    combined_data_filename = "jekyll_data_v2"
    write_directory = "./data/jekyll/features"
    glue_code_file = './repos/jekyll/features/step_definitions.rb'
    parsed_gcode_file = 'parsed_stepdefinitions2.json'
    language = "ruby"

    combined_json = []
    total_step_count = 0
    total_matched_steps = 0
    total_test_cases = 0
    for filename in os.listdir(feature_directory):
        if filename.endswith(".feature"):
            feature_file = os.path.join(feature_directory, filename)
            print("----------------------------------------------------")
            print("Processing file: ", feature_file)
            feature = parse_file(feature_file)

            # run feature parser
            matched_steps, step_count, num_matched_steps, test_cases = feature_parser(parsed_gcode_file, feature, write_directory, glue_code_file)
            combined_json.extend(matched_steps)
            total_step_count += step_count
            total_matched_steps += num_matched_steps
            total_test_cases += test_cases
    
    print("----------FINISHED-------------")
    print("Total Step Count: ", total_step_count)
    print("Total Matched Steps: ", total_matched_steps)
    print("Total Test Cases: ", total_test_cases)
    print("-------------------------------")

    json_file_path = os.path.join(combined_directory, f'{combined_data_filename}.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(combined_json, json_file, indent=4)
    
    csv_file_path = os.path.join(combined_directory, f'{combined_data_filename}.csv')
    json_to_csv(combined_json, csv_file_path)
    

    







