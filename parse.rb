require 'pathname'
require 'json'
require 'parser/current'
require 'unparser'

def extract_steps(node, filename)
  steps = {}

  if node.nil?
    puts "Node is nil in file #{filename}"
    return steps
  end

  begin
    node.children.each do |child|
      next unless child.is_a?(Parser::AST::Node) && child.type == :block

      method_call, args, body = child.children

      if method_call.is_a?(Parser::AST::Node) && method_call.type == :send
        method_name = method_call.children[1]
        if [:Given, :When, :Then, :And].include?(method_name)
          regex_node = method_call.children[2]
          if regex_node.is_a?(Parser::AST::Node) && regex_node.type == :regexp
            regex = regex_node.children.first.children.last

            # Extract the code block without the Given/When/Then/And part
            code = Unparser.unparse(body)

            # Reconstruct the code block with do ... end if not using braces
            if child.location.begin.source == "do"
              code = "do\n#{code.strip}\nend"
            end

            steps[regex] = {
              "Code" => code,
              "File" => filename
            }
          end
        end
      end
    end
  rescue StandardError => e
    puts "Error processing node in file #{filename}: #{e.message}"
  end

  steps
end

def parser(code, file_path, result)
  buffer = Parser::Source::Buffer.new(file_path)
  buffer.source = code
  parser = Parser::CurrentRuby.new
  begin
    ast = parser.parse(buffer)
  rescue Parser::SyntaxError => e
    puts "Syntax error in file #{file_path}: #{e.message}"
    return
  rescue StandardError => e
    puts "Error parsing file #{file_path}: #{e.message}"
    return
  end

  steps = extract_steps(ast, file_path)
  result.merge!(steps)
end

def main(files_with_step_definitions, output_dir)
  result = {}

  files_with_step_definitions.each do |file_path|
    begin
      code = File.read(file_path)
    rescue Errno::ENOENT
      puts "File not found: #{file_path}"
      next
    rescue Errno::EACCES
      puts "Permission denied reading file: #{file_path}"
      next
    rescue StandardError => e
      puts "Error reading file #{file_path}: #{e.message}"
      next
    end

    parser(code, file_path, result)
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
