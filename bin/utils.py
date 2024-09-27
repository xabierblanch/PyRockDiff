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
import webbrowser
import sys

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
    return output_log

def check_path(path, path_name, warning, is_required=True):
    warning_new = warning
    if os.path.exists(path):
        status = "\033[92mOk\033[0m"
        warning = False
    elif is_required:
        status = "\033[91mWarning: File not found\033[0m"
        warning= True
    else:
        status = "\033[93mNot found, but not required\033[0m"
        warning = False
    if warning_new:
        warning = True
    print(f"{path_name}: {status}")
    return warning

def start_code(options, parameters, pointCloud, paths):

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"

    print("\n" + "="*50 + "\n")
    print("\033[1mReading JSON file:\033[0m\n")

    requires_two_clouds = any([options["transform_and_subsample"], options["vegetation_filter"],
                               options["cleaning_filtering"], options["fast_registration"],
                               options["icp_registration"], options["roi_focus"], options["m3c2_dist"]])

    if requires_two_clouds:
        try:
            e1 = get_file_name(pointCloud['e1'])
        except:
            print('ERROR: Not e1 pointcloud')
        try:
            e2 = get_file_name(pointCloud['e2'])
        except:
            print('ERROR: Not e2 pointcloud')

        print(f'PyRockDiff will automatically perform a 3D comparison '
              f'between the point cloud: {BLUE}{e1}{RESET} and the point cloud: {BLUE}{e2}{RESET}')

    elif options["auto_parameters"] or options["rf_clustering"] or options["rf_volume"]:
        try:
            e1_e2 = get_file_name(pointCloud['e1_e2'])
        except:
            print('ERROR: Not e1_e2 pointcloud')
        print(f'PyRockDiff will process the precomputed comparison of two different epochs using the point cloud: {BLUE}{e1_e2}{RESET}')

    else:
        print("Invalid configuration in JSON. Please check the options.")

    print('\033[1m\nThe following functions are enabled:\033[0m\n')

    for option in options:
        if options[option]:
            print(f'{option}: {GREEN}{options[option]}{RESET}')
        else:
            print(f'{option}: {RED}{options[option]}{RESET}')

    print('\033[1m\nAnd the following parameters will be used:\033[0m\n')
    for parameter in parameters:
        print(f'{parameter}: {YELLOW}{parameters[parameter]}{RESET}')

    print('\033[1m\nFile Paths and PointClouds Verification:\033[0m\n')
    warning = False
    warning = check_path(paths["CloudCompare"], "CloudCompare", warning)
    warning = check_path(paths["output"], "output", warning)

    if requires_two_clouds:
        warning = check_path(pointCloud["e1"], "e1", warning)
        warning = check_path(pointCloud["e2"], "e2", warning)
        warning = check_path(pointCloud["e1_e2"], "e1_e2", warning, is_required=False)
    else:
        warning = check_path(pointCloud["e1"], "e1", warning, is_required=False)
        warning = check_path(pointCloud["e2"], "e2", warning, is_required=False)
        warning = check_path(pointCloud["e1_e2"], "e1_e2", warning)

    if options["m3c2_dist"]:
        warning = check_path(paths["m3c2_param"], "m3c2_param", warning)
    else:
        warning = check_path(paths["m3c2_param"], "m3c2_param", warning, is_required=False)

    if options["vegetation_filter"]:
        warning = check_path(paths["canupo_file"], "canupo_file", warning)
    else:
        warning = check_path(paths["canupo_file"], "canupo_file", warning, is_required=False)

    if warning:
        print("\n\033[91mWarning: One or more required paths were not found. Code will not run properly\033[0m")

    while True:
        user_response = input("\nDo you want to start the code with these parameters? (y/n): ").strip().lower()
        if user_response == "y":
            print("\n" + "=" * 50 + "\n")
            _print("Executing the code")
            break
        elif user_response == "n":
            print("\nOperation canceled. Exiting the program")
            sys.exit()
        else:
            print("\nInvalid input. Please enter 'y' or 'n'.")

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
    while True:
        filename = input(f"\nDefault folder name: {epoch1_name + '_to_' + epoch2_name}, do you want to modify it? (y/n):").strip().lower()
        if filename == 'y':
            while True:
                include_timestamp = input(f"\nDo you want to include timestamp in the folder name? (y/n): ").strip().lower()
                if include_timestamp == 'y':
                    project_path = os.path.join(output_path, timestamp + "_to_" + epoch1_name + '__' + epoch2_name)
                    break
                if include_timestamp == 'n':
                    new_name = input("\nWrite the new folder name:").strip()
                    project_path = os.path.join(output_path, new_name)
                    break
                else:
                    print("\nInvalid input. Please enter 'y' or 'n'")
            break
        if filename == "n":
            project_path = os.path.join(output_path, epoch1_name + '_to_' + epoch2_name)
            break
        else:
            print("\nInvalid input. Please enter 'y' or 'n'")

    if os.path.exists(project_path):
        while True:
            overwrite = input(f"\n\033[91mWarning:\033[0m The folder '\033[94m{project_path}\033[0m' already exists. Do you want to overwrite the contents? (y/n) (If not, an automatic timestamp will be added): ").strip().lower()
            if overwrite == 'n':
                print("\nThe folder will be created with a new timestamp to avoid overwriting.")
                project_path = os.path.join(output_path, f"{timestamp}__{epoch1_name}_to_{epoch2_name}")
                break
            if overwrite == 'y':
                print("\nThe files in the folder will be overwritten.")
                break
            else:
                print("\nInvalid input. Please enter 'y' or 'n'")

    os.makedirs(project_path, exist_ok=True)
    shutil.copy(file, os.path.join(project_path, Path(file).name))
    print(f"\nFolder created at: \033[94m{project_path}\033[0m\nThis folder will now be opened.")
    webbrowser.open(project_path)
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

def density(path, CloudCompare_path, dbscan_folder):
    output_path = os.path.join(dbscan_folder, get_file_name(path) + "__density.xyz")
    radius = 0.25
    _print(f'Computing point density {get_file_name(path)}. Sphere radius: {radius} m')
    CC_DEN_Command = [CloudCompare_path,
                      "-AUTO_SAVE", "OFF",
                      "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                      "-O", path,
                      "-DENSITY", str(radius), "-TYPE", "KNN",
                      "-SAVE_CLOUDS", "FILE", f'"{output_path}"']

    subprocess.run(CC_DEN_Command)
    _print(f"Computing the median density points for ¨{get_file_name(path)}: Done")
    time.sleep(5)
    densPC = loadPC(output_path, array=True)
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
    print("\n" + "="*50 + "\n")
    print("\033[1mJSON file (Parameters) selection\033[0m")  # Texto en negrita
    main_directory = os.getcwd()
    json_directory = os.path.join(main_directory, 'json_files')

    print("\nLooking for .json files in: \033[94m{}\033[0m".format(json_directory))

    json_files = [file for file in os.listdir(json_directory) if file.endswith('.json')]

    print("\nAvailable JSON files:\n")
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
                print("ERROR: Invalid selection. Please try again (check that JSON file is properly created")

        except ValueError:
            print("ERROR: Invalid input. Please enter a number.")


