import open3d as o3d
import copy
import numpy as np
import os
import subprocess
from bin.utils import get_file_name, _print
from pathlib import Path
import datetime

def preprocess_point_cloud(pcd, voxel_size):
    _print("Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    _print("Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    _print("Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def draw_registration_result(source, target, transformation, initial=False, enable=True):
    if enable:
        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        source_temp.transform(transformation)
        if initial:
            _print("Showing initial Point Cloud positions")
        else:
            _print("Showing Point Cloud registration result")
        o3d.visualization.draw_geometries([source_temp, target_temp])

def prepare_dataset(voxel_size, target_pc, source_pc):
    _print("Load two point clouds and disturb initial pose.")
    target = o3d.io.read_point_cloud(target_pc, format='xyz')
    source = o3d.io.read_point_cloud(source_pc, format='xyz')

    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    draw_registration_result(source_down, target_down, np.identity(4), initial=True, enable=True)

    return source, target, source_down, target_down, source_fpfh, target_fpfh

def execute_global_registration(source_down, target_down, source_fpfh,
                                target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    return result

def execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 0.5
    _print("Apply Fast Global Registration with distance threshold %.3f" % distance_threshold)
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))
    return result


def FGR_reg(voxel_size, e1_path, e2_path, registration_folder, ite):
    _print(f"Running FGR algorithm to do a fast registration - {ite} iterations will be executed")
    e1_name = get_file_name(e1_path)
    e2_name = get_file_name(e2_path)
    e1_path_out = os.path.join(registration_folder, e1_name + '__FGR.xyz')
    e2_path_out = os.path.join(registration_folder, e2_name + '__FGR.xyz')

    for i in range(ite):
        _print(f"Running FGR algorithm for fast registration (Iteration {i + 1} of {ite})")
        source, target, source_down, target_down, source_fpfh, target_fpfh = prepare_dataset(voxel_size, target_pc=e1_path, source_pc=e2_path)
        result_fast = execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
        source_reg = source.transform(result_fast.transformation)
        draw_registration_result(source_down.transform(result_fast.transformation), target_down, np.identity(4), enable=True)
        # draw_registration_result(target, source_reg, np.identity(4))

        o3d.io.write_point_cloud(e1_path_out, target, format='xyz',
                                 write_ascii=True, compressed=False)

        o3d.io.write_point_cloud(e2_path_out, source_reg, format='xyz',
                                 write_ascii=True, compressed=False)

        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%Hh%M")
        transformation_matrix_path = os.path.join(registration_folder, e2_name + f'__FGR_REGISTRATION_MATRIX_{formatted_date}_{formatted_time}.txt')
        np.savetxt(transformation_matrix_path, result_fast.transformation, fmt='%.6f')  # Guarda la matriz con 6 decimales

        e1_path = e1_path_out
        e2_path = e2_path_out
        _print(f"FGR algorithm - Iteration {i + 1} of {ite} completed successfully\n")

    return e1_path_out, e2_path_out

def ICP_reg(e1_path, e2_path, CloudComapare_path, ite):
    print("ICP Registration")
    _print(f"Running ICP algorithm to refine registration - {ite} iterations will be executed")

    e1_file = get_file_name(e1_path)
    e2_file = get_file_name(e2_path)
    e1_path_out = os.path.join(Path(e1_path).parent, e1_file + "__ICP.xyz")
    e2_path_out = os.path.join(Path(e2_path).parent, e2_file + "__ICP.xyz")

    for i in range(ite):
        _print(f"Running ICP algorithm to refine registration (Iteration {i + 1} of {ite})")
        CC_ICP_Command = [CloudComapare_path,
                          "-AUTO_SAVE", "OFF",
                          "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                          "-O", e1_path,
                          "-O", e2_path,
                          "-ICP", "-REFERENCE_IS_FIRST", "-OVERLAP", "100",
                          "-RANDOM_SAMPLING_LIMIT", "1000000000", "-FARTHEST_REMOVAL",
                          "-SAVE_CLOUDS", "FILE", f'"{e1_path_out}" "{e2_path_out}"']
        try:
            subprocess.run(CC_ICP_Command, check=True)
            _print(f"ICP algorithm - Iteration {i+1} of {ite} completed successfully")
        except subprocess.CalledProcessError as e:
            _print(f"ICP command failed with exit code {e.returncode}")

        e1_path = e1_path_out
        e2_path = e2_path_out

    return e1_path_out, e2_path_out