# Authors of the code: Xabier Blanch and Antonio Abellan

# This software is based on the methodologies developed in the doctoral theses of:
# Antonio Abellán (2010):
# Manuel Royán (2015): https://diposit.ub.edu/dspace/handle/2445/68667
# Xabier Blanch (2023): https://diposit.ub.edu/dspace/handle/2445/189157
# Developed in the RISKNAT research group of the University of Barcelona.

# External software and libraries are used. Special mention to:
# CloudCompare: https://www.danielgm.net/cc/ - used under GNU General Public License (GPL)
# py4dgeo: https://github.com/3dgeo-heidelberg/py4dgeo - used under MIT License
# Open3D: https://www.open3d.org/ - used under MIT License

# You are free to use this software for any purpose. This freedom is being defined by the GNU General Public License (GPL).
''' Import libraries '''
import numpy as np
from tkinter.filedialog import askopenfilename
import bin.utils as utils
import bin.ICP as ICP
import open3d as o3d
import subprocess
import os
import py4dgeo

print('\nPyRockFall is running\n')

''' Software parameters'''
PCload_visualization = False
CloudComapare_ICP = False
voxel_size = 0.25  # downsampling for ICP registration
ICP_reg = True
CloudComapare_path = "C:\Program Files\CloudCompare\cloudcompare.exe"
output_path = r"C:\Users\XBG\Desktop\test"

''' Loading ICP '''
print('\nLoading PointCloud #epoch 1')
#pc1_path = askopenfilename(title = "Select PointCloud 1") #use open GUI
pc1_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Data_test\PCTest1.xyz" #use path file
utils.PCVisualization(pc1_path, enable=PCload_visualization)

print('\nLoading PointCloud #epoch 2')
#pc2_path = askopenfilename(title = "Select PointCloud 2") #use open GUI
pc2_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Data_test\PCTest2.xyz" #use path file
utils.PCVisualization(pc2_path, enable=PCload_visualization)

''' Create folders '''
pc1_name, pc2_name, source_path, registration_path = utils.folders(output_path, pc1_path, pc2_path)
utils.copy_source(pc1_path, pc2_path, source_path)

''' ICP Registration '''
if ICP_reg:
    source, target, source_down, target_down, source_fpfh, target_fpfh = ICP.prepare_dataset(voxel_size, pc1_path, pc2_path)
    result_fast = ICP.execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
    o3d.io.write_point_cloud(os.path.join(registration_path, pc1_name + '_reg.xyz'), target_down, format='auto',
                             write_ascii=True, compressed=False, print_progress=True)
    o3d.io.write_point_cloud(os.path.join(registration_path, pc2_name + '_reg.xyz'), source_down, format='auto',
                             write_ascii=True, compressed=False, print_progress=True)

    epoch1 = py4dgeo.read_from_xyz(os.path.join(registration_path, pc1_name + '_reg.xyz'))
    epoch2 = py4dgeo.read_from_xyz(os.path.join(registration_path, pc2_name + '_reg.xyz'))
    trafo = py4dgeo.iterative_closest_point(epoch1, epoch2)
    epoch2.transform(trafo)
    epoch2.save(os.path.join(registration_path, pc2_name + '_reg.xyz'))

    CC_ICP_Command = CloudComapare_path + ' -AUTO_SAVE OFF -C_EXPORT_FMT ASC -PREC 3 -o "' +\
                     os.path.join(registration_path, pc1_name + '_reg.xyz') +\
                     '" -o "' +\
                     os.path.join(registration_path, pc2_name + '_reg.xyz') +\
                     '" -ICP -REFERENCE_IS_FIRST -OVERLAP 95 -RANDOM_SAMPLING_LIMIT 999999999 -FARTHEST_REMOVAL -SAVE_CLOUDS FILE ""' +\
                     os.path.join(registration_path, pc1_name + '_reg.xyz') +\
                     '" "' + \
                     os.path.join(registration_path, pc2_name + '_reg.xyz')+'""'

    #subprocess.run(CC_ICP_Command)


#ICP.draw_registration_result(source_down, target_down, result_fast.transformation)
o3d.io.write_point_cloud(os.path.join(registration_path,pc1_name+'_reg.xyz'), target_down, format='auto', write_ascii=True, compressed=False, print_progress=True)
o3d.io.write_point_cloud(os.path.join(registration_path,pc2_name+'_reg.xyz'), source_down, format='auto', write_ascii=True, compressed=False, print_progress=True)

'''' shape cut '''