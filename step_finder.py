from typing import List
import os
import re

def find_step_definition_files(directory: str, file_type: str=".rb") -> List[str]:
    step_definition_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_type):
                file_path = os.path.join(root, file)
                if has_step_definitions(file_path):
                    step_definition_files.append(file_path)
    
    print("------------------------------------------------")
    print(f"Found {len(step_definition_files)} code files.")
    print("\nStep Definition Files:")
    for file_path in step_definition_files:
        print(file_path)
    print(f"\nTotal Step Definition Files: {len(step_definition_files)}")
    print("------------------------------------------------")
    return step_definition_files

def has_step_definitions(file_path: str) -> bool:
    pattern = re.compile(r'^(Given|When|Then|And)\s*\(', re.IGNORECASE)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if pattern.search(line):
                    return True
    except UnicodeDecodeError:
        print(f"Skipping file {file_path} due to UnicodeDecodeError")
    return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Find and print Ruby step definition files.')
    parser.add_argument('directory', type=str, help='Directory to search for step definition files')
    parser.add_argument('--file-type', type=str, default='.rb', help='File type to search for (default: .rb)')
    args = parser.parse_args()

    step_definition_files = find_step_definition_files(args.directory, args.file_type)