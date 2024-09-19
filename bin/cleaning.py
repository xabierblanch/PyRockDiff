import open3d as o3d
import os
from bin.utils import get_file_name, dbscan_core, savePC, _print

def dbscan_filter(pc_path, clean_folder, eps, min_samples):
    pc_cluster = dbscan_core(pc_path, eps, min_samples)
    pc_filtered = pc_cluster[pc_cluster[:, -1] >= 0]
    file_name = get_file_name(pc_path)
    output_path = savePC(os.path.join(clean_folder, file_name + '_dbscan.xyz'), pc_filtered)
    return output_path

def outlier_filter(pc_path, nb_neighbors, std_ratio, output_folder):
    file_name = get_file_name(pc_path)
    _print(f'Running statistical outlier filter {file_name}')
    target = o3d.io.read_point_cloud(pc_path, format='xyz')
    cl, ind = target.remove_statistical_outlier(nb_neighbors, std_ratio)
    _print("Statistical outlier filter done")
    output_path = os.path.join(output_folder, file_name + '_outlier.xyz')
    o3d.io.write_point_cloud(output_path, cl, format='xyz', write_ascii=True, compressed=False)
    _print(f"Saving {get_file_name(output_path)} completed successfully")
    return output_path
