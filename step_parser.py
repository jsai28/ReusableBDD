from typing import List
import subprocess
import json
from step_finder import find_step_definition_files

def parse_ruby_code(file_path):
    try:
        file_path = file_path.replace('\\', '/')
        result = subprocess.run(['ruby-parse', '--emit-json', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode != 0:
            raise Exception(f"Error running ruby-parse: {result.stderr}")
    except Exception as e:
        print(f"Error parsing Ruby code: {e}")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON output: {e}")
        return None

def step_parser(directory: str, file_type: str=".rb", output_dir="./data") -> None:
    step_definition_files = find_step_definition_files(directory, file_type)
    ruby_script = './parse.rb'

    subprocess.run(['ruby', ruby_script] + step_definition_files + [output_dir])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parse step definitions in Ruby files.')
    parser.add_argument('directory', type=str, help='Directory containing Ruby files')
    parser.add_argument('--file-type', type=str, default='.rb', help='File type of Ruby files (default: .rb)')
    parser.add_argument('--output-dir', type=str, default='./data', help='Output directory for parsed files (default: ./data)')
    args = parser.parse_args()

    step_parser(args.directory, args.file_type, args.output_dir)


