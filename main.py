# Authors of the code: Xabier Blanch and Antonio Abellan

# This software is based on the methodologies developed in the doctoral theses of:
# Antonio Abellán (2010):
# Manuel Royán (2015): https://diposit.ub.edu/dspace/handle/2445/68667
# Xabier Blanch (2023): https://diposit.ub.edu/dspace/handle/2445/189157
# developed in the RISKNAT research group of the University of Barcelona.

# External Open Source software and libraries are used. Special mention to:
# CloudCompare: https://www.danielgm.net/cc/ - used under GNU General Public License (GPL)
# py4dgeo: https://github.com/3dgeo-heidelberg/py4dgeo - used under MIT License
# Open3D: https://www.open3d.org/ - used under MIT License

# You are free to use this software for any purpose. This freedom is being defined by the GNU General Public License (GPL).
#TODO Include DBSCAN filter after CANUPO and other Outliers filter.
#TODO Migrate from CloudCompare to other solutions
#TODO Compute the volume of the clusters
#TODO include verbososity option + Silent in cloudcompare
#TODO Create some log file

''' Import libraries '''
import bin.utils as utils
import bin.registration as reg
from bin.Boundary3D import main_2Dcut
import bin.m3c2 as m3c2
import bin.canupo as cp
import bin.cleaning as cl
import bin.rockfalls as rf

options = {
    'transform_and_subsample': True,    #Do the conversion to XYZ and subsampling together (save time)
    "vegetation_filter": True,         #Vegetation filter (CANUPO)
    "cleaning_filtering": True,        #Apply DBSCAN filtering and outliers filtering
    "fast_registration": True,         #Fast registration to approximate both Point Clouds
    "icp_registration": True,          #ICP registration
    "roi_focus": False,                 #Cut and remove areas out of ROI
    "m3c2_dist": True,                 #Compute the M3C2 differences
    "auto_parameters": True,
    "rf_clustering": True,
    "rockfalls_1by1": False}

parameters = {
    "spatial_distance": 0.05,         #Value [in m] for CloudCompare subsampling TODO: move to open3D
    "voxel_size": 0.25,               #downsampling for fast registration
    "ite_icp": 3,                     #ICP iterations for fine adjustment

    "diff_threshold": -0.05,           #Threshold for filtering pointclouds (in cm)
    "eps_rockfalls": 0.3,             #DBSCAN: Max distance to search points
    "min_samples_rockfalls": 15,      #DBSCAN: Min number of points to be cluster (Could be estimated automatically)

    "nb_neighbors_f" : 10,            #statistic filtering / https://www.open3d.org/docs/0.9.0/tutorial/Advanced/pointcloud_outlier_removal.html
    "std_ratio_f" : 1.5}                #statistic filtering

''' Paths '''
CloudComapare_path = r"C:\Program Files\CloudCompare\cloudcompare.exe"
output_path = r"C:\Users\Xabier\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Results"
m3c2_param = r'.\bin\m3c2_params.txt'
canupo_file = r'.\bin\canupo.prm'

''' PointCloud Paths '''
e1_path = r"C:\Users\Xabier\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\ICGC_Data\Apostols\190711_Apostols.xyz"
e2_path = r"C:\Users\Xabier\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\ICGC_Data\Apostols\240423_Apostols.xyz"

# e1_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Results\190711_Apostols_vs_240423_Apostols\clean\190711_Apostols_sub_rock_dbscan.xyz"
# e1_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Results\190711_Apostols_sub_rock_dbscan_vs_240423_Apostols_sub_rock_dbscan\m2c2\190711_Apostols_sub_rock_dbscan_vs_240423_Apostols_sub_rock_dbscan_m3c2.xyz"

'''Main code'''
project_folder = utils.create_project_folders(output_path, e1_path, e2_path)
utils.start_code(options, parameters, e1_path, e2_path)

if options['transform_and_subsample']:
    XYZ_sub_folder = utils.create_folder(project_folder, 'XYZ_sub')
    e1_sub_path = utils.transform_subsample(CloudComapare_path, e1_path, XYZ_sub_folder, parameters['spatial_distance'])
    e2_sub_path = utils.transform_subsample(CloudComapare_path, e2_path, XYZ_sub_folder, parameters['spatial_distance'])
else:
    e1_sub_path = e1_path
    e2_sub_path = e2_path

if options['vegetation_filter']:
    print("\nData vegetation filtering")
    canupo_folder = utils.create_folder(project_folder, 'canupo')
    e1_canupo_path = cp.canupo_core(CloudComapare_path, e1_sub_path, canupo_file, canupo_folder)
    e2_canupo_path = cp.canupo_core(CloudComapare_path, e2_sub_path, canupo_file, canupo_folder)
else:
    e1_canupo_path = e1_sub_path
    e2_canupo_path = e2_sub_path

if options['cleaning_filtering']:
    clean_folder = utils.create_folder(project_folder, 'clean')
    print("\nStatistical oulier removal")
    e1_filtered_path = cl.outlier_filter(e1_canupo_path, parameters['nb_neighbors_f'], parameters['std_ratio_f'])
    e2_filtered_path = cl.outlier_filter(e2_canupo_path, parameters['nb_neighbors_f'], parameters['std_ratio_f'])
else:
    e1_filtered_path = e1_canupo_path
    e2_filtered_path = e2_canupo_path

if options['fast_registration']:
    print("\nFast registration")
    registration_folder = utils.create_folder(project_folder, 'registration')
    e1_reg_path, e2_reg_path = reg.fast_reg(parameters['voxel_size'], e1_filtered_path, e2_filtered_path, registration_folder)
    e1_reg_path, e2_reg_path = reg.fast_reg(parameters['voxel_size'], e1_reg_path, e2_reg_path, registration_folder)

if options['icp_registration']:
    print("\nICP registration")
    registration_folder = utils.create_folder(project_folder, 'registration')
    e1_reg_path, e2_reg_path = reg.ICP_CC(e1_reg_path, e2_reg_path, CloudComapare_path, parameters['ite_icp'])
else:
    e1_reg_path = e1_filtered_path
    e2_reg_path = e2_filtered_path

if options['roi_focus']:
    print("\nROI clipping")
    e1_RegCut_path, e2_RegCut_path = main_2Dcut(e1_reg_path, e2_reg_path, registration_folder)
else:
    e1_cut_path = e1_reg_path
    e2_cut_path = e2_reg_path

if options['m3c2_dist']:
    print("\nM3C2 Computation")
    m3c2_folder = utils.create_folder(project_folder, 'm2c2')
    e1vse2_path = m3c2.m3c2_core(CloudComapare_path, e1_cut_path, e2_cut_path, m3c2_param, m3c2_folder, e1_path, e2_path)
else:
    e1vse2_path = e1_reg_path

if options['auto_parameters']:
    print("\nAuto DBSCAN parameters computation")
    dbscan_folder = utils.create_folder(project_folder, 'dbscan')
    density_points, spatial_distance = utils.density(e1vse2_path, CloudComapare_path, dbscan_folder)
    parameters['min_samples_rockfalls'] = utils.auto_param(density_points, parameters['eps_rockfalls'], safety_factor=0.9)

if options["rf_clustering"]:
    dbscan_folder = utils.create_folder(project_folder, 'dbscan')
    e1ve2_DBSCAN_path = rf.dbscan(dbscan_folder, e1vse2_path, parameters, options)
#
# ''' Volume Calculation '''
