import numpy as np
import open3d as o3d
from pathlib import Path
import os
import shutil
import subprocess
import datetime
import pandas as pd


def loadPC(path):
    _print(f'Loading: {get_file_name(path)}. Some skiprows will be tested')
    get_file_name(path)
    for skiprows in range (25):
        try:
            pc = np.loadtxt(path, skiprows=skiprows)
            _print(f'File: {get_file_name(path)} loaded')
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
    _print(f"Saving transformed {pc_name} data in XYZ folder")
    np.savetxt(path, pointcloud, fmt='%1.3f', delimiter=' ')
    _print(f"Saving transformed {pc_name} completed")
    return path

def subsampling(path, spatial_distance, CloudComapare_path, subsample_folder):
    output_path = os.path.join(subsample_folder, get_file_name(path) + "_sub.txt")
    _print(f'Subsampling data. Spatial distance: {spatial_distance}')

    CC_SUB_Command = ('"' + CloudComapare_path + '" -AUTO_SAVE OFF -C_EXPORT_FMT ASC -PREC 3 -o "' + path + '" -SS SPATIAL '
                       + str(spatial_distance) + ' -SAVE_CLOUDS FILE "' + output_path + '"')
    subprocess.run(CC_SUB_Command)
    return output_path

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