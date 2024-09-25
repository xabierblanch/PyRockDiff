import numpy as np
import open3d as o3d
from pathlib import Path
import os
import shutil
import subprocess
import datetime
from sklearn.cluster import DBSCAN
import math
import time
import json
import pandas as pd
import logging

def create_log(project_folder):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%d%m%Y_%H%M")
    output_log = os.path.join(project_folder, f"{formatted_time}.log")

    logging.basicConfig(
        filename=output_log,
        encoding="utf-8",
        filemode="w",
        level=logging.INFO,
        format='%(message)s',
    )

    start_message = f"Log file created on: {current_time.strftime('%d/%m/%Y at %H:%M:%S')}"
    logging.info(start_message)

def start_code(options, parameters, e1_path, e2_path, project_folder):
    e1 = get_file_name(e1_path)
    e2 = get_file_name(e2_path)

    print('\n*****************************************************\n')
    print(f'PyRockDiff will automatically perform a 3D comparison'
          f' between the point cloud {e1} and the point cloud {e2}.\n'
          f'\nThe following functions are enabled:\n')

    for option in options:
        print(f'{option}: {options[option]}')

    print(f'\nAnd the following parameters will be used:\n')
    for parameter in parameters:
        print(f'{parameter}: {parameters[parameter]}')
    print('\n*****************************************************\n')

def loadPC(path, array=False):
    _print(f'File {get_file_name(path)}: Loading')
    get_file_name(path)

    if array==True:
        pc = np.loadtxt(path)
        _print(f'File {get_file_name(path)}: Loaded as NumPy array')
        return pc
    else:
        try:
            pc = pd.read_csv(path, sep=' ')
            _print(f'File {get_file_name(path)}: Loaded as DataFrame. Number of points: {pc.shape[0]} with {pc.shape[1]} columns')
            return pc
        except pd.errors.EmptyDataError:
            _print(f'File {get_file_name(path)} appears to be empty or cannot be read as CSV')
            return None
        except pd.errors.ParserError:
            _print(f'File {get_file_name(path)}: Not a typical CSV format, trying with NumPy')
            for skiprows in range (25):
                try:
                    pc = np.loadtxt(path, skiprows=skiprows)
                    _print(f'File {get_file_name(path)}: Loaded as NumPy array')
                    return pc
                except:
                    _print(f'Skipping line: {skiprows}, and trying to load the file again')

    _print(f'Failed to load the file: {get_file_name(path)}')
    return None

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
    file_name = file_name.split('__')[0]
    return file_name

