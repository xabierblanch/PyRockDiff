from bin.utils import loadPC
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree
from alpha_shapes import Alpha_Shaper
from sklearn.neighbors import NearestNeighbors
import open3d as o3d

def visualize_rockfall(rockfall, shape, alpha_shape):
    fig = plt.figure()
    # ax = plt.axes(projection='3d')
    plt.scatter(rockfall[:,0], rockfall[:,2])
    plt.triplot(rockfall[:, 0], rockfall[:, 2], shape.triangles)
    x, y = alpha_shape.exterior.xy
    plt.plot(x, y)
    plt.show()

def estimate_alpha_distance(points, percentile=50):
    """Estima alpha basado en la distancia entre puntos vecinos."""
    nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(points)
    distances, _ = nbrs.kneighbors(points)
    typical_distance = np.percentile(distances[:, 1], percentile)
    return 1 / (typical_distance * 2)

rockfall_path = r"C:\Users\XBG\Desktop\PyRockDiff_ICGCData\190711_Apostols_rock_to_240423_Apostols_rock\rockfall\rockfall.xyz"

rockfall = loadPC(rockfall_path)
alpha_distance = estimate_alpha_distance(rockfall[:,[0,2]])

shaper = Alpha_Shaper(rockfall[:,[0,2]])
alpha_opt, alpha_shape = shaper.optimize()
# alpha_shape = shaper.get_shape(alpha=5)


plt.scatter(rockfall[:,0], rockfall[:,2])
plt.triplot(shaper)
x, y = alpha_shape.exterior.xy
plt.plot(x, y)
plt.show()

#visualize_rockfall(rockfall, shaper, alpha_shape)
