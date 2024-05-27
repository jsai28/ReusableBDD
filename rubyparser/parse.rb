require 'pathname'
require 'json'
require 'parser/current'
require 'unparser'

def find_ruby_files(base_dir)
  ruby_files = []
  base_path = Pathname.new(base_dir)
  
  Dir.glob(base_path.join('**/*.rb')).each do |file_path|
    relative_path = Pathname.new(file_path).relative_path_from(base_path).to_s
    ruby_files << relative_path
  end

  ruby_files
end

def find_step_definitions(file_path)
  step_definitions = []
  
  # Check if the file is UTF-8 encoded
  if File.open(file_path, 'r:utf-8').read.encoding.to_s == 'UTF-8'
    file_content = File.read(file_path, mode: 'rb').force_encoding('UTF-8').encode('UTF-8', invalid: :replace, undef: :replace, replace: '')
  
    step_patterns = [
      /^(Given|When|Then|And)\s*\(['"]([^'"]*)['"]\)\s*do\s*\|\s*([^|]*)\s*\|/,
      /^(Given|When|Then|And)\s*\(['"]([^'"]*)['"]\)\s*do/,
      /^(Given|When|Then|And)\s*\(['"]([^'"]*)['"]\)\s*do\s*\|?\s*([^|]*)\|?/,
      /^(Given|When|Then|And)\s*\(([^)]*)\)\s*do/,
      /^(Given|When|Then|And)\s*\(([^)]*)\)\s*do\s*\|([^|]*)\|/,
    ]
  
    step_patterns.each do |pattern|
      file_content.scan(pattern).each do |match|
        step_definitions << match.map(&:strip)
      end
    end
  else
    puts "File #{file_path} is not UTF-8 encoded. Skipping..."
  end

  step_definitions
end

def extract_steps(node, filename)
  steps = {}

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

  steps
end

def parser(code, file_path, result)
  buffer = Parser::Source::Buffer.new(file_path)
  buffer.source = code
  parser = Parser::CurrentRuby.new
  ast = parser.parse(buffer)
  steps = extract_steps(ast, file_path)
  result.merge!(steps)
end

def main(base_dir, output_dir)
  ruby_files = find_ruby_files(base_dir)
  files_with_step_definitions = []
  result = {}

  ruby_files.each do |file_path|
    step_definitions = find_step_definitions(File.join(base_dir, file_path))
    if step_definitions.any?
      files_with_step_definitions << file_path
      code = File.read(File.join(base_dir, file_path))
      parser(code, file_path, result)
    end
  end

  if files_with_step_definitions.empty?
    puts "No step definitions found in any file."
  else
    puts " "
    puts "Step definitions found in the following files: "
    puts " "
    puts files_with_step_definitions.join(' ')
    puts " "
  end

  # Write result to a JSON file
  output_path = File.join(output_dir, 'parsed_stepdefinitions.json')
  File.write(output_path, JSON.pretty_generate(result))
  puts "Parsed step definitions have been written to #{output_path}"
end

# Specify the path to the repository directory
repository_directory = './repos/keygen-api'
output_directory = './data/keygen-api'

main(repository_directory, output_directory)
