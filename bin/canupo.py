import subprocess
import os
from bin.utils import get_file_name, loadPC, savePC
import numpy as np

def canupo_core(CloudComapare_path, epoch_path, canupo_file, canupo_folder):
    name = get_file_name(epoch_path)
    epoch_output_path = os.path.join(canupo_folder, name + '_canupo.xyz')

    CC_canupo_Command = ('"' + CloudComapare_path + '" -AUTO_SAVE OFF -C_EXPORT_FMT ASC -PREC 3 -o "' +
                      epoch_path + '" -CANUPO_CLASSIFY "' + canupo_file + '" -SAVE_CLOUDS FILE "'
                      + epoch_output_path + '"')

    # subprocess.run(CC_canupo_Command)

    epoch_filtered = loadPC(epoch_output_path)
    epoch_rock = epoch_filtered[epoch_filtered[:, 3] == 1]
    epoch_vegetation = epoch_filtered[epoch_filtered[:, 3] == 2]
    # epoch_rock_xyz = epoch_rock[:, :3]  # Select columns 0, 1, 2
    # epoch_veg_xyz = epoch_vegetation[:, :3]
    savePC(os.path.join(canupo_folder, name + '_rock.xyz'), epoch_rock)
    savePC(os.path.join(canupo_folder, name + '_veg.xyz'), epoch_vegetation)

    return os.path.join(canupo_folder, name + '_rock.xyz')

