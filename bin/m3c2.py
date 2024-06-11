import subprocess
import os
from bin.utils import get_file_name, _print
def m3c2_core(CloudComapare_path, e1_path, e2_path, m3c2_param, m3c2_path, epoch1_path, epoch2_path):
    epoch1_name = get_file_name(epoch1_path)
    epoch2_name = get_file_name(epoch2_path)

    _print("Running M3C2 algorithm to compute the differences")

    output = os.path.join(m3c2_path, epoch1_name + "_vs_" + epoch2_name + "_m3c2.xyz")

    CC_m3c2_Command = [CloudComapare_path,
                      "-AUTO_SAVE", "OFF",
                      "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                      "-O", e1_path, "-O", e2_path,
                      "-M3C2", m3c2_param,
                      "-SAVE_CLOUDS", "FILE", f'"{e1_path}" "{e2_path}" "{output}"']

    subprocess.run(CC_m3c2_Command)

    _print("M3C2 algorithm completed successfully")

    return output

