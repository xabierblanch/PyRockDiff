import subprocess
import os
from bin.utils import get_file_name
def m3c2_core(CloudComapare_path, e1_RegCut_path, e2_RegCut_path, m3c2_param, m3c2_path):
    epoch1_name = get_file_name(e1_RegCut_path)
    epoch2_name = get_file_name(e2_RegCut_path)

    output = os.path.join(m3c2_path, epoch1_name + '_vs_' + epoch2_name + '.xyz')

    CC_m3c2_Command = CloudComapare_path + ' -AUTO_SAVE OFF -C_EXPORT_FMT ASC -PREC 3 -O "' + \
                      e1_RegCut_path + \
                      '" -O "' + \
                      e2_RegCut_path + \
                      '" -M3C2 "' + m3c2_param + '" -SAVE_CLOUDS FILE ""' + e1_RegCut_path + '" "' + \
                      e2_RegCut_path + '" "' + \
                      output + '""'

    subprocess.run(CC_m3c2_Command)

    return output

