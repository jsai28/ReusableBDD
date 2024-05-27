from typing import List
import subprocess
import json

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

ruby_ast = parse_ruby_code('./repos/cucumber-ruby/features/lib/step_definitions/command_line_steps.rb')

""" if ruby_ast:
    with open('ruby_ast_cucumber.json', 'w') as f:
        json.dump(ruby_ast, f, indent=2)

print("AST saved to 'ruby_ast_cucumber.json'") """

""" # inputs
directory = "./repos/vagrant-exec"
file_type = ".rb"


step_definition_files = find_step_definition_files(directory, file_type) """


