import subprocess
import os
from bin.utils import get_file_name, _print, loadPC, savePC
import pandas as pd
def m3c2_core(CloudComapare_path, e1_path, e2_path, m3c2_param, m3c2_path, epoch1_path, epoch2_path):
    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)

    _print("Running M3C2 algorithm to compute the differences")

    output = os.path.join(m3c2_path, epoch1_name + "_vs_" + epoch2_name + "_m3c2.xyz")

    CC_m3c2_Command = [CloudComapare_path,
                      "-AUTO_SAVE", "OFF",
                      "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                      "-O", e1_path, "-OCTREE_NORMALS", "0.12", "-ORIENT", "MINUS_ORIGIN",
                      "-O", e2_path,
                      "-M3C2", m3c2_param,
                      "-CLEAR_NORMALS",
                      "-SAVE_CLOUDS", "FILE", f'"{e1_path}" "{e2_path}" "{output}"']

    subprocess.run(CC_m3c2_Command)

    _print("M3C2 algorithm completed successfully")
    _print("M3C2 adding file headings")

    pc = loadPC(output)
    pc_df = pc.dropna()
    pc_df.columns = ['x', 'y', 'z', 'change_significance', 'dist_uncertainty', 'm3c2_diff']
    savePC(output, pc_df)

    return output

