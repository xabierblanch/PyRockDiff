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


def ransac_plane_fit(points, n_iterations=1000, distance_threshold=0.1, min_inliers=100):
    best_inliers = []
    best_plane = None
    n_points = len(points)

    for _ in range(n_iterations):
        sample_indices = np.random.choice(n_points, 3, replace=False)
        sample_points = points[sample_indices]

        v1 = sample_points[1] - sample_points[0]
        v2 = sample_points[2] - sample_points[0]
        normal = np.cross(v1, v2)

        if np.linalg.norm(normal) < 1e-6:
            continue

        normal = normal / np.linalg.norm(normal)
        d = -np.dot(normal, sample_points[0])
        distances = np.abs(np.dot(points, normal) + d)
        inliers = np.where(distances < distance_threshold)[0]

        if len(inliers) > len(best_inliers) and len(inliers) >= min_inliers:
            best_inliers = inliers
            best_plane = np.append(normal, d)

    if best_plane is None:
        return pca_plane_fallback(points)

    return best_plane, best_inliers


def pca_plane_fallback(points):
    _print("RANSAC failed, using PCA fallback")
    pca = PCA(n_components=3)
    centered_points = points - np.mean(points, axis=0)
    pca.fit(centered_points)
    normal = pca.components_[2]
    d = -np.dot(normal, np.mean(points, axis=0))
    plane_coeffs = np.append(normal, d)
    inliers = np.arange(len(points))
    return plane_coeffs, inliers


def align_to_plane(points, plane_coeffs):
    [a, b, c, d] = plane_coeffs
    normal = np.array([a, b, c])
    normal = normal / np.linalg.norm(normal)

    z_axis = np.array([0, 0, 1])
    v = np.cross(normal, z_axis)
    s = np.linalg.norm(v)
    c_dot = np.dot(normal, z_axis)

    if s < 1e-6:
        R = np.eye(3)
    else:
        vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        R = np.eye(3) + vx + np.dot(vx, vx) * ((1 - c_dot) / (s ** 2))

    return np.dot(points, R.T)


def compute_plane_projection(points_3d, plane_coeffs, xy_mean, pca_2d):
    pts_aligned = align_to_plane(points_3d, plane_coeffs)
    xy_pts = pts_aligned[:, :2]
    xy_centered = xy_pts - xy_mean
    xy_rotated = pca_2d.transform(xy_centered)
    return xy_rotated[:, 0]


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
    x_clusters = diff_cluster['x'].values
    z_clusters = diff_cluster['z'].values

    _print(f"Plot data: {len(diff_cluster)} points from {diff_cluster['rockfall_label'].max() + 1} DBSCAN clusters")

    pc_background = loadPC(m3c2_result_path)
    subsampled_background = pc_background.sort_values(by='x').iloc[::11]

    bg_points_3d = np.column_stack([
        subsampled_background['x'].values,
        subsampled_background['y'].values if 'y' in subsampled_background.columns else np.zeros(
            len(subsampled_background)),
        subsampled_background['z'].values
    ])

    _print("Computing RANSAC plane fit")
    plane_coeffs, inliers = ransac_plane_fit(bg_points_3d, n_iterations=1000, distance_threshold=0.10)

    bg_aligned = align_to_plane(bg_points_3d, plane_coeffs)
    xy_bg_aligned = bg_aligned[:, :2]
    pca_2d = PCA(n_components=2)
    xy_centered = xy_bg_aligned - np.mean(xy_bg_aligned, axis=0)
    pca_2d.fit(xy_centered)
    xy_mean = np.mean(xy_bg_aligned, axis=0)

    cluster_points_3d = np.column_stack([
        x_clusters,
        diff_cluster['y'].values if 'y' in diff_cluster.columns else np.zeros(len(x_clusters)),
        z_clusters
    ])
    x_clusters_proj = compute_plane_projection(cluster_points_3d, plane_coeffs, xy_mean, pca_2d)
    x_bg_proj = compute_plane_projection(bg_points_3d, plane_coeffs, xy_mean, pca_2d)
    z_bg = subsampled_background['z'].values

    fig_width, fig_height = compute_plot_dimensions(x_clusters_proj, z_clusters)
    beta = 1 if parameters["image_mirror"] else -1

    def create_and_save_plot(x_plot, z_plot, colors, file_suffix, include_labels=False):
        plt.figure(figsize=(fig_width, fig_height), dpi=300)

        plt.scatter(beta * x_plot, z_plot, color=colors, s=0.8, marker='.', alpha=0.9)

        cluster_color = 'cadetblue' if deformation else 'salmon'
        plt.scatter(beta * x_clusters_proj, z_clusters, s=1.1, c=cluster_color, marker='.', alpha=0.8)

        if include_labels:
            grouped = diff_cluster.groupby('rockfall_label').agg({
                'x': 'mean', 'z': 'mean', 'y': 'mean' if 'y' in diff_cluster.columns else 'first'
            }).reset_index()

            for _, row in grouped.iterrows():
                y_val = row.get('y', 0) if 'y' in row else 0
                label_points_3d = np.column_stack([[row['x']], [y_val], [row['z']]])
                x_label_transformed = compute_plane_projection(label_points_3d, plane_coeffs, xy_mean, pca_2d)[0]

                plt.text(float(beta * x_label_transformed) - 1, float(row['z']) + 1,
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
            x_veg_proj = compute_plane_projection(veg_points_3d, plane_coeffs, xy_mean, pca_2d)

            labels = subsampled_data[:, 3]
            colors = np.where(labels == 1, 'silver', 'green')

            create_and_save_plot(x_veg_proj, subsampled_data[:, 2], colors, '_veg', False)
            create_and_save_plot(x_veg_proj, subsampled_data[:, 2], colors, '_veg', True)
        else:
            _print("No vegetation files found")

    _print('Plotting with standard background')
    create_and_save_plot(x_bg_proj, z_bg, 'silver', '', False)
    create_and_save_plot(x_bg_proj, z_bg, 'silver', '', True)

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
