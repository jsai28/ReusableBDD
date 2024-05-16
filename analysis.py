import json
import zlib
import numpy as np
import matplotlib.pyplot as plt

data_file = './data/jekyll/jekyll_data_v2.json'
with open(data_file, 'r') as f:
	test_data = json.load(f)

def calculate_ncd(data1, data2):
    """Calculate the Normalized Compression Distance (NCD) between two strings."""
    combined_length = len(data1) + len(data2)
    compressed1 = zlib.compress(data1.encode())
    compressed2 = zlib.compress(data2.encode())
    compressed_combined = zlib.compress((data1 + data2).encode())
    return (len(compressed_combined) - min(len(compressed1), len(compressed2))) / combined_length

# Concatenate step_num and step_name for each test case
step_name_strings = []
for test_case in test_data:
    step_name_string = ""
    for step in test_case["steps"]:
        step_name_string += f"{step['step_num']}: {step['step_name']}\n"
    step_name_strings.append(step_name_string)

# Concatenate step_num and glue_code for each test case
glue_code_strings = []
for test_case in test_data:
    glue_code_string = ""
    for step in test_case["steps"]:
        glue_code_string += f"{step['step_num']}: {step['glue_code']}\n"
    glue_code_strings.append(glue_code_string)

# Calculate NCD for step_name
step_name_ncd_matrix = np.zeros((len(step_name_strings), len(step_name_strings)))
for i in range(len(step_name_strings)):
    for j in range(i+1, len(step_name_strings)):
        ncd = calculate_ncd(step_name_strings[i], step_name_strings[j])
        step_name_ncd_matrix[i, j] = ncd
        step_name_ncd_matrix[j, i] = ncd  # Since NCD is symmetric

# Calculate NCD for glue_code
glue_code_ncd_matrix = np.zeros((len(glue_code_strings), len(glue_code_strings)))
for i in range(len(glue_code_strings)):
    for j in range(i+1, len(glue_code_strings)):
        ncd = calculate_ncd(glue_code_strings[i], glue_code_strings[j])
        glue_code_ncd_matrix[i, j] = ncd
        glue_code_ncd_matrix[j, i] = ncd  # Since NCD is symmetric

# Create subplots for the heatmaps
fig, axs = plt.subplots(1, 2, figsize=(20, 8))

# Plot heatmap for step_name
axs[0].imshow(step_name_ncd_matrix, cmap='hot', interpolation='nearest')
axs[0].set_title('NCD Heatmap for Step Name')
axs[0].set_xlabel('Test Case Index')
axs[0].set_ylabel('Test Case Index')

# Plot heatmap for glue_code
axs[1].imshow(glue_code_ncd_matrix, cmap='hot', interpolation='nearest')
axs[1].set_title('NCD Heatmap for Glue Code')
axs[1].set_xlabel('Test Case Index')
axs[1].set_ylabel('Test Case Index')

plt.show()