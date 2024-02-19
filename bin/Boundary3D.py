import numpy as np
import matplotlib.pyplot as plt
import alphashape
from bin.utils import loadPC, savePC, get_file_name
import os
def extract_boundary(epoch_xz):
    #alpha = 0.95 * alphashape.optimizealpha(epoch_xz)
    alpha = 0.5
    hull = alphashape.alphashape(epoch_xz, alpha)
    if hull.geom_type =='Polygon':
        hull_pts = hull.exterior.coords.xy
    else:
        polygon = list(hull.geoms) #get all polygons
        max_area = 0
        for i, poly in enumerate(polygon):
            area = poly.area
            if area > max_area:
                max_area = area
                id = i
        hull_pts = polygon[i]
        hull_pts = hull_pts.exterior.coords.xy
    line = plt.plot(hull_pts[0], hull_pts[1])
    return hull_pts, line

def plot_boundary(epoch, hull_pts, plot=False):
    if plot:
        fig = plt.figure()
        plt.scatter(hull_pts[0], hull_pts[1])
        plt.scatter(epoch[:,0], epoch[:,2], c='r', s=0.001)
        plt.show()
def remove_points(epoch, line):
    mask = line[0].get_path().contains_points(epoch[:,[0,2]])
    filtered_epoch = epoch[mask]
    return filtered_epoch

def main_2Dcut(epoch1_path, epoch2_path, registration_path):
    epoch1 = loadPC(epoch1_path)
    epoch2 = loadPC(epoch2_path)
    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)

    epoch_xz = epoch1[:, [0, 2]]
    hull_pts, line = extract_boundary(epoch_xz)
    plot_boundary(epoch2, hull_pts, plot=True)
    plot_boundary(epoch1, hull_pts, plot=True)
    epoch1_cut = remove_points(epoch1, line)
    epoch2_cut = remove_points(epoch2, line)

    epoch_xz = epoch2_cut[:, [0, 2]]
    hull_pts, line = extract_boundary(epoch_xz)
    plot_boundary(epoch1_cut, hull_pts, plot=True)
    plot_boundary(epoch2_cut, hull_pts, plot=True)

    epoch1_cut = remove_points(epoch1_cut, line)
    epoch2_cut = remove_points(epoch2_cut, line)
    epoch1_cut_path = savePC(os.path.join(registration_path, epoch1_name + '_reg_cut.xyz'), epoch1_cut)
    epoch2_cut_path = savePC(os.path.join(registration_path, epoch2_name + '_reg_cut.xyz'), epoch2_cut)

    return epoch1_cut_path, epoch2_cut_path

