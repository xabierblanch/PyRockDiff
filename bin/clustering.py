import matplotlib.pyplot as plt
from pathlib import Path
from bin.utils import loadPC, savePC, get_file_name, create_folder, _print
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import open3d as o3d
import os

def threshold_filter(threshold, e1e2_change_path):
    pc = loadPC(e1e2_change_path)
    _print(f'Filtering Point Cloud: Difference threshold: {threshold}')
    if threshold < 0:
        pc_filtered = pc[pc['m3c2_diff'] < threshold]
    if threshold > 0:
        pc_filtered = pc[pc['m3c2_diff'] > threshold]
    _print(f'Point Cloud after threshold filter: {pc_filtered.shape[0]} points')
    return pc_filtered

def dbscan_core(diff_filter, eps, min_samples):
    _print(f'Running DBSCAN algorithm for clustering the {diff_filter.shape[0]} points')
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(diff_filter[['x','y','z']])
    labels = clustering.labels_.reshape((-1, 1))
    labels_df = pd.DataFrame(labels, columns=['rockfall_label'])
    diff_cluster = pd.concat([diff_filter.reset_index(drop=True), labels_df], axis=1)
    diff_cluster = diff_cluster[diff_cluster['rockfall_label'] >= 0]
    # plt.scatter(diff_cluster[:, 0], diff_cluster[:, 2], c=diff_cluster[:, -1])
    # plt.show()
    _print(f'DBSCAN algorithm applied correctly: {diff_cluster.shape[0]} points in {diff_cluster["rockfall_label"].max()} clusters identified')
    return diff_cluster

def plot_clusters(diff_cluster, e1e2_change_path, dbscan_folder):
    project_path=Path(dbscan_folder).parent
    name = get_file_name(e1e2_change_path).split('_vs_')[0]
    point_cloud = os.path.join(project_path, '1.2_canupo', name+'__canupo.xyz')
    if os.path.exists(point_cloud):
        canupo = loadPC(point_cloud, array=True)
        data_sorted = canupo[canupo[:, 0].argsort()]
        subsampled_data = data_sorted[::50]
        labels = subsampled_data[:, 3]
        colors = np.where(labels == 1, 'lightgrey', 'green')
        plt.scatter(subsampled_data[:, 0], subsampled_data[:, 2], color=colors, s=0.1)

    plt.scatter(diff_cluster['x'], diff_cluster['z'], s=1)
    grouped = diff_cluster.groupby('rockfall_label').agg({'x': 'mean', 'z': 'mean'}).reset_index()
    for index, row in grouped.iterrows():
        plt.text(int(row['x']+0.5), int(row['z']+0.5), f"{int(row['rockfall_label'])}", fontsize=12, ha='center', va='center')
    plt.show()


def dbscan(dbscan_folder, e1e2_change_path, parameters):
    pc_filtered = threshold_filter(parameters['diff_threshold'], e1e2_change_path)
    diff_cluster = dbscan_core(pc_filtered, parameters['eps_rockfalls'], parameters['min_samples_rockfalls'])
    file_name = get_file_name(e1e2_change_path)
    dbscan_path = savePC(os.path.join(dbscan_folder, file_name + '__dbscan.xyz'), diff_cluster)
    plot_clusters(diff_cluster, e1e2_change_path, dbscan_folder)

    return dbscan_path