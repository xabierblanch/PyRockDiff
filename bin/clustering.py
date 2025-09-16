import matplotlib.pyplot as plt
from pathlib import Path
from bin.utils import loadPC, savePC, get_file_name, create_folder, _print, auto_param
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
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
    x = diff_cluster['x'].values
    y = diff_cluster['y'].values if 'y' in diff_cluster.columns else np.zeros(len(diff_cluster))
    z = diff_cluster['z'].values

    points_xy = np.column_stack([x, y])
    pca_2d = PCA(n_components=2)
    centered_xy = points_xy - np.mean(points_xy, axis=0)
    pca_2d.fit(centered_xy)
    rotated_xy = pca_2d.transform(centered_xy)
    x_aligned = rotated_xy[:, 0]
    z_original = z

    invert_x = np.mean(x_aligned) < 0
    x_aligned_cluster = -x_aligned if invert_x else x_aligned

    width = x_aligned_cluster.max() - x_aligned_cluster.min()
    height = z_original.max() - z_original.min()
    fixed_max = 20
    if max(width, height) == 0:
        fig_width = fig_height = 20
    else:
        scale = fixed_max / max(width, height)
        fig_width = width * scale
        fig_height = height * scale

    plt.figure(figsize=(fig_width, fig_height), dpi=300)

    def transform_base_points(x_vals, z_vals, y_vals=None):
        if y_vals is None:
            y_vals = np.zeros_like(x_vals)
        pts = np.column_stack([x_vals, y_vals])
        centered = pts - np.mean(points_xy, axis=0)
        rotated = pca_2d.transform(centered)
        return rotated[:, 0], z_vals

    def transform_cluster_points(x_vals, z_vals, y_vals=None):
        if y_vals is None:
            y_vals = np.zeros_like(x_vals)
        pts = np.column_stack([x_vals, y_vals])
        centered = pts - np.mean(points_xy, axis=0)
        rotated = pca_2d.transform(centered)
        x_clust = -rotated[:, 0] if invert_x else rotated[:, 0]
        return x_clust, z_vals

    if vegetation:
        project_path = Path(dbscan_folder).parent
        name = get_file_name(e1e2_change_path).split('_vs_')[0]
        point_cloud = os.path.join(project_path, '1.2_canupo', name + '__canupo.xyz')
        if os.path.exists(point_cloud):
            canupo = loadPC(point_cloud, array=True)
            data_sorted = canupo[canupo[:, 0].argsort()]
            subsampled_data = data_sorted[::15]
            labels = subsampled_data[:, 3]
            colors = np.where(labels == 1, 'silver', 'green')
            x_plot, z_plot = transform_base_points(subsampled_data[:, 0], subsampled_data[:, 2], subsampled_data[:, 1] if subsampled_data.shape[1] > 3 else None)
            plt.scatter(-x_plot, z_plot, color=colors, s=0.75, marker='.')
            file_name = '_veg'
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
        y_vals = subsampled_data['y'].values if 'y' in subsampled_data.columns else None
        x_plot, z_plot = transform_base_points(subsampled_data['x'].values, subsampled_data['z'].values, y_vals)
        plt.scatter(-x_plot, z_plot, color='silver', s=0.75, marker='.')
        file_name = ''

    plt.scatter(x_aligned_cluster, z_original, s=1.5, c='orange', marker='.')

    grouped = diff_cluster.groupby('rockfall_label').agg({'x': 'mean', 'z': 'mean', 'y': 'mean' if 'y' in diff_cluster.columns else 'first'}).reset_index()
    for index, row in grouped.iterrows():
        y_val = row.get('y', 0) if 'y' in row else 0
        x_text, z_text = transform_cluster_points(np.array([row['x']]), np.array([row['z']]), np.array([y_val]))
        plt.text(float(x_text[0])-1, float(z_text[0])+1, f"{int(row['rockfall_label'])}", fontsize=13, ha='center', va='center')

    plt.gca().set_aspect('equal')
    plt.axis('off')
    plt.tight_layout(pad=0.1)
    plt.subplots_adjust(top=0.95)
    plt.title(f"{get_file_name(e1e2_change_path)} with DBSCAN (eps = {parameters['eps']:.1f}, minPts = {parameters['min_samples']}) and DiffThreshold = {change_threshold} m", fontsize=20)
    plt.savefig(os.path.join(dbscan_folder, get_file_name(e1e2_change_path) + f'{file_name}.jpg'), dpi=300, pad_inches=0.1)
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