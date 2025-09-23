import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from bin.utils import loadPC, savePC, get_file_name, _print
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import math
from sklearn.neighbors import NearestNeighbors
import os


def dbscan_core(e1e2_change_path, eps, min_samples):
    print("\nDBSCAN Algorithm")
    diff_filter = loadPC(e1e2_change_path)
    _print(f'Running DBSCAN algorithm for clustering the {diff_filter.shape[0]} points')
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(diff_filter[['x', 'y', 'z']])
    labels = clustering.labels_.reshape((-1, 1))
    labels_df = pd.DataFrame(labels, columns=['rockfall_label'])
    diff_cluster = pd.concat([diff_filter.reset_index(drop=True), labels_df], axis=1)
    diff_cluster = diff_cluster[diff_cluster['rockfall_label'] >= 0]
    _print(
        f'DBSCAN algorithm applied correctly: {diff_cluster.shape[0]} points in {diff_cluster["rockfall_label"].max()} clusters identified')
    return diff_cluster


def find_wall_plane(points):
    pca = PCA(n_components=3)
    pca.fit(points)

    normal = pca.components_[2]
    if normal[2] < 0:
        normal = -normal

    center = np.mean(points, axis=0)

    z_axis = np.array([0, 0, 1])
    wall_dir = np.cross(normal, z_axis)
    wall_dir = wall_dir / np.linalg.norm(wall_dir)

    if np.dot(wall_dir, [1, 0, 0]) < 0:
        wall_dir = -wall_dir

    return wall_dir, center


def project_to_wall_view(points, wall_dir, center):
    centered_points = points - center

    x_wall = np.dot(centered_points, wall_dir)
    z_wall = centered_points[:, 2]

    return x_wall, z_wall


def compute_plot_dimensions(x_data, z_data, fixed_max=20):
    width = x_data.max() - x_data.min()
    height = z_data.max() - z_data.min()
    if max(width, height) == 0:
        return 20, 20
    scale = fixed_max / max(width, height)
    return width * scale, height * scale


