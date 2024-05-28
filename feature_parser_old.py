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

def feature_parser(feature_files, parsed_definitions, combined_directory):
    """
    Build the dataset of each test case and its corresponding glue code and step definitions.

    Args:
        feature_files (list): A list of feature file paths to be parsed.
        parsed_definitions (dict): Dictionary of step patterns and their glue code.
        combined_directory (str): The directory where the combined data file will be saved.

    Returns:
        None: This function saves the combined data to a specified file and does not return anything.
    """

    combined_json = []
    total_test_cases = 0
    total_unmatched_steps = 0
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
                        "step_definition": step_definition,
                        "step_definition_file": step_definition_file
                    })
                
                if matched_scenario[step.name] is None:
                    print(f"Step number {step_num} with Step name {step.name} not matched.")
                    total_unmatched_steps += 1
            
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
    
    print("Total Test Cases: ", total_test_cases)
    json_file_path = os.path.join(combined_directory, f'{os.path.basename(combined_directory)}_parsed_steps.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(combined_json, json_file, indent=4)

if __name__ == "__main__":
    aruba_definitions = './data/aruba/aruba_stepdefinitions.json'
    cucumber_definitions = './data/cucumber_stepdefinitions.json'
    feature_directory = './repos/keygen-api/features'
    step_definition_file = './data/keygen-api/parsed_stepdefinitions.json'
    feature_files = find_feature_files(feature_directory)
    combined_directory = "./data/keygen-api"

    with open(step_definition_file) as f:
        parsed_steps_file = json.load(f)
    
    with open(aruba_definitions) as f:
        aruba_steps_file = json.load(f)
    
    with open(cucumber_definitions) as f:
        cucumber_steps_file = json.load(f)
    
    combined_steps = {**parsed_steps_file, **aruba_steps_file, **cucumber_steps_file}

    feature_parser(feature_files, combined_steps, combined_directory)
    """
    # parsing aws-sdk-js files
    step_definitions_directory = './repos/aws-sdk-js/features'
    file_ext = ".js"

    regex_str = r'\bthis\.(Given|When|Then|Before|After|And)\(([^,]+),\s*function\(([^)]*)\)\s*{([^}]*)}\s*\)'
    feature_directory = './repos/aws-sdk-js/features'

    combined_directory = "./test/aws-sdk-js"

    run_parser(step_definitions_directory, file_ext, regex_str, feature_directory, combined_directory)
    """
    """
    step_definitions_directory = './repos/jekyll/features'
    file_ext = ".rb"

    regex_str = r'(Given|When|Then|Before|After)\(%r!(.*?)!\) do(.*?)end'
    feature_directory = './repos/jekyll/features'

    combined_directory = "./test/jekyll"

    # retrieve step definitions
    step_definitions = find_step_definition_files(step_definitions_directory, file_ext)

    # parse the step definitions and create the parsed_stepdefinitions file
    parsed_steps_file = step_definition_parser(step_definitions, combined_directory, regex_str)
    """
    