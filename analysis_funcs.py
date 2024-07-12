import json
import collections
import zlib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import f1_score, precision_score, recall_score

def run_analysis(data_file):
    """main function to run the analysis"""
    # Load in data
    with open(data_file, 'r') as f:
        test_data = json.load(f)
    
    # Convert JSON steps into strings
    step_definition_strings = stringify_test_cases(test_data, "step_definition")
    step_name_strings = stringify_test_cases(test_data, "step_name")
    scenario_nums, scenario_title_strings = stringify_test_titles(test_data)

    # Calculate matrices for each metric
    matrices = {
        "Step Name NCD": calculate_pairwise_ncd(step_name_strings),
        "Step Definition NCD": calculate_pairwise_ncd(step_definition_strings),
        "Scenario Title NCD": calculate_pairwise_ncd(scenario_title_strings),
        "Step Name Cosine": calculate_cosine_similarity(step_name_strings),
        "Step Definition Cosine": calculate_cosine_similarity(step_definition_strings),
        "Scenario Title Cosine": calculate_cosine_similarity(scenario_title_strings),
        "Step Name Euclidean": calculate_euclidean_distance(step_name_strings),
        "Step Definition Euclidean": calculate_euclidean_distance(step_definition_strings),
        "Scenario Title Euclidean": calculate_euclidean_distance(scenario_title_strings),
        "Step Name Manhattan": calculate_manhattan_distance(step_name_strings),
        "Step Definition Manhattan": calculate_manhattan_distance(step_definition_strings),
        "Scenario Title Manhattan": calculate_manhattan_distance(scenario_title_strings)
    }

    # Determine number of clusters
    num_clusters = len(set([test['feature_file'] for test in test_data]))
    true_cluster_labels = true_clusters(test_data)

    # Process each matrix, plot data and list metrics
    metrics = {}
    for matrix_name, matrix in matrices.items():
        aligned_clusters, precision, mean_avg_precision, mean_reciprocal_ranks = plot_and_cluster(
            matrix, matrix_name, num_clusters, scenario_title_strings, true_cluster_labels
        )
        metrics[matrix_name] = (aligned_clusters, precision, mean_avg_precision, mean_reciprocal_ranks)

def plot_and_cluster(matrix, matrix_name, num_clusters, scenario_titles, true_clusters):
    """
    Plot heatmap, perform k-means clustering, and compute similarity metrics.
    """
    # Plot heatmap
    plot_individual_heatmap(matrix, title=f"{matrix_name} Heatmap")

    # Perform k-means clustering
    predicted_clusters = kmeans_clustering(matrix, num_clusters, scenario_titles)

    # Calculate similarity metrics
    aligned_clusters, precision, mean_avg_precision, mean_reciprocal_ranks = cluster_similarity(true_clusters, predicted_clusters)

    # Print metrics
    print(f"{matrix_name} Metrics:")
    print(f"  Precision: {precision:.4f}")
    print(f"  Mean Average Precision: {mean_avg_precision:.4f}")
    print(f"  Mean Reciprocal Ranks: {mean_reciprocal_ranks:.4f}")
    print()

    return aligned_clusters, precision, mean_avg_precision, mean_reciprocal_ranks

def cluster_similarity(true_clusters, predicted_clusters):
    true_keys = list(true_clusters.keys())
    pred_keys = list(predicted_clusters.keys())
    
    overlap_matrix = np.zeros((len(true_keys), len(pred_keys)))
    
    for i, true_key in enumerate(true_keys):
        true_values = set(true_clusters[true_key])
        for j, pred_key in enumerate(pred_keys):
            pred_values = set(predicted_clusters[pred_key])
            overlap = true_values & pred_values
            overlap_matrix[i, j] = len(overlap)
    
    cost_matrix = -overlap_matrix
    
    # Apply the Hungarian algorithm to find the optimal assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    i = 0
    total_correct = 0
    total_scenarios = 0
    average_precisions = []
    reciprocal_ranks = []
    for true_key, true_labels in true_clusters.items():
        cur_correct = 0
        pred_cluster_index = col_ind[i]
        pred_labels = set(predicted_clusters[pred_cluster_index])

        for label in true_labels:
            total_scenarios += 1
            if label in pred_labels:
                total_correct += 1
                cur_correct += 1
            
            for pred_key, pred_labels in predicted_clusters.items():
                if label in pred_labels:
                    reciprocal_ranks.append(1/(pred_key+1))

        average_precisions.append(cur_correct/len(true_labels))

    
    precision = total_correct/total_scenarios
    mean_average_precision = np.mean(average_precisions)
    matches = [(true_keys[i], pred_keys[j]) for i, j in zip(row_ind, col_ind)] 
    mean_reciprocal_ranks = np.mean(reciprocal_ranks)

    return matches, precision, mean_average_precision, mean_reciprocal_ranks

def kmeans_clustering(matrix, num_clusters, labels):
    """Perform K-Means clustering and return the clusters."""
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(matrix)
    cluster_labels = kmeans.labels_
    
    clusters = {}
    for idx, label in enumerate(cluster_labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(labels[idx])
    
    sorted_clusters = dict(sorted(clusters.items()))
    return sorted_clusters

def list_clusters(clusters):
    """Print each cluster and its corresponding test cases."""
    for cluster, test_cases in clusters.items():
        print(f"\nCluster {cluster}:")
        for test_case in test_cases:
            print(f"  - {test_case}")

def true_clusters(test_data):
    clusters = {}
    for test in test_data:
        feature_file = test["feature_file"]
        test_case = test["test_case"]
        if feature_file not in clusters:
            clusters[feature_file] = []
            
        clusters[feature_file].append(test_case)
    
    return clusters

def calculate_ncd(data1, data2):
    if not data1 or not data2:
        raise ValueError("Input data strings must not be empty.")
    
    compressed1 = zlib.compress(data1.encode())
    compressed2 = zlib.compress(data2.encode())
    compressed_combined = zlib.compress((data1 + data2).encode())
    
    len_compressed1 = len(compressed1)
    len_compressed2 = len(compressed2)
    combined_length = len_compressed1 + len_compressed2
    
    if combined_length == 0:
        raise ValueError("Combined length of compressed data is zero, cannot calculate NCD.")
    
    return (len(compressed_combined) - min(len_compressed1, len_compressed2)) / combined_length

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
    num_strings = len(test_strings)
    ncd_matrix = np.zeros((num_strings, num_strings))
    
    for i in range(num_strings):
        for j in range(i + 1, num_strings):
            try:
                ncd = calculate_ncd(test_strings[i], test_strings[j])
                ncd_matrix[i, j] = ncd
                ncd_matrix[j, i] = ncd  # Since NCD is symmetric
            except ValueError as e:
                print(f"Error calculating NCD for pair ({i}, {j}): {e}")
                ncd_matrix[i, j] = float('inf')
                ncd_matrix[j, i] = float('inf')
    
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

def plot_individual_heatmap(matrix, title):
    """Plot a single similarity matrix using a heatmap."""
    plt.figure(figsize=(8, 8))
    plt.imshow(matrix, cmap='hot', interpolation='nearest')
    plt.title(title)
    plt.xlabel('Test Case Index')
    plt.ylabel('Test Case Index')
    plt.colorbar()
    plt.show()

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
    axs[1].set_title(f'{type} Heatmap for Step Definitions')
    axs[1].set_xlabel('Test Case Index')
    axs[1].set_ylabel('Test Case Index')
    fig.colorbar(im2, ax=axs[1])

    # Plot heatmap for titles
    im2 = axs[2].imshow(title_matrix, cmap='hot', interpolation='nearest')
    axs[2].set_title(f'{type} Heatmap for Scenarios')
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