def create_project_folders(output_path, epoch1_path, epoch2_path, file):
    timestamp = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)
    filename = input(f"Default folder name: {epoch1_name + '_to_' + epoch2_name}, do you want to modify it? (y/n):").strip().lower()
    if filename == 'y':
        include_timestamp = input(f"Do you want to include timestamp in the folder name? (y/n): ").strip().lower()
        if include_timestamp == 'y':
            project_path = os.path.join(output_path, timestamp + "_to_" + epoch1_name + '__' + epoch2_name)
        else:
            new_name = input("Write the new folder name:").strip()
            project_path = os.path.join(output_path, new_name)
    else:
        project_path = os.path.join(output_path, epoch1_name + '_to_' + epoch2_name)

    if os.path.exists(project_path):
        overwrite = input(f"The folder '{project_path}' already exists. Do you want to overwrite the contents? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("The folder will be created with a new timestamp to avoid overwriting.")
            project_path = os.path.join(output_path, f"{timestamp}__{epoch1_name}_to_{epoch2_name}")

    os.makedirs(project_path, exist_ok=True)
    shutil.copy(file, os.path.join(project_path, Path(file).name))
    print(f"Folder created at: {project_path}")

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

    if isinstance(pointcloud, pd.DataFrame):
        pointcloud.to_csv(path, index=False, float_format='%.3f', sep=' ')
    elif isinstance(pointcloud, np.ndarray):
        np.savetxt(path, pointcloud, fmt='%1.3f', delimiter=' ')
    else:
        raise ValueError("Unsupported data type. Pointcloud must be a pandas DataFrame or a NumPy ndarray.")

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

    return os.path.join(subsample_folder, get_file_name(path) + "_sub.xyz")

def density(path, CloudComapare_path, dbscan_folder):
    output_path = os.path.join(dbscan_folder, get_file_name(path) + "_density.xyz")
    radius = 0.25
    _print(f'Computing point density {get_file_name(path)}. Sphere radius: {radius} m')
    CC_DEN_Command = [CloudComapare_path,
                      "-AUTO_SAVE", "OFF",
                      "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                      "-O", path,
                      "-DENSITY", str(radius), "-TYPE", "KNN",
                      "-SAVE_CLOUDS", "FILE", f'"{output_path}"']

    subprocess.run(CC_DEN_Command)
    _print(f"Computing the median density points for ¨{get_file_name(path)}: Done")
    time.sleep(5)
    densPC = loadPC(output_path)
    num_points = densPC[:,6].mean()
    density_points = num_points/(math.pi*(radius**2))
    spatial_distance = math.sqrt(1/density_points)
    _print(f'Point cloud density: {density_points:.2f} points/m2')
    _print(f'Point cloud spatial distance: {spatial_distance:.3f} m')
    return density_points, spatial_distance

def auto_param(density_points, radius, safety_factor):
    area_circle = math.pi * (radius ** 2)
    min_points = math.ceil(density_points * area_circle * safety_factor)
    _print(f'DBSCAN parameters:')
    _print(f'DBSCAN eps: {radius:.2f}')
    _print(f'DBSCAN min_points: {min_points:.2f}')
    return min_points

def _print(message):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("[%d/%m/%Y - %H:%M]")
    full_message = f"{formatted_time} :: {message}"
    print(full_message)
    logging.info(full_message)

def transform_subsample(CloudComapare_path, path, data_folder, spatial_distance):

    output_path = os.path.join(data_folder, get_file_name(path) + ".xyz")
    _print(f'Converting to XYZ and subsampling {get_file_name(path)}. Spatial distance: {spatial_distance} cm')

    CC_TRA_Command = [CloudComapare_path,
                      "-AUTO_SAVE", "OFF",
                      "-O", path,
                      "-SS", "SPATIAL", str(spatial_distance),
                      "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                      "-REMOVE_ALL_SFS", "-REMOVE_RGB", "-REMOVE_NORMALS",
                      "-SAVE_CLOUDS", "FILE", f'"{output_path}"']

    subprocess.run(CC_TRA_Command)
    _print(f'Conversiond and subsampling {get_file_name(path)} completed')

    return output_path

def transform_file(CloudComapare_path, path, data_folder):
    output_path = os.path.join(data_folder, get_file_name(path) + ".xyz")

    CC_TRA_Command = [CloudComapare_path,
                      "-AUTO_SAVE", "OFF",
                      "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                      "-O", path,
                      "-SAVE_CLOUDS", "FILE", f'"{output_path}"']

    subprocess.run(CC_TRA_Command)
    time.sleep(5)
    pc_xyz = loadPC(output_path)
    pc_name = get_file_name(path)
    mask = np.all(pc_xyz != 0, axis=1)
    pc_xyz_filtered = pc_xyz[mask]
    savePC(os.path.join(data_folder,pc_name + '.xyz'), pc_xyz_filtered)
    return output_path

def dbscan_core(pc_path, eps, min_samples):
    pc = loadPC(pc_path)
    _print(f"Running DBSCAN clustering: {get_file_name(pc_path)}")
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(pc[:,[0,1,2]])
    labels = clustering.labels_.reshape((-1, 1))
    pc_cluster = np.append(pc, labels, axis=1)
    _print("DBSCAN clustering complete successfully")
    return pc_cluster

def select_json_file():
    print('\n*****************************************************\n')

    main_directory = os.getcwd()
    json_directory = os.path.join(main_directory, 'json_files')

    print(f"Looking for .json files in: {json_directory}")

    json_files = [file for file in os.listdir(json_directory) if file.endswith('.json')]

    print("Available JSON files:\n")
    for idx, file in enumerate(json_files):
        print(f"-> {idx + 1}. {file}")

    while True:
        try:
            selection = int(input(f"\nSelect the file number (1-{len(json_files)}): ")) - 1
            if 0 <= selection < len(json_files):
                file = os.path.join(json_directory, json_files[selection])

                with open(file, 'r') as f:
                    config = json.load(f)
                    pointCloud = config['pointCloud']
                    options = config['options']
                    parameters = config['parameters']
                    paths = config['paths']

                return pointCloud, options, parameters, paths, file

            else:
                print("Invalid selection. Please try again.")

        except ValueError:
            print("Invalid input. Please enter a number.")


