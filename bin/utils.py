import numpy as np
import open3d as o3d
from pathlib import Path
import os
import shutil

def loadPC(path):
    try:
        pc = np.loadtxt(path)
        print(f'Number of points: {pc.shape[0]} points')
        print(f'Number of columns {pc.shape[1]} columns')
        if pc.shape[1] > 4:
            print('Number of atributes > 4 - We will use attribute number for 4 for visualization')
    except:
        print('ERROR: Check that the PointCloud file fits the requirements')
        print(f'ERROR: {path}')
    return pc

def PCVisualization(path, enable=False):
    try:
        if enable:
            pcd = o3d.io.read_point_cloud(path, format='xyz')
            o3d.visualization.draw_geometries([pcd])
    except:
        print(f'ERROR: {path}')
    return

def get_file_name(path):
    file_name = Path(path).stem
    return file_name


def folders(output_path, epoch1_path, epoch2_path):
    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)
    project_path = os.path.join(output_path, epoch1_name + '_vs_' + epoch2_name)
    os.makedirs(project_path, exist_ok=True)
    os.makedirs(os.path.join(project_path,'source'), exist_ok=True)
    os.makedirs(os.path.join(project_path,'registration'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'm3c2'), exist_ok=True)
    return os.path.join(project_path,'source'), os.path.join(project_path,'registration'), os.path.join(project_path, 'm3c2')

def copy_source(pc1_path, pc2_path, source_path):
    shutil.copyfile(pc1_path, os.path.join(source_path, Path(pc1_path).stem + '.xyz'))
    shutil.copyfile(pc2_path, os.path.join(source_path, Path(pc2_path).stem + '.xyz'))

def savePC(path, pointcloud):
    np.savetxt(path, pointcloud, fmt='%1.3f', delimiter=' ')
    return path

