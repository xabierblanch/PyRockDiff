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
from tkinter.filedialog import askopenfilename
import bin.utils as utils
import bin.registration as reg
from bin.Boundary3D import main_2Dcut
import bin.m3c2 as m3c2
import bin.rockfalls as rf
import open3d as o3d
import os

''' Parameters'''
PCload_visualization = False
auto_aligment = True
visualizations = True
voxel_size = 0.5                #downsampling for fast registration
ite = 4                         #ICP iterations for fine adjustment
diff_threshold = 0.05           #Threshold for filtering pointclouds (in cm)
eps = 0.10                      #DBSCAN: Max distance to search points
min_samples = 20                #DBSCAN: Min number of points to be cluster

''' Paths '''
CloudComapare_path = r"C:\Program Files\CloudCompare\cloudcompare.exe"
output_path = r"C:\Users\XBG\Desktop\test"
m3c2_param = r'C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\PyRockFall_PointClouds\bin\m3c2_params.txt'

''' PointCloud Paths '''
#epoch1_path = askopenfilename(title = "Select PointCloud 1") #use open GUI
#epoch2_path = askopenfilename(title = "Select PointCloud 2") #use open GUI
epoch1_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Data_test\PCTest2_1848.xyz"
epoch2_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Data_test\PCTest1_2135.xyz"

utils.PCVisualization(epoch1_path, enable=PCload_visualization)
utils.PCVisualization(epoch2_path, enable=PCload_visualization)

''' Create folders '''
project_folder = utils.create_project_folders(output_path, epoch1_path, epoch2_path)
raw_folder = utils.create_folder(project_folder, 'raw')
registration_folder = utils.create_folder(project_folder, 'registration')
m3c2_folder = utils.create_folder(project_folder, 'm2c2')
dbscan_folder = utils.create_folder(project_folder, 'dbscan')

'''Copy original PC'''
utils.copy_source(epoch1_path, epoch2_path, raw_folder)

if auto_aligment == True:
    ''' Fast Registration '''
    e1_Reg_path, e2_Reg_path = reg.fast_reg(voxel_size, epoch1_path, epoch2_path, registration_folder)
    ''' ICP Registration '''
    e1_Reg_path, e2_Reg_path = reg.ICP_CC(e1_Reg_path, e2_Reg_path, CloudComapare_path, ite)

else:
    e1_Reg_path = epoch1_path
    e2_Reg_path = epoch2_path

'''' cut '''
e1_RegCut_path, e2_RegCut_path = main_2Dcut(e1_Reg_path, e2_Reg_path, registration_folder)

''' M3C2 '''
e1ve2_path = m3c2.m3c2_core(CloudComapare_path, e1_RegCut_path, e2_RegCut_path, m3c2_param, m3c2_folder, epoch1_path, epoch2_path)

''' Rockfall Extraction'''
e1ve2_DBSCAN_path = rf.dbscan(dbscan_folder, e1ve2_path, diff_threshold, eps, min_samples)

''' Volume Calculation '''