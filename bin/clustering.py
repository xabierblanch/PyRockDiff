import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from bin.utils import loadPC, savePC, get_file_name, create_folder, _print
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import math
import open3d as o3d
from sklearn.neighbors import NearestNeighbors
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

def ransac_plane_fit(points, n_iterations=1000, distance_threshold=0.05, min_inliers=100):
    best_inliers = []
    best_plane = None

    n_points = len(points)

    for _ in range(n_iterations):
        sample_indices = np.random.choice(n_points, 3, replace=False)
        sample_points = points[sample_indices]

        # Calcular plano usando los 3 puntos
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
        return pca_fallback(points)

    return best_plane, best_inliers


def align_to_plane(points, plane_coeffs):
    [a, b, c, d] = plane_coeffs
    normal = np.array([a, b, c])
    normal = normal / np.linalg.norm(normal)

    z_axis = np.array([0, 0, 1])

    v = np.cross(normal, z_axis)
    s = np.linalg.norm(v)
    c = np.dot(normal, z_axis)

    if s < 1e-6:
        R = np.eye(3)
    else:
        vx = np.array([[0, -v[2], v[1]],
                       [v[2], 0, -v[0]],
                       [-v[1], v[0], 0]])
        R = np.eye(3) + vx + np.dot(vx, vx) * ((1 - c) / (s ** 2))

    aligned_points = np.dot(points, R.T)

    return aligned_points


def pca_fallback(points):
    pca = PCA(n_components=3)
    centered_points = points - np.mean(points, axis=0)
    pca.fit(centered_points)

    normal = pca.components_[2]
    d = -np.dot(normal, np.mean(points, axis=0))
    plane_coeffs = np.append(normal, d)

    aligned_points = align_to_plane(points, plane_coeffs)
    inliers = np.arange(len(points))  # Todos son inliers en PCA

    return plane_coeffs, inliers, aligned_points


