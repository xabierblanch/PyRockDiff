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
import bin.canupo as canupo
import bin.rockfalls as rf
import open3d as o3d
import os

''' Parameters'''
transform_data = True
subsample = True
vegetation_filter = True
auto_aligment = False
cut_pointcloud = False
m3c2_dist = True
visualizations = False
save_rockfalls = False

spatial_distance = 0.05
voxel_size = 0.5                #downsampling for fast registration
ite = 4                         #ICP iterations for fine adjustment
diff_threshold = 0.20           #Threshold for filtering pointclouds (in cm)
eps = 1                         #DBSCAN: Max distance to search points
min_samples = 15                #DBSCAN: Min number of points to be cluster

''' Paths '''
CloudComapare_path = r"C:\Program Files\CloudCompare\cloudcompare.exe"
output_path = r"C:\Users\Xabier\Desktop\PyRockDiff_ICGCData"
m3c2_param = r'.\bin\m3c2_params.txt'
canupo_file = r'.\bin\canupo.prm'

''' PointCloud Paths '''
e1_path = r"C:\Users\Xabier\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\ICGC_Data\Apostols\190711_Apostols.xyz"
e2_path = r"C:\Users\Xabier\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\ICGC_Data\Apostols\240423_Apostols.xyz"

'''Main code'''
project_folder = utils.create_project_folders(output_path, e1_path, e2_path)
raw_folder = utils.create_folder(project_folder, 'raw')
e1_raw_path = utils.copy_source(e1_path, raw_folder)
e2_raw_path = utils.copy_source(e2_path, raw_folder)

if transform_data:
    data_folder = utils.create_folder(project_folder, 'XYZ')
    e1_xyz_path = utils.transform_files(e1_path, data_folder)
    e2_xyz_path = utils.transform_files(e2_path, data_folder)
else:
    e1_xyz_path = e1_raw_path
    e2_xyz_path = e2_raw_path

if subsample:
    subsample_folder = utils.create_folder(project_folder, 'subsample')
    e1_sub_path = utils.subsampling(e1_xyz_path, spatial_distance, CloudComapare_path, subsample_folder)
    e2_sub_path = utils.subsampling(e2_xyz_path, spatial_distance, CloudComapare_path, subsample_folder)
else:
    e1_sub_path = e1_xyz_path
    e2_sub_path = e2_xyz_path

if vegetation_filter:
    canupo_folder = utils.create_folder(project_folder, 'canupo')
    e1_filtered_path = canupo.canupo_core(CloudComapare_path, e1_sub_path, canupo_file, canupo_folder)
    e2_filtered_path = canupo.canupo_core(CloudComapare_path, e2_sub_path, canupo_file, canupo_folder)
else:
    e1_filtered_path = e1_sub_path
    e2_filtered_path = e2_sub_path

if auto_aligment == True:
    registration_folder = utils.create_folder(project_folder, 'registration')
    ''' Fast Registration '''
    e1_reg_path, e2_reg_path = reg.fast_reg(voxel_size, e1_filtered_path, e2_filtered_path, registration_folder)
    ''' ICP Registration '''
    e1_reg_path, e2_reg_path = reg.ICP_CC(e1_reg_path, e2_reg_path, CloudComapare_path, ite)
else:
    e1_reg_path = e1_filtered_path
    e2_reg_path = e2_filtered_path

if cut_pointcloud:
    e1_RegCut_path, e2_RegCut_path = main_2Dcut(e1_reg_path, e2_reg_path, registration_folder)
else:
    e1_cut_path = e1_reg_path
    e2_cut_path = e2_reg_path

if m3c2_dist:
    m3c2_folder = utils.create_folder(project_folder, 'm2c2')
    e1ve2_path = m3c2.m3c2_core(CloudComapare_path, e1_cut_path, e2_cut_path, m3c2_param, m3c2_folder, e1_path, e2_path)
#
# ''' Rockfall Extraction'''
# dbscan_folder = utils.create_folder(project_folder, 'dbscan')
#
# e1ve2_DBSCAN_path = rf.dbscan(dbscan_folder, e1ve2_path, diff_threshold, eps, min_samples, save_rockfalls)
#
# ''' Volume Calculation '''
