import os
import re
import json
from behave.parser import parse_file

def find_feature_files(base_dir):
    """
    Given the base directory, find all feature files.

    Args:
        base_dir (str): The base directory where the search for feature files will be conducted.

    Returns:
        list: A list of paths to the feature files found in the base directory.
    """
    feature_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".feature"):
                print(file)
                feature_files.append(os.path.join(root, file))
    
    return feature_files

def pattern_search(step_name, step_patterns):
    """
    Given a feature step, search the parsed definitions for the glue code.

    Args:
        step_name (str): The name of the step to search for.
        step_patterns (dict): A dictionary where keys are regex patterns and values are dictionaries 
                              containing step definitions, including the "Glue Code".

    Returns:
        dict or None: The glue code corresponding to the step_name if a match is found, otherwise None.
    """
    for pattern, definition in step_patterns.items():
        if re.match(pattern, step_name):
            return definition
    return None

def replace_inputs_with_blank_quotes(step_name):
    # This regex matches any text within double quotes
    pattern = r'"[^"]*"'
    
    # Replace matched text with ""
    modified_text = re.sub(pattern, '""', step_name)
    
    return modified_text

def feature_parser(base_dir, parsed_definitions, combined_directory='./data'):
    """
    Build the dataset of each test case and its corresponding glue code and step definitions.

    Args:
        base_dir (str): The base directory where the search for feature files will be conducted.
        parsed_definitions (dict): Dictionary of step patterns and their glue code.
        combined_directory (str): The directory where the combined data file will be saved.

    Returns:
        None: This function saves the combined data to a specified file and does not return anything.
    """
    feature_files = find_feature_files(base_dir)

    combined_json = []
    total_test_cases = 0
    total_unmatched_steps = 0
    total_step_count = 0
    for feature_file in feature_files:
        print("----------------------------------------------------")
        print("Processing file: ", feature_file)
        feature = parse_file(feature_file)

        if feature is None:
            continue

        matched_steps = []
        step_count = 0

        for scenario in feature.scenarios:
            total_test_cases += 1
            matched_scenario = {}
            step_num = 0
            steps = []
            # find the glue code for each step
            for step in scenario.steps:
                total_step_count += 1
                step_count += 1
                step_num += 1
                definition = pattern_search(step.name, parsed_definitions)

                if definition is None:
                    definition = pattern_search(step.name+":", parsed_definitions)

                matched_scenario[step.name] = definition
                
                if step.name in matched_scenario:
                    step_definition = None if matched_scenario[step.name] is None else matched_scenario[step.name]['Code']
                    step_definition_file = None if matched_scenario[step.name] is None else matched_scenario[step.name]['File']
                    steps.append({
                        "step_num": step_num,
                        "step_name": step.name,
                        "step_name_cleaned": replace_inputs_with_blank_quotes(step.name),
                        "step_definition": step_definition,
                        "step_definition_file": step_definition_file
                    })

                if matched_scenario[step.name] is None:
                    print(f"Step number {step_num} with Step name {step.name} not matched.")
                    total_unmatched_steps += 1
            
            if not steps:
                continue
            
            matched_steps.append({
                        "feature_file": os.path.basename(feature_file),
                        "test_num": total_test_cases,
                        "test_case": scenario.name,
                        "steps": steps
                    })
            
        combined_json.extend(matched_steps)
        
        print(f"FINISHED PARSING '{feature_file}' FEATURE FILE")
        print("Feature Steps: ",step_count)
        print("Steps Parsed: ", len(matched_steps))
        print("Test Cases Parsed: ", len(feature.scenarios))
        print("----------------------------------------------------")
        print("\n")
    
    print("Total Test Cases: ", total_test_cases)
    print("Total Steps: ", total_step_count)
    print("Total Unmatched: ", total_unmatched_steps)
    json_file_path = os.path.join(combined_directory, f'{os.path.basename(combined_directory)}_parsed_steps.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(combined_json, json_file, indent=4)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse feature files and step definitions.")
    parser.add_argument("base_dir", help="The base directory to search for feature files.")
    parser.add_argument("step_definition_file", help="The JSON file with parsed step definitions.")
    parser.add_argument("--aruba_definitions", default="./data/aruba/aruba_stepdefinitions.json", help="The JSON file with Aruba step definitions.")
    parser.add_argument("--cucumber_definitions", default="./data/cucumber-ruby/cucumber_stepdefinitions.json", help="The JSON file with Cucumber step definitions.")
    parser.add_argument("--output_dir", default="./data", help="The directory to save the combined data file.")

    args = parser.parse_args()

    with open(args.step_definition_file) as f:
        parsed_steps_file = json.load(f)
    
    with open(args.aruba_definitions) as f:
        aruba_steps_file = json.load(f)
    
    with open(args.cucumber_definitions) as f:
        cucumber_steps_file = json.load(f)
    
    combined_steps = {**parsed_steps_file, **aruba_steps_file, **cucumber_steps_file}

    feature_parser(args.base_dir, combined_steps, args.output_dir)