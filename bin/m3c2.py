import os
from bin.utils import get_file_name, _print, loadPC, savePC, run_command

def m3c2_core(e1_path, e2_path, m3c2_path, paths, parameters, deformation):

    CloudComapare_path = paths['CloudCompare']
    m3c2_param = paths['inputs']['m3c2_file']
    epoch1_path = paths['inputs']['epoch1']
    epoch2_path = paths['inputs']['epoch2']
    spatial_resolution = parameters['subsampling']['spatial_resolution']

    if deformation:
        threshold = parameters['deformation']['change_threshold']
        auto_m3c2 = parameters['deformation']['auto_parameters_m3c2']
    else:
        threshold = parameters['rockfall']['change_threshold']
        auto_m3c2 = parameters['rockfall']['auto_parameters_m3c2']

    if auto_m3c2:
        _print("Using auto M3C2 parameters")
        m3c2_file = update_m3c2_config(m3c2_param, spatial_resolution, m3c2_path, deformation)
    else:
        _print("Using default M3C2 parameters")
        m3c2_file = m3c2_param

    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)

    _print("Running M3C2 algorithm to compute the differences")

    output = os.path.join(m3c2_path, epoch1_name + "_vs_" + epoch2_name + "__m3c2.xyz")

    CC_m3c2_Command = [CloudComapare_path,
                       "-VERBOSITY", "2", "-SILENT",
                       "-AUTO_SAVE", "OFF",
                       "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                       "-O", e2_path,
                       "-O", e1_path,
                       "-M3C2", m3c2_file,
                       "-SAVE_CLOUDS", "FILE", f'"{e2_path}" "{e1_path}" "{output}"']

    run_command(CC_m3c2_Command)
    _print("M3C2 algorithm completed successfully")
    _print("M3C2 adding file headings")

    pc = loadPC(output)
    pc.columns = ['x', 'y', 'z', 'normal_distance', 'change_significance', 'dist_uncertainty', 'm3c2_diff', 'nx', 'ny', 'nz']
    output = os.path.join(m3c2_path, epoch1_name + "_vs_" + epoch2_name + "__m3c2.xyz")
    savePC(output, pc)
    pc_filtered = threshold_filter(threshold, pc)
    filtered_path = savePC(os.path.join(m3c2_path, epoch1_name + "_vs_" + epoch2_name + "__threshold.xyz"), pc_filtered)

    return filtered_path, output

def threshold_filter(threshold, pc):
    _print(f'Filtering Point Cloud: Difference threshold: {threshold}')
    if threshold < 0:
        pc_filtered = pc[pc['m3c2_diff'] < threshold]
    if threshold > 0:
        pc_filtered = pc[pc['m3c2_diff'] > threshold]
    _print(f'Point Cloud after threshold filter: {pc_filtered.shape[0]} points')
    return pc_filtered

def update_m3c2_config(m3c2_param, spatial_resolution, m3c2_path, deformation):
    if deformation:
        normal_scale = round(spatial_resolution * 3, 2)
        NormalMinScale = round(spatial_resolution * 4, 2)
        NormalStep = round(spatial_resolution, 2)
        NormalMaxScale = round(spatial_resolution * 10, 2)
        search_scale = spatial_resolution * 8
        _print(f"New NormalScale: {normal_scale}")
        _print(f"New SearchScale: {search_scale}")

    else:
        normal_scale = round(spatial_resolution * 3, 2)
        NormalMinScale = round(spatial_resolution * 2, 2)
        NormalStep = round(spatial_resolution, 2)
        NormalMaxScale = round(spatial_resolution * 5, 2)
        search_scale = spatial_resolution * 4
        _print(f"New NormalScale: {normal_scale}")
        _print(f"New SearchScale: {search_scale}")

    with open(m3c2_param, 'r') as f:
        lines = f.readlines()

    param_map = {
        "NormalScale": normal_scale,
        "SearchScale": search_scale,
        "NormalMinScale": NormalMinScale,
        "NormalStep": NormalStep,
        "NormalMaxScale": NormalMaxScale
    }

    new_lines = []
    changes_made = 0

    for line in lines:
        key = line.split('=')[0].strip()
        if key in param_map:
            old_value = line.split('=')[1].strip()
            new_lines.append(f"{key}={param_map[key]}\n")
            _print(f"UPDATED: {key} = {old_value} → {param_map[key]}")
            changes_made += 1
        else:
            new_lines.append(line)

    if deformation:
        output = os.path.join(m3c2_path, "m3c2_auto_params.txt")
        with open(output, 'w') as f:
            f.writelines(new_lines)
    else:
        output = os.path.join(m3c2_path, "m3c2_auto_params.txt")
        with open(output, 'w') as f:
            f.writelines(new_lines)

    _print(f"Updated M3C2 config saved to: {output}")
    return output

