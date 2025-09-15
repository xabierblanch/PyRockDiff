import matplotlib.pyplot as plt
from pathlib import Path
from bin.utils import loadPC, savePC, get_file_name, create_folder, _print, auto_param
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import open3d as o3d
import os

def dbscan_core(e1e2_change_path, eps, min_samples):
    diff_filter = loadPC(e1e2_change_path)
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

def plot_clusters(diff_cluster, e1e2_change_path, dbscan_folder, parameters, change_threshold, vegetation=True):
    plt.figure(figsize=(20, 15), dpi=450)
    if vegetation:
        project_path = Path(dbscan_folder).parent
        name = get_file_name(e1e2_change_path).split('_vs_')[0]
        point_cloud = os.path.join(project_path, '1.2_canupo', name + '__canupo.xyz')
        if os.path.exists(point_cloud):
            canupo = loadPC(point_cloud, array=True)
            data_sorted = canupo[canupo[:, 0].argsort()]
            subsampled_data = data_sorted[::15]
            labels = subsampled_data[:, 3]
            colors = np.where(labels == 1, 'lightgrey', 'green')
            plt.scatter(-subsampled_data[:, 0], subsampled_data[:, 2], color=colors, s=1, marker='.')
            file_name = '_vegetation'
        else:
            _print("No vegetation files. This plot will be skipped")
            return
    else:
        project_path = Path(dbscan_folder).parent
        name = get_file_name(e1e2_change_path).split('__')[0]
        point_cloud = os.path.join(project_path, '3_change_detection', name + '__m3c2.xyz')
        pc = loadPC(point_cloud)
        data_sorted = pc.sort_values(by='x')
        subsampled_data = data_sorted.iloc[::15]
        plt.scatter(-subsampled_data['x'], subsampled_data['z'], color='lightgrey', s=1, marker='.')
        file_name = ''

    plt.scatter(-diff_cluster['x'], diff_cluster['z'], s=1.5, c='orange', marker='.')
    grouped = diff_cluster.groupby('rockfall_label').agg({'x': 'mean', 'z': 'mean'}).reset_index()
    for index, row in grouped.iterrows():
        plt.text(int(-row['x']-1), int(row['z']+1), f"{int(row['rockfall_label'])}", fontsize=12, ha='center', va='center')
    plt.axis('off')
    plt.tight_layout(pad=0.1)
    plt.title(f"{get_file_name(e1e2_change_path)} with DBSCAN (eps = {parameters['eps']}, minPts = {parameters['min_samples']}) and DiffThreshold = {change_threshold} m", fontsize=20)
    plt.savefig(os.path.join(dbscan_folder,get_file_name(e1e2_change_path)+f'{file_name}.jpg'), bbox_inches='tight', pad_inches=0.1)
    plt.close()

def dbscan(dbscan_folder, e1e2_change_path, parameters, spatial_resolution, change_threshold):
    file_name = get_file_name(e1e2_change_path)

    if parameters['auto_parameters_dbscan']:
        print("\nAuto DBSCAN parameters computation")
        parameters['min_samples'], parameters['eps'] = auto_param(spatial_resolution)

    diff_cluster = dbscan_core(e1e2_change_path, parameters['eps'], parameters['min_samples'])
    _print(f"DBSCAN -> eps:{parameters['eps']} and min_samples: {parameters['min_samples']}")

    if diff_cluster.shape[0] == 0:
        _print("DBSCAN found 0 clusters. No rockfall activity detected.")
        _print("We recommend double-checking the M3C2 output.")
        return None

    dbscan_path = savePC(os.path.join(dbscan_folder, file_name + '__dbscan.xyz'), diff_cluster)

    plot_clusters(diff_cluster, e1e2_change_path, dbscan_folder, parameters, change_threshold, vegetation=True)
    plot_clusters(diff_cluster, e1e2_change_path, dbscan_folder, parameters, change_threshold, vegetation=False)

    return dbscan_path