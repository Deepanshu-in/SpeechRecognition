import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial import Voronoi, voronoi_plot_2d
import seaborn as sns

# Sample data loading function
def load_data():
    # Replace with actual data loading logic
    data = pd.DataFrame({
        'player': ['Player1', 'Player2', 'Player3', 'Player4'],
        'runs': [500, 600, 550, 700],
        'wickets': [20, 25, 15, 30],
        'fielding': [10, 15, 12, 18]
    })
    return data

# Preprocess data
def preprocess_data(data):
    # Handle outliers and normalize data
    scaler = StandardScaler()
    data[['runs', 'wickets', 'fielding']] = scaler.fit_transform(data[['runs', 'wickets', 'fielding']])
    return data

# Determine optimal number of clusters
def find_optimal_clusters(data):
    silhouette_scores = []
    for n_clusters in range(2, 10):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(data)
        score = silhouette_score(data, kmeans.labels_)
        silhouette_scores.append(score)
    optimal_clusters = np.argmax(silhouette_scores) + 2
    return optimal_clusters

# Perform KMeans clustering
def perform_clustering(data, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    data['cluster'] = kmeans.fit_predict(data[['runs', 'wickets', 'fielding']])
    return data, kmeans.cluster_centers_

# Visualize clusters
def visualize_clusters(data, centroids):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=data, x='runs', y='wickets', hue='cluster', palette='viridis')
    plt.scatter(centroids[:, 0], centroids[:, 1], s=300, c='red', marker='X')
    plt.title('Player Clusters with Centroids')
    plt.show()

# Voronoi diagram for fielding positions
def plot_voronoi(fielders_positions):
    vor = Voronoi(fielders_positions)
    fig, ax = plt.subplots()
    voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors='orange', line_width=2)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    plt.title('Voronoi Diagram for Fielding Positions')
    plt.show()

# Analyze clusters
def analyze_clusters(data):
    cluster_analysis = data.groupby('cluster').mean()
    print("Cluster Analysis:\n", cluster_analysis)
    return cluster_analysis

# Identify top players in each cluster
def identify_top_players(data):
    data['composite_score'] = data['runs'] + data['wickets'] + data['fielding']
    top_players = data.loc[data.groupby('cluster')['composite_score'].idxmax()]
    print("Top Players in Each Cluster:\n", top_players)
    return top_players

# Main function to execute the workflow
def main():
    data = load_data()
    data = preprocess_data(data)
    optimal_clusters = find_optimal_clusters(data[['runs', 'wickets', 'fielding']])
    data, centroids = perform_clustering(data, optimal_clusters)
    visualize_clusters(data, centroids)
    fielders_positions = np.random.rand(10, 2) * 100  # Random fielders positions for demonstration
    plot_voronoi(fielders_positions)
    analyze_clusters(data)
    identify_top_players(data)

if __name__ == "__main__":
    main()