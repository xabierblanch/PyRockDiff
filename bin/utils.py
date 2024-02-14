import numpy as np
import open3d as o3d

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