def plot_clusters(diff_cluster, e1e2_change_path, m3c2_result_path, dbscan_folder, parameters, change_threshold,
                  vegetation=True):
    x = diff_cluster['x'].values
    y = diff_cluster['y'].values if 'y' in diff_cluster.columns else np.zeros(len(diff_cluster))
    z = diff_cluster['z'].values

    # ✅ CALCULAR RANSAC CON BACKGROUND
    pc_background = loadPC(m3c2_result_path)
    data_sorted = pc_background.sort_values(by='x')
    subsampled_background = data_sorted.iloc[::15]

    bg_points_3d = np.column_stack([
        subsampled_background['x'].values,
        subsampled_background['y'].values if 'y' in subsampled_background.columns else np.zeros(
            len(subsampled_background)),
        subsampled_background['z'].values
    ])

    plane_coeffs, inliers = ransac_plane_fit(
        bg_points_3d,
        n_iterations=1000,
        distance_threshold=0.05,
        min_inliers=max(100, len(bg_points_3d) // 20)
    )

    if plane_coeffs is None:
        pca = PCA(n_components=3)
        centered = bg_points_3d - np.mean(bg_points_3d, axis=0)
        pca.fit(centered)
        normal = pca.components_[2]
        plane_coeffs = np.append(normal, -np.dot(normal, np.mean(bg_points_3d, axis=0)))

    bg_aligned = align_to_plane(bg_points_3d, plane_coeffs)
    xy_bg_aligned = bg_aligned[:, :2]

    pca_2d = PCA(n_components=2)
    xy_centered = xy_bg_aligned - np.mean(xy_bg_aligned, axis=0)
    pca_2d.fit(xy_centered)

    xy_mean = np.mean(xy_bg_aligned, axis=0)

    def transform_points(x_vals, z_vals, y_vals=None, apply_inversion=False):
        if y_vals is None:
            y_vals = np.zeros_like(x_vals)

        pts_3d = np.column_stack([x_vals, y_vals, z_vals])
        pts_aligned = align_to_plane(pts_3d, plane_coeffs)
        xy_pts = pts_aligned[:, :2]
        xy_centered = xy_pts - xy_mean
        xy_rotated = pca_2d.transform(xy_centered)
        x_transformed = xy_rotated[:, 0]

        if apply_inversion:
            x_transformed = -x_transformed

        return x_transformed, z_vals

    # ✅ TRANSFORMAR CLUSTERS
    points_3d = np.column_stack([x, y, z])
    x_clusters, z_clusters = transform_points(x, z, y, apply_inversion=False)

    if np.mean(x_clusters) < 0:
        x_clusters = -x_clusters
        invert_background = True
    else:
        invert_background = False

    # ✅ CALCULAR FIGSIZE
    width = x_clusters.max() - x_clusters.min()
    height = z_clusters.max() - z_clusters.min()
    fixed_max = 20
    if max(width, height) == 0:
        fig_width = fig_height = 20
    else:
        scale = fixed_max / max(width, height)
        fig_width = width * scale
        fig_height = height * scale

    # ✅ CONTROLAR MIRRORING
    if parameters["image_mirror"]:
        beta = 1
    else:
        beta = -1

    # ✅ PREPARAR DATOS SEGÚN VEGETATION (SOLO UNA OPCIÓN)
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

            x_plot, z_plot = transform_points(
                subsampled_data[:, 0],
                subsampled_data[:, 2],
                subsampled_data[:, 1] if subsampled_data.shape[1] > 3 else None,
                apply_inversion=invert_background
            )
            file_name = '_veg'
        else:
            _print("No vegetation files. This plot will be skipped")
            return
    else:
        # Usar background sin vegetación
        y_vals = subsampled_background['y'].values if 'y' in subsampled_background.columns else None
        x_plot, z_plot = transform_points(
            subsampled_background['x'].values,
            subsampled_background['z'].values,
            y_vals,
            apply_inversion=invert_background
        )
        colors = 'silver'  # Solo color plata
        file_name = ''

    # ✅ FUNCIÓN PARA CREAR PLOT (EVITAR DUPLICACIÓN)
    def create_and_save_plot(include_labels=False):
        plt.figure(figsize=(fig_width, fig_height), dpi=300)

        # Plotear background
        if vegetation:
            plt.scatter(beta * x_plot, z_plot, color=colors, s=0.75, marker='.', alpha=0.6)
        else:
            plt.scatter(beta * x_plot, z_plot, color=colors, s=0.75, marker='.', alpha=0.6)

        # Plotear clusters
        plt.scatter(beta * x_clusters, z_clusters, s=1.5, c='orange', marker='.', alpha=0.8)

        # ✅ AÑADIR ETIQUETAS SI CORRESPONDE
        if include_labels:
            grouped = diff_cluster.groupby('rockfall_label').agg({
                'x': 'mean',
                'z': 'mean',
                'y': 'mean' if 'y' in diff_cluster.columns else 'first'
            }).reset_index()

            for index, row in grouped.iterrows():
                y_val = row.get('y', 0) if 'y' in row else 0
                x_text, z_text = transform_points(
                    np.array([row['x']]),
                    np.array([row['z']]),
                    np.array([y_val]),
                    apply_inversion=invert_background
                )
                plt.text(float(beta * x_text[0]) - 1, float(z_text[0]) + 1,
                         f"{int(row['rockfall_label'])}",
                         fontsize=13, ha='center', va='center',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

        plt.gca().set_aspect('equal')
        plt.axis('off')
        plt.tight_layout(pad=0.1)
        plt.subplots_adjust(top=0.95)
        plt.title(
            f"{get_file_name(e1e2_change_path)} with DBSCAN (eps = {parameters['eps']:.2f}, minPts = {parameters['min_samples']}) and DiffThreshold = {change_threshold} m",
            fontsize=20)

        # Determinar nombre del archivo
        suffix = '_labels' if include_labels else ''
        output_filename = get_file_name(e1e2_change_path) + f'{file_name}{suffix}.jpg'

        plt.savefig(os.path.join(dbscan_folder, output_filename), dpi=300, pad_inches=0.1)
        plt.close()

    # ✅ GENERAR SOLO 2 PLOTS SEGÚN EL MODO
    create_and_save_plot(include_labels=False)  # Plot sin etiquetas
    create_and_save_plot(include_labels=True)  # Plot con etiquetas


def auto_param(m3c2_result_path, spatial_resolution):
    points = loadPC(m3c2_result_path)
    nbrs = NearestNeighbors(n_neighbors=10).fit(points[["x", "y", "z"]])
    distances, _ = nbrs.kneighbors(points[["x", "y", "z"]])
    k_distances = np.sort(distances[:, -1])
    eps = np.percentile(k_distances, 90)
    expected_pts = (math.pi * eps**2) / (spatial_resolution**2)
    alpha = 0.5
    minpts = math.ceil(alpha * expected_pts)
    _print(f'DBSCAN Automatic Parameters:')
    _print(f'DBSCAN eps: {eps:.2f}')
    _print(f'DBSCAN min_points: {minpts:.0f}')
    return minpts, eps

def dbscan(dbscan_folder, e1e2_change_path, m3c2_result_path, parameters, spatial_resolution, change_threshold):
    file_name = get_file_name(e1e2_change_path)

    if parameters['auto_parameters_dbscan']:
        print("\nAuto DBSCAN parameters computation")
        parameters['min_samples'], parameters['eps'] = auto_param(m3c2_result_path, spatial_resolution)

    diff_cluster = dbscan_core(e1e2_change_path, parameters['eps'], parameters['min_samples'])
    _print(f"DBSCAN -> eps:{parameters['eps']} and min_samples: {parameters['min_samples']}")

    if diff_cluster.shape[0] == 0:
        _print("DBSCAN found 0 clusters. No rockfall activity detected.")
        _print("We recommend double-checking the M3C2 output.")
        return None

    dbscan_path = savePC(os.path.join(dbscan_folder, file_name + '__dbscan.xyz'), diff_cluster)

    plot_clusters(diff_cluster, e1e2_change_path, m3c2_result_path, dbscan_folder, parameters, change_threshold, vegetation=True)
    plot_clusters(diff_cluster, e1e2_change_path, m3c2_result_path, dbscan_folder, parameters, change_threshold, vegetation=False)

    return dbscan_path