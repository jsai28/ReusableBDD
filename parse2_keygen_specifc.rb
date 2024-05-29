require 'pathname'
require 'json'

def extract_steps_from_file(file_path)
  steps = {}

  begin
    code = File.read(file_path)
  rescue Errno::ENOENT
    puts "File not found: #{file_path}"
    return steps
  rescue Errno::EACCES
    puts "Permission denied reading file: #{file_path}"
    return steps
  rescue StandardError => e
    puts "Error reading file #{file_path}: #{e.message}"
    return steps
  end

  # Regular expression to match step definitions
  step_definition_regex = /(Given|Then|When|And)\s*\(\s*%r!([^!]+)!\)\s*do\s*(?:\|[^|]*\|\s*)?(.*?)end/m

  code.scan(step_definition_regex).each do |match|
    step_type = match[0]
    regex_pattern = match[1].strip
    step_code = match[2].strip

    steps[regex_pattern] = {
      "Code" => step_code,
      "File" => 'resource_steps.rb'
    }
  end

  steps
end

def main(files_with_step_definitions, output_dir)
  result = {}

  files_with_step_definitions.each do |file_path|
    steps = extract_steps_from_file(file_path)
    if steps.empty?
      puts "No steps found in file: #{file_path}"
    end
    result.merge!(steps)
  end

  if result.empty?
    puts "Steps were not parsed properly / no step definitions files were passed"
  else
    begin
      # Create the output directory if it doesn't exist
      Dir.mkdir(output_dir) unless Dir.exist?(output_dir)

      # Write result to a JSON file
      output_path = File.join(output_dir, 'parsed_stepdefinitions.json')
      File.write(output_path, JSON.pretty_generate(result))
      puts "Parsed step definitions have been written to #{output_path}"
    rescue Errno::EACCES
      puts "Permission denied writing to directory: #{output_dir}"
    rescue StandardError => e
      puts "Error writing to file #{output_path}: #{e.message}"
    end
  end
end

# Ensure the script is run with the correct arguments
if ARGV.length < 2
  puts "Usage: ruby script.rb <step_definition_files> <output_directory>"
  exit 1
end

# Parse arguments
files_with_step_definitions = ARGV[0...-1] # Exclude the last argument which is the output directory
output_directory = ARGV.last

main(files_with_step_definitions, output_directory)
