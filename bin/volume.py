from scipy.spatial import Delaunay
import alphashape
from sklearn.neighbors import NearestNeighbors
from bin.utils import loadPC, _print, get_file_name
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from shapely.geometry import Polygon, MultiPolygon
import numpy as np
import os
from bin.clustering import project_to_wall_view

#TODO: use original epoch2 points instead of epoch1+diff

def estimate_alpha(points, percentile=50):
    nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(points)
    distances, _ = nbrs.kneighbors(points)
    typical_distance = np.percentile(distances[:, 1], percentile)
    return round(1 / (typical_distance * 2),4)

def alphashape_delaunay(points, alpha):
    alpha_shape = alphashape.alphashape(points, alpha)
    tri = Delaunay(points)

    valid_simplices = []
    for simplex in tri.simplices:
        triangle = Polygon(points[simplex])
        if alpha_shape.contains(triangle.centroid):
            valid_simplices.append(simplex)

    return np.array(valid_simplices), alpha_shape

def calculate_triangle_volumes(points, simplices, diff):
    volumes = []
    for simplex in simplices:
        triangle = points[simplex]
        area = 0.5 * np.abs(np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0]))
        avg_diff = np.mean(diff[simplex])
        volume = area * (-avg_diff)
        volumes.append(volume)
    total_volume = np.sum(volumes)
    return round(total_volume, 6)


def volume_plot(valid_simplices, alpha_shape, diff, auto_alpha, total_volume, points_xz, volume_folder, i, file_name):
    matplotlib.use('Agg')
    try:
        fig, ax = plt.subplots(figsize=(6, 6))

        for simplex in valid_simplices:
            ax.plot(points_xz[simplex, 0], points_xz[simplex, 1], 'c-', linewidth=0.5, alpha=0.5)

        if isinstance(alpha_shape, Polygon):
            x, y = alpha_shape.exterior.xy
            ax.plot(x, y, 'r--', linewidth=2)

        elif isinstance(alpha_shape, MultiPolygon):
            for poly in alpha_shape.geoms:
                x, y = poly.exterior.xy
                ax.plot(x, y, 'r--', linewidth=2)

        tri_diff = np.mean(diff[valid_simplices], axis=1)
        triangles = points_xz[valid_simplices]
        triangle_patchs = PolyCollection(triangles, array=tri_diff,
                                         cmap='YlGnBu', edgecolors='face',
                                         alpha=0.7)

        ax.add_collection(triangle_patchs)
        ax.set_aspect('equal', adjustable='box')

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        cbar = fig.colorbar(triangle_patchs, cax=cax)
        cbar.set_label('Differences [m]')

        ax.set_title(f'{file_name} - Cluster: {i} | Volume: {total_volume:.2f} m³',
                     loc='center', pad=10, fontsize=14)

        os.makedirs(os.path.join(volume_folder, 'vol_plots'), exist_ok=True)
        output_path = os.path.join(volume_folder, 'vol_plots', f'{file_name}_{i}_Vol.png')
        plt.savefig(output_path, dpi=300)
        plt.close()

    except Exception as e:
        _print(f"ERROR: Plot {i} can't be done: {str(e)}")

def rockfall_plot(points_xyz, y_diff, valid_simplices, volume_folder, i, file_name):
    matplotlib.use('Agg')
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(points_xyz[:,0], points_xyz[:,1], points_xyz[:,2], triangles=valid_simplices, color='lightgreen', shade=True, alpha=0.80, edgecolor='black', linewidth=0.15, label='Epoch1')
    ax.plot_trisurf(points_xyz[:,0], y_diff, points_xyz[:,2], triangles=valid_simplices, color='cornflowerblue', shade=True, alpha=0.80, edgecolor='black', linewidth=0.15, label='Epoch1 + M3C2')
    ax.view_init(elev=15, azim=180)
    ax.legend()
    os.makedirs(os.path.join(volume_folder, '3D_plots'), exist_ok=True)
    output_path = os.path.join(volume_folder, '3D_plots', f'{file_name}_{i}_3D.png')
    plt.title(f'{file_name} - Cluster: {i}')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def rockfall_db(volume_folder, rockfalls, volumes_db, file_name):
    database = rockfalls.groupby(['rockfall_label']).median()
    merged_df = pd.merge(database, volumes_db, on='rockfall_label', how='left')
    merged_df = merged_df.round(4)
    merged_df.to_csv(os.path.join(volume_folder, file_name + '__db.csv'), sep=' ', index=False)

def volume(e1ve2_DBSCAN_path, volume_folder, parameters, wall_projection=None):
    image_mirror = parameters['rockfall']['image_mirror']
    beta = 1 if image_mirror else -1

    rockfalls = loadPC(e1ve2_DBSCAN_path)
    file_name = get_file_name(e1ve2_DBSCAN_path)
    if wall_projection is not None:
        wall_direction, wall_center = wall_projection
    else:
        wall_direction, wall_center = None, None

    rockfall_volumes = []
    _print("Computing volume for every cluster")

    for i in range(rockfalls['rockfall_label'].max()+1):
        _print(f'Computing volume: cluster {i} of {rockfalls["rockfall_label"].max()+1}')
        rockfall = rockfalls[rockfalls["rockfall_label"] == i]
        if len(rockfall) < 4:
            _print(f"Cluster {i} has less than 4 points. Will not be computed.")
            continue
        points_xyz = rockfall[['x', 'y', 'z']].values
        if wall_direction is not None and wall_center is not None:
            x_proj, z_proj = project_to_wall_view(points_xyz, wall_direction, wall_center)
            points_xz = np.column_stack([beta * x_proj, z_proj])
        else:
            # points_xz = rockfall[['x', 'z']].values
            points_xz = np.column_stack([beta * rockfall[['x']].values.flatten(), rockfall[['z']].values.flatten()])
        diff = rockfall['m3c2_diff'].values*(-1)
        y_diff = rockfall['y'].values+diff
        auto_alpha = estimate_alpha(points_xz)
        _print(f"Automatically calculated alpha: {auto_alpha}")
        valid_simplices, alpha_shape = alphashape_delaunay(points_xz, auto_alpha)
        total_volume = calculate_triangle_volumes(points_xz, valid_simplices, diff)
        _print(f"Cluster {i}: Volume: {total_volume} m³")
        rockfall_volumes.append({'rockfall_label': i, 'total_volume': total_volume})
        volume_plot(valid_simplices, alpha_shape, diff, auto_alpha, total_volume, points_xz, volume_folder, i, file_name)
        rockfall_plot(points_xyz, y_diff, valid_simplices, volume_folder, i, file_name)

    volumes_db = pd.DataFrame(rockfall_volumes)
    rockfall_db(volume_folder, rockfalls, volumes_db, file_name)
    return volumes_db