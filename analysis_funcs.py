import json
import zlib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def kmeans_clustering(matrix, num_clusters, labels):
    """Perform K-Means clustering and plot the results."""
    # Perform K-Means clustering on the distance matrix
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    # Reshape the matrix to a 2D array suitable for K-Means (flatten the upper triangle)
    upper_triangle_indices = np.triu_indices_from(matrix, k=1)
    matrix_flattened = matrix[upper_triangle_indices]
    matrix_for_clustering = matrix_flattened.reshape(-1, 1)
    kmeans.fit(matrix_for_clustering)
    clusters = kmeans.labels_
    
    # Reshape cluster labels back to the original matrix form
    clustered_matrix = np.zeros_like(matrix)
    for idx, (i, j) in enumerate(zip(*upper_triangle_indices)):
        clustered_matrix[i, j] = clusters[idx]
        clustered_matrix[j, i] = clusters[idx]  # Since the distance matrix is symmetric
    
    # Plot the clustered heatmap
    plt.figure(figsize=(10, 7))
    sns.heatmap(clustered_matrix, annot=True, cmap='viridis', xticklabels=labels, yticklabels=labels)
    plt.title(f"K-Means Clustering with {num_clusters} Clusters")
    plt.xlabel('Test Case Index')
    plt.ylabel('Test Case Index')
    plt.show()
    
    return clusters

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

def stringify_test_titles(test_data):
    """Retrieve the scenario titles and put them in an array"""
    test_titles = []
    test_nums = []
    for test in test_data:
        test_nums.append(test["test_num"])
        test_titles.append(test["test_case"])
    return test_nums, test_titles

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

def plot_heatmaps(step_matrix, glue_matrix, title_matrix, type):
    """Plot similarity matrix using heatmaps"""
    fig, axs = plt.subplots(1, 3, figsize=(20, 8))

    # Plot heatmap for step_name
    im1 = axs[0].imshow(step_matrix, cmap='hot', interpolation='nearest')
    axs[0].set_title(f'{type} Heatmap for Step Name')
    axs[0].set_xlabel('Test Case Index')
    axs[0].set_ylabel('Test Case Index')
    fig.colorbar(im1, ax=axs[0])

    # Plot heatmap for glue_code
    im2 = axs[1].imshow(glue_matrix, cmap='hot', interpolation='nearest')
    axs[1].set_title(f'{type} Heatmap for Glue Code')
    axs[1].set_xlabel('Test Case Index')
    axs[1].set_ylabel('Test Case Index')
    fig.colorbar(im2, ax=axs[1])

    # Plot heatmap for titles
    im2 = axs[2].imshow(title_matrix, cmap='hot', interpolation='nearest')
    axs[2].set_title(f'{type} Heatmap for Titles')
    axs[2].set_xlabel('Test Case Index')
    axs[2].set_ylabel('Test Case Index')
    fig.colorbar(im2, ax=axs[2])

    plt.show()

if __name__ == "__main__":
    data_file = './data/jekyll/jekyll_parsed_steps.json'
    with open(data_file, 'r') as f:
        test_data = json.load(f)

    test_step_strings, test_glue_strings = stringify_test_cases(test_data, 'step_name'), stringify_test_cases(test_data, 'step_definition')
    test_titles = stringify_test_titles(test_data)
    
    # calculate and plot NCD
    step_ncd_matrix, glue_ncd_matrix, title_ncd_matrix = calculate_pairwise_ncd(test_step_strings), calculate_pairwise_ncd(test_glue_strings), calculate_pairwise_ncd(test_titles)
    plot_heatmaps(step_ncd_matrix, glue_ncd_matrix, title_ncd_matrix, "NCD")

    # calculate and plot cosine
    step_cosine_matrix, glue_cosine_matrix, title_cosine_matrix = calculate_cosine_similarity(test_step_strings), calculate_cosine_similarity(test_glue_strings), calculate_cosine_similarity(test_titles)
    plot_heatmaps(step_cosine_matrix, glue_cosine_matrix, title_cosine_matrix, "Cosine")

    # calculate euclidean distances
    step_euclidean_matrix, glue_euclidean_matrix, title_euclidean_matrix = calculate_euclidean_distance(test_step_strings), calculate_euclidean_distance(test_glue_strings), calculate_euclidean_distance(test_titles)
    plot_heatmaps(step_euclidean_matrix, glue_euclidean_matrix,title_euclidean_matrix, "Euclidean")

    # calculate manhattan distances
    step_manhattan_matrix, glue_manhattan_matrix, title_manhattan_matrix = calculate_manhattan_distance(test_step_strings), calculate_manhattan_distance(test_glue_strings), calculate_manhattan_distance(test_titles)
    plot_heatmaps(step_manhattan_matrix, glue_manhattan_matrix,title_manhattan_matrix, "Manhattan")
