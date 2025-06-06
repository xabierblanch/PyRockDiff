import subprocess
import os
from bin.utils import get_file_name, _print, loadPC, savePC
import pandas as pd
def m3c2_core(CloudComapare_path, e1_path, e2_path, m3c2_param, m3c2_path, epoch1_path, epoch2_path, spatial_resolution, threshold):
    update_m3c2_config(m3c2_param, spatial_resolution, output_path=None)

    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)

    _print("Running M3C2 algorithm to compute the differences")

    output = os.path.join(m3c2_path, epoch1_name + "_vs_" + epoch2_name + "__m3c2.xyz")

    CC_m3c2_Command = [CloudComapare_path,
                       "-VERBOSITY", "0", "-SILENT",
                       "-AUTO_SAVE", "OFF",
                       "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                       "-O", e1_path,
                       "-O", e2_path,
                       "-M3C2", m3c2_param,
                       "-SAVE_CLOUDS", "FILE", f'"{e1_path}" "{e2_path}" "{output}"']

    subprocess.run(CC_m3c2_Command)
    _print("M3C2 algorithm completed successfully")
    _print("M3C2 adding file headings")

    pc = loadPC(output)
    pc.columns = ['x', 'y', 'z', 'normal_distance', 'change_significance', 'dist_uncertainty', 'm3c2_diff', 'nx', 'ny', 'nz']
    output = os.path.join(m3c2_path, epoch1_name + "_vs_" + epoch2_name + "__m3c2_v2.xyz")
    savePC(output, pc)
    pc_filtered = threshold_filter(threshold, pc)
    filtered_path = savePC(os.path.join(m3c2_path, epoch1_name + "_vs_" + epoch2_name + "__threshold.xyz"), pc_filtered)

    return filtered_path

def threshold_filter(threshold, pc):
    _print(f'Filtering Point Cloud: Difference threshold: {threshold}')
    if threshold < 0:
        pc_filtered = pc[pc['m3c2_diff'] < threshold]
    if threshold > 0:
        pc_filtered = pc[pc['m3c2_diff'] > threshold]
    _print(f'Point Cloud after threshold filter: {pc_filtered.shape[0]} points')
    return pc_filtered

def update_m3c2_config(m3c2_param, spatial_resolution, output_path=None):
    normal_scale = spatial_resolution * 3
    normal_min_scale = spatial_resolution * 1
    normal_max_scale = spatial_resolution * 5
    normal_step = normal_min_scale/2
    search_scale = spatial_resolution * 3

    with open(m3c2_param, 'r') as f:
        lines = f.readlines()

    param_map = {
        "NormalScale": normal_scale,
        "NormalMinScale": normal_min_scale,
        "NormalMaxScale": normal_max_scale,
        "NormalStep": normal_step,
        "SearchScale": search_scale,
    }

    new_lines = []
    for line in lines:
        key = line.split('=')[0].strip()
        if key in param_map:
            new_lines.append(f"{key}={param_map[key]}\n")
        else:
            new_lines.append(line)

    if not output_path:
        output_path = m3c2_param  # overwrite original

    with open(output_path, 'w') as f:
        f.writelines(new_lines)

    print(f"Updated M3C2 config saved to: {output_path}")
