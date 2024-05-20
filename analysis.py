import json
import zlib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def calculate_ncd(data1, data2):
    """Calculate the Normalized Compression Distance (NCD) between two strings."""
    combined_length = len(data1) + len(data2)
    compressed1 = zlib.compress(data1.encode())
    compressed2 = zlib.compress(data2.encode())
    compressed_combined = zlib.compress((data1 + data2).encode())
    return (len(compressed_combined) - min(len(compressed1), len(compressed2))) / combined_length

def stringify_test_cases(test_data, data_key):
    """Convert the steps and glue code into strings"""
    test_strings = []
    for test_case in test_data:
        step_name_string = ""
        for step in test_case["steps"]:
            step_name_string += f"{step['step_num']}: {step[data_key]}\n"
        test_strings.append(step_name_string)
    
    return test_strings

def calculate_pairwise_ncd(test_strings):
    ncd_matrix = np.zeros((len(test_strings), len(test_strings)))
    for i in range(len(test_strings)):
        for j in range(i+1, len(test_strings)):
            ncd = calculate_ncd(test_strings[i], test_strings[j])
            ncd_matrix[i, j] = ncd
            ncd_matrix[j, i] = ncd  # Since NCD is symmetric
    
    return ncd_matrix

def create_tfidf_matrix(test_case_strings):
    """Create the TF-IDF matrix for the given test cases (as strings)."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(test_case_strings)

    return tfidf_matrix

def calculate_cosine_similarity(test_case_strings):
    """Calculate cosine similarity between test cases."""
    tfidf_matrix = create_tfidf_matrix(test_case_strings)

    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return similarity_matrix

def calculate_euclidean_distance(test_case_strings):
    """Calculate the Euclidean distance between test cases."""
    tfidf_matrix = create_tfidf_matrix(test_case_strings).toarray()
    num_test_cases = tfidf_matrix.shape[0]
    euclidean_distances = np.zeros((num_test_cases, num_test_cases))
    for i in range(num_test_cases):
        for j in range(i+1, num_test_cases):
            euclidean_distances[i, j] = np.linalg.norm(tfidf_matrix[i] - tfidf_matrix[j])
            euclidean_distances[j, i] = euclidean_distances[i, j]  # Since the distance is symmetric
    return euclidean_distances

def calculate_manhattan_distance(test_case_strings):
    """Calculate the Manhattan distance between test cases."""
    tfidf_matrix = create_tfidf_matrix(test_case_strings).toarray()
    num_test_cases = tfidf_matrix.shape[0]
    manhattan_distances = np.zeros((num_test_cases, num_test_cases))
    for i in range(num_test_cases):
        for j in range(i+1, num_test_cases):
            manhattan_distances[i, j] = np.sum(np.abs(tfidf_matrix[i] - tfidf_matrix[j]))
            manhattan_distances[j, i] = manhattan_distances[i, j]  # Since the distance is symmetric
    return manhattan_distances

def plot_heatmaps(step_matrix1, glue_matrix2, type):
    """Plot similarity matrix using heatmaps"""
    fig, axs = plt.subplots(1, 2, figsize=(20, 8))

    # Plot heatmap for step_name
    im1 = axs[0].imshow(step_matrix1, cmap='hot', interpolation='nearest')
    axs[0].set_title(f'{type} Heatmap for Step Name')
    axs[0].set_xlabel('Test Case Index')
    axs[0].set_ylabel('Test Case Index')
    fig.colorbar(im1, ax=axs[0])

    # Plot heatmap for glue_code
    im2 = axs[1].imshow(glue_matrix2, cmap='hot', interpolation='nearest')
    axs[1].set_title(f'{type} Heatmap for Glue Code')
    axs[1].set_xlabel('Test Case Index')
    axs[1].set_ylabel('Test Case Index')
    fig.colorbar(im2, ax=axs[1])

    plt.show()

if __name__ == "__main__":
    data_file = './data/jekyll/jekyll_data_v2.json'
    with open(data_file, 'r') as f:
        test_data = json.load(f)

    test_step_strings, test_glue_strings = stringify_test_cases(test_data, 'step_name'), stringify_test_cases(test_data, 'glue_code')
    
    # calculate and plot NCD
    step_ncd_matrix, glue_ncd_matrix = calculate_pairwise_ncd(test_step_strings), calculate_pairwise_ncd(test_glue_strings)
    plot_heatmaps(step_ncd_matrix, glue_ncd_matrix, "NCD")

    # calculate and plot cosine
    step_cosine_matrix, glue_cosine_matrix = calculate_cosine_similarity(test_step_strings), calculate_cosine_similarity(test_glue_strings)
    plot_heatmaps(step_cosine_matrix, glue_cosine_matrix, "Cosine")

    # calculate euclidean distances
    step_euclidean_matrix, glue_euclidean_matrix = calculate_euclidean_distance(test_step_strings), calculate_euclidean_distance(test_glue_strings)
    plot_heatmaps(step_euclidean_matrix, glue_euclidean_matrix, "Euclidean")

    # calculate manhattan distances
    step_manhattan_matrix, glue_manhattan_matrix = calculate_manhattan_distance(test_step_strings), calculate_manhattan_distance(test_glue_strings)
    plot_heatmaps(step_manhattan_matrix, glue_manhattan_matrix, "Manhattan")
