from scipy.spatial import Delaunay
import alphashape
from shapely.geometry import Polygon
from sklearn.neighbors import NearestNeighbors
from bin.utils import loadPC
from matplotlib.collections import PolyCollection
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('TkAgg')  #Activate/Deactivate interactive plot

#TODO: use original epoch2 points instead of epoch1+diff

def estimate_alpha(points, percentile=50):
    nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(points)
    distances, _ = nbrs.kneighbors(points)
    typical_distance = np.percentile(distances[:, 1], percentile)
    return 1 / (typical_distance * 2)

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
        volume = area * avg_diff
        volumes.append(volume)
    total_volume = np.sum(volumes)
    return total_volume

def volume_plot(valid_simplices, alpha_shape, points_xz):
    fig, ax = plt.subplots(figsize=(6, 6))
    for simplex in valid_simplices:
        ax.plot(points_xz[simplex, 0], points_xz[simplex, 1], 'c-', linewidth=0.5, alpha=0.5)
    x, y = alpha_shape.exterior.xy
    ax.plot(x, y, 'r--', linewidth=2)
    ax.set_title(f'Alpha Shape - Delaunay Triangulation (alpha={auto_alpha:.2f})\n'
                 f'Estimated Total Volume: {total_volume:.2f} m³')
    tri_diff = np.mean(diff[valid_simplices], axis=1)
    triangles = points_xz[valid_simplices]
    triangle_patchs = PolyCollection(triangles, array=tri_diff,
                                     cmap='YlGnBu', edgecolors='face',
                                     alpha=0.7)

    ax.add_collection(triangle_patchs)
    ax.set_aspect('equal', adjustable='box')
    cbar = plt.colorbar(triangle_patchs)
    cbar.set_label('Differences [m]')
    plt.savefig('Vol_rockfall.png', bbox_inches='tight', dpi=300)
    plt.close()

def rockfall_plot(points_xyz, y_diff, valid_simplices):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(points_xyz[:,0], points_xyz[:,1], points_xyz[:,2], triangles=valid_simplices, color='lightgreen', shade=True, alpha=0.80, edgecolor='black', linewidth=0.15, label='Epoch1')
    ax.plot_trisurf(points_xyz[:,0], y_diff, points_xyz[:,2], triangles=valid_simplices, color='cornflowerblue', shade=True, alpha=0.80, edgecolor='black', linewidth=0.15, label='Epoch1 + M3C2')
    ax.view_init(elev=15, azim=180)
    ax.legend()
    plt.savefig('3D_rockfall.png', bbox_inches='tight', dpi=300)
    plt.close()

def volume(e1ve2_DBSCAN_path):
    e1ve2_DBSCAN_path = r"C:\Users\XBG\Desktop\PyRockDiff_ICGCData\190711_Apostols_rock_to_240423_Apostols_rock\dbscan\190711_Apostols_rock_vs_240423_Apostols_rock_m3c2_dbscan.xyz"
    rockfalls = loadPC(e1ve2_DBSCAN_path)





points_xz = rockfall[:,[0,2]]
points_xyz = rockfall[:,[0,1,2]]
diff = rockfall[:, 3]*(-1)
y_diff = rockfall[:,1]+diff

auto_alpha = estimate_alpha(points_xz)
print(f"Automatically calculated alpha: {auto_alpha}")
valid_simplices, alpha_shape = alphashape_delaunay(points_xz, auto_alpha)
total_volume = calculate_triangle_volumes(points_xz, valid_simplices, diff)
volume_plot(valid_simplices, alpha_shape, points_xz)
rockfall_plot(points_xyz, y_diff, valid_simplices)





