import open3d as o3d
import copy
import numpy as np
import os
import subprocess
from bin.utils import get_file_name

def preprocess_point_cloud(pcd, voxel_size):
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp])

def prepare_dataset(voxel_size, pc1_path, pc2_path):
    print(":: Load two point clouds and disturb initial pose.")
    target = o3d.io.read_point_cloud(pc1_path)
    source = o3d.io.read_point_cloud(pc2_path)
    draw_registration_result(source, target, np.identity(4))
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)
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

def execute_fast_global_registration(source_down, target_down, source_fpfh,
                                     target_fpfh, voxel_size):
    distance_threshold = voxel_size * 0.5
    print(":: Apply fast global registration with distance threshold %.3f" \
            % distance_threshold)
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))
    return result


def fast_reg(voxel_size, epoch1_path, epoch2_path, registration_path):
    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)
    source, target, source_down, target_down, source_fpfh, target_fpfh = prepare_dataset(voxel_size, epoch1_path, epoch2_path)
    result_fast = execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
    o3d.io.write_point_cloud(os.path.join(registration_path, epoch1_name + '_reg.xyz'), target_down, format='auto',
                             write_ascii=True, compressed=False, print_progress=True)
    o3d.io.write_point_cloud(os.path.join(registration_path, epoch2_name + '_reg.xyz'), source_down, format='auto',
                             write_ascii=True, compressed=False, print_progress=True)
    return os.path.join(registration_path, epoch1_name + '_reg.xyz'), os.path.join(registration_path, epoch2_name + '_reg.xyz')

def ICP_CC(epoch1_path, epoch2_path, CloudComapare_path, ite):
    CC_ICP_Command = CloudComapare_path + ' -AUTO_SAVE OFF -C_EXPORT_FMT ASC -PREC 3 -o "' +\
                     epoch1_path +\
                     '" -o "' + \
                     epoch2_path +\
                     '" -ICP -REFERENCE_IS_FIRST -OVERLAP 99 -RANDOM_SAMPLING_LIMIT 1000000000 -FARTHEST_REMOVAL -SAVE_CLOUDS FILE ""' +\
                     epoch1_path +\
                     '" "' + \
                     epoch2_path +'""'
    for i in range(ite):
        subprocess.run(CC_ICP_Command)

    return epoch1_path, epoch2_path