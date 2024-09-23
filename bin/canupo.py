import subprocess
import os
from bin.utils import get_file_name, loadPC, savePC, _print
import numpy as np

def canupo_core(CloudComapare_path, epoch_path, canupo_file, canupo_folder):
    name = get_file_name(epoch_path)
    output_path = os.path.join(canupo_folder, name + "__canupo.xyz")

    _print(f'CANUPO Algorithm: {get_file_name(epoch_path)}')

    CC_canupo_Command = [CloudComapare_path,
                      "-AUTO_SAVE", "OFF",
                      "-C_EXPORT_FMT", "ASC", "-PREC", "3",
                      "-O", epoch_path,
                      "-CANUPO_CLASSIFY", canupo_file,
                      "-SAVE_CLOUDS", "FILE", f'"{output_path}"']

    subprocess.run(CC_canupo_Command)

    _print(f'CANUPO Algorithm: {get_file_name(epoch_path)} done')
    _print(f'CANUPO Algorithm: {get_file_name(output_path)} saved')

    epoch_filtered = loadPC(output_path, array=True)
    epoch_rock = epoch_filtered[epoch_filtered[:, 3] == 1]
    savePC(os.path.join(canupo_folder, name + '__rock.xyz'), epoch_rock)

    # epoch_vegetation = epoch_filtered[epoch_filtered[:, 3] == 2]
    #savePC(os.path.join(canupo_folder, name + '__veg.xyz'), epoch_vegetation)

    return os.path.join(canupo_folder, name + '__rock.xyz')

