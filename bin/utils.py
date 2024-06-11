import numpy as np
import open3d as o3d
from pathlib import Path
import os
import shutil
import subprocess
import datetime
from sklearn.cluster import DBSCAN


def start_code(options, parameters, e1_path, e2_path):
    e1 = get_file_name(e1_path)
    e2 = get_file_name(e2_path)
    print('\n\n*****************************************************')
    print(f'PyRockDiff will automatically perform a 3D comparison'
          f' between the point cloud {e1} and the point cloud {e2}.\n'
          f'\nThe following functions are enabled:\n')

    for option in options:
        print(f'{option}: {options[option]}')

    print(f'\nAnd the following parameters will be used:\n')
    for parameter in parameters:
        print(f'{parameter}: {parameters[parameter]}')
    print('\n\n*****************************************************')


def loadPC(path):
    _print(f'File {get_file_name(path)}: Loading')
    get_file_name(path)
    for skiprows in range (25):
        try:
            pc = np.loadtxt(path, skiprows=skiprows)
            _print(f'File {get_file_name(path)}: Done')
            return pc
        except:
            _print(f'Skipping line: {skiprows}, and trying to load the file again')

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


def create_project_folders(output_path, epoch1_path, epoch2_path):
    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)
    project_path = os.path.join(output_path, epoch1_name + '_vs_' + epoch2_name)
    os.makedirs(project_path, exist_ok=True)
    return project_path

def create_folder(project_path, folder):
    os.makedirs(os.path.join(project_path, folder), exist_ok=True)
    return os.path.join(project_path, folder)

def copy_source(pc1_path, project_folder):
    try:
        shutil.copyfile(pc1_path, os.path.join(project_folder, Path(pc1_path).stem + '.xyz'))
    except:
        _print('Raw files have not been copied')
    return os.path.join(project_folder, Path(pc1_path).stem + '.xyz')

def savePC(path, pointcloud):
    pc_name = get_file_name(path)
    _print(f"Saving {pc_name} data in '{Path(path).parts[-2]}' folder")
    np.savetxt(path, pointcloud, fmt='%1.3f', delimiter=' ')
    _print(f"Saving {pc_name} completed")
    return path

def subsampling(path, spatial_distance, CloudComapare_path, subsample_folder):
    output_path = os.path.join(subsample_folder, get_file_name(path) + "_sub.txt")

    _print(f'Subsampling {get_file_name(path)}. Spatial distance: {spatial_distance} cm')

    CC_SUB_Command = [CloudComapare_path,
                      "-AUTO_SAVE", "OFF",
                      "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                      "-O", path,
                      "-SS", "SPATIAL", str(spatial_distance),
                      "-SAVE_CLOUDS", "FILE", f'"{output_path}"']

    subprocess.run(CC_SUB_Command)
    _print(f'Subsampling {get_file_name(path)} completed')
    _print(f'Subsampling {get_file_name(output_path)} saved')
    return os.path.join(subsample_folder, get_file_name(path) + "_sub.txt")

def _print(message):
    """Prints a message with a timestamp in the format [DD/MM/YYYY - HH:MM] :: """
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("[%d/%m/%Y - %H:%M]")
    print(f"{formatted_time} :: {message}")

def transform_files(path, raw_folder):
    pc = loadPC(path)
    pc_name = get_file_name(path)
    _print("Only X,Y,Z values will be loaded")
    pc_xyz = pc[:, [0,1,2]]

    _print("First 10 lines of pc_xyz:\n")
    for i in range(10):
        print(f'line {i} -> {pc_xyz[i]}')

    skipLines = int(input("\nPlease select the first line with X,Y,Z data\n"))
    pc_xyz = pc_xyz[skipLines:]
    mask = np.all(pc_xyz != 0, axis=1)  # Create mask for non-zero rows
    pc_xyz_filtered = pc_xyz[mask]
    _print(f"Line 0 to {skipLines} will be removed from your file")
    savePC(os.path.join(raw_folder,pc_name + '.txt'), pc_xyz_filtered)
    return os.path.join(raw_folder,pc_name + '.txt')

def dbscan_core(pc_path, eps, min_samples):
    pc = loadPC(pc_path)
    _print("Running DBSCAN clustering")
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(pc[:,[0,1,2]])
    labels = clustering.labels_.reshape((-1, 1))
    pc_cluster = np.append(pc, labels, axis=1)
    _print("DBSCAN clustering complete")
    return pc_cluster
