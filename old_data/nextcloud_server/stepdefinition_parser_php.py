import re

def extract_step_definitions_and_functions(file_content):
    # Regular expression to match the PHPDoc comment with @When, followed by public function
    step_definition_pattern = re.compile(
        r'(/\*\*\s*\*\s*@When\s+[^\*]*\*/\s*public\s+function\s+\w+\s*\([^\)]*\)\s*\{[^\}]*\})',
        re.DOTALL
    )

    # Find all matches in the file content
    matches = step_definition_pattern.findall(file_content)

    # Extract step definitions and their corresponding function bodies
    step_definitions = []
    for match in matches:
        # Extract the step definition pattern
        step_pattern = re.search(r'@When\s+(.*?)\*/', match, re.DOTALL)
        if step_pattern:
            step_expression = step_pattern.group(1).strip()
            step_definitions.append((step_expression, match))

    return step_definitions

# Load the PHP file content (replace 'file_path' with the actual path to your PHP file)
file_path = './repos/server/build/integration/features/bootstrap/Auth.php'
with open(file_path, 'r') as file:
    file_content = file.read()

# Match all step definitions using a regular expression
pattern = r'/\*\*\n\s+\*\s+@(Given|When|Then)\s+(.*?)\s+\*/\n\s*public function\s+(.*?)\((.*?)\)\s*{'
matches = re.findall(pattern, file_content, re.DOTALL)

# Extract and display the regex pattern, function name, and function body for each match
for match in matches:
    annotation = match[0]
    regex = match[1]
    function_name = match[2]

    print(f"Annotation: {annotation}")
    print(f"Regex: {regex}")
    print(f"Function Name: {function_name}\n")