def plot_clusters(diff_cluster, e1e2_change_path, m3c2_result_path, dbscan_folder,
                  parameters, change_threshold, deformation=False, vegetation=True):
    print('\nRendering Plots')

    pc_background = loadPC(m3c2_result_path)
    subsampled_background = pc_background.sort_values(by='x').iloc[::11]

    bg_points_3d = np.column_stack([
        subsampled_background['x'].values,
        subsampled_background['y'].values if 'y' in subsampled_background.columns else np.zeros(
            len(subsampled_background)),
        subsampled_background['z'].values
    ])

    _print("Finding wall plane orientation")
    wall_dir, center = find_wall_plane(bg_points_3d)

    x_bg_proj, z_bg_proj = project_to_wall_view(bg_points_3d, wall_dir, center)

    cluster_points_3d = np.column_stack([
        diff_cluster['x'].values,
        diff_cluster['y'].values if 'y' in diff_cluster.columns else np.zeros(len(diff_cluster)),
        diff_cluster['z'].values
    ])
    x_clusters_proj, z_clusters_proj = project_to_wall_view(cluster_points_3d, wall_dir, center)

    fig_width, fig_height = compute_plot_dimensions(x_clusters_proj, z_clusters_proj)
    beta = 1 if parameters["image_mirror"] else -1

    _print(f"Plot data: {len(diff_cluster)} points from {diff_cluster['rockfall_label'].max() + 1} DBSCAN clusters")

    def create_and_save_plot(x_plot, z_plot, colors, file_suffix, include_labels=False):
        plt.figure(figsize=(fig_width, fig_height), dpi=300)

        plt.scatter(beta * x_plot, z_plot, color=colors, s=0.8, marker='.', alpha=0.9)

        cluster_color = 'cadetblue' if deformation else 'salmon'
        plt.scatter(beta * x_clusters_proj, z_clusters_proj, s=1.1, c=cluster_color, marker='.', alpha=0.8)

        if include_labels:
            grouped = diff_cluster.groupby('rockfall_label').agg({
                'x': 'mean', 'z': 'mean', 'y': 'mean' if 'y' in diff_cluster.columns else 'first'
            }).reset_index()

            for _, row in grouped.iterrows():
                label_point_3d = np.array([[row['x'], row.get('y', 0), row['z']]])
                x_label_proj, z_label_proj = project_to_wall_view(label_point_3d, wall_dir, center)

                plt.text(float(beta * x_label_proj[0]) - 1, float(z_label_proj[0]) + 1,
                         f"{int(row['rockfall_label'])}",
                         fontsize=13, ha='center', va='center',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

        plt.gca().set_aspect('equal')
        plt.axis('off')
        plt.tight_layout(pad=0.1)
        plt.subplots_adjust(top=0.93)
        plt.title(
            f"{get_file_name(e1e2_change_path)} | DBSCAN (eps = {parameters['eps']:.2f}, minPts = {parameters['min_samples']}) | DiffThreshold = {change_threshold} m",
            fontsize=20)

        suffix = '_labels' if include_labels else ''
        output_filename = get_file_name(e1e2_change_path) + f'{file_suffix}{suffix}.jpg'
        _print(f'Saving plot (including labels = {include_labels})')
        plt.savefig(os.path.join(dbscan_folder, output_filename), dpi=300, pad_inches=0.1)
        plt.close()

    if vegetation:
        _print('Plotting with vegetation background')
        project_path = Path(dbscan_folder).parent
        name = get_file_name(e1e2_change_path).split('_vs_')[0]
        point_cloud = os.path.join(project_path, '2_Vegetation_Filter', name + '__canupo.xyz')

        if os.path.exists(point_cloud):
            canupo = loadPC(point_cloud, array=True)
            subsampled_data = canupo[canupo[:, 0].argsort()][::11]

            veg_points_3d = np.column_stack([subsampled_data[:, 0], subsampled_data[:, 1], subsampled_data[:, 2]])
            x_veg_proj, z_veg_proj = project_to_wall_view(veg_points_3d, wall_dir, center)

            labels = subsampled_data[:, 3]
            colors = np.where(labels == 1, 'silver', 'green')

            create_and_save_plot(x_veg_proj, z_veg_proj, colors, '_veg', False)
            create_and_save_plot(x_veg_proj, z_veg_proj, colors, '_veg', True)
        else:
            _print("No vegetation files found")

    _print('Plotting with standard background')
    create_and_save_plot(x_bg_proj, z_bg_proj, 'silver', '', False)
    create_and_save_plot(x_bg_proj, z_bg_proj, 'silver', '', True)


def auto_param(m3c2_result_path, spatial_resolution, parameters):
    points = loadPC(m3c2_result_path)
    nbrs = NearestNeighbors(n_neighbors=10).fit(points[["x", "y", "z"]])
    distances, _ = nbrs.kneighbors(points[["x", "y", "z"]])
    k_distances = np.sort(distances[:, -1])
    eps = np.percentile(k_distances, 90)
    expected_pts = (math.pi * eps ** 2) / (spatial_resolution ** 2)
    alpha = parameters['auto_parameters_dbscan_alpha']
    minpts = math.ceil(alpha * expected_pts)
    _print(f'DBSCAN Automatic Parameters. Alpha value = {alpha}:')
    _print(f'DBSCAN eps: {eps:.2f}')
    _print(f'DBSCAN min_points: {minpts:.0f}')
    return minpts, eps


def dbscan(dbscan_folder, e1e2_change_path, m3c2_result_path, parameters, deformation=False):
    spatial_resolution = parameters['subsampling']['spatial_resolution']

    if deformation:
        parameters = parameters['deformation']
    else:
        parameters = parameters['rockfall']

    threshold = parameters['change_threshold']
    file_name = get_file_name(e1e2_change_path)

    if parameters['auto_parameters_dbscan']:
        print("Auto DBSCAN parameters computation")
        parameters['min_samples'], parameters['eps'] = auto_param(m3c2_result_path, spatial_resolution, parameters)

    diff_cluster = dbscan_core(e1e2_change_path, parameters['eps'], parameters['min_samples'])
    _print(f"DBSCAN -> eps:{parameters['eps']} and min_samples: {parameters['min_samples']}")

    if diff_cluster.shape[0] == 0:
        _print("DBSCAN found 0 clusters. No rockfall activity detected.")
        _print("We recommend double-checking the M3C2 output.")
        return None

    dbscan_path = savePC(os.path.join(dbscan_folder, file_name + '__dbscan.xyz'), diff_cluster)

    project_path = Path(dbscan_folder).parent
    name = get_file_name(e1e2_change_path).split('_vs_')[0]
    point_cloud = os.path.join(project_path, '2_Vegetation_Filter', name + '__canupo.xyz')

    if os.path.exists(point_cloud):
        try:
            _print("Plotting results with vegetation background")
            plot_clusters(diff_cluster, e1e2_change_path, m3c2_result_path, dbscan_folder, parameters, threshold,
                          deformation, vegetation=True)
        except Exception as e:
            _print(f"Error creating vegetation plot: {e}")

    try:
        _print("Plotting results with standard background")
        plot_clusters(diff_cluster, e1e2_change_path, m3c2_result_path, dbscan_folder, parameters, threshold,
                      deformation, vegetation=False)
    except Exception as e:
        _print(f"Error creating standard plot: {e}")

    return dbscan_path
