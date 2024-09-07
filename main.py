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

'''Main code'''

pointCloud, options, parameters, paths = utils.select_json_file()

project_folder = utils.create_project_folders(paths['output'], pointCloud['e1'], pointCloud['e2'])

utils.start_code(options, parameters, pointCloud['e1'], pointCloud['e2'])

if options['transform_and_subsample']:
    XYZ_sub_folder = utils.create_folder(project_folder, 'XYZ_sub')
    e1_sub_path = utils.transform_subsample(paths['CloudComapare'], pointCloud['e1'], XYZ_sub_folder, parameters['spatial_distance'])
    e2_sub_path = utils.transform_subsample(paths['CloudComapare'], pointCloud['e2'], XYZ_sub_folder, parameters['spatial_distance'])
else:
    e1_sub_path = pointCloud['e1']
    e2_sub_path = pointCloud['e2']

if options['vegetation_filter']:
    print("\nData vegetation filtering")
    canupo_folder = utils.create_folder(project_folder, 'canupo')
    e1_canupo_path = cp.canupo_core(paths['CloudComapare'], e1_sub_path, paths['canupo_file'], canupo_folder)
    e2_canupo_path = cp.canupo_core(paths['CloudComapare'], e2_sub_path, paths['canupo_file'], canupo_folder)
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
    e1_reg_path, e2_reg_path = reg.ICP_CC(e1_reg_path, e2_reg_path, paths['CloudComapare'], parameters['ite_icp'])
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
    e1vse2_path = m3c2.m3c2_core(paths['CloudComapare'], e1_cut_path, e2_cut_path, paths['m3c2_param'], m3c2_folder, pointCloud['e1'], pointCloud['e2'])
else:
    e1vse2_path = e1_reg_path

if options['auto_parameters']:
    print("\nAuto DBSCAN parameters computation")
    dbscan_folder = utils.create_folder(project_folder, 'dbscan')
    density_points, spatial_distance = utils.density(e1vse2_path, paths['CloudComapare'], dbscan_folder)
    parameters['min_samples_rockfalls'] = utils.auto_param(density_points, parameters['eps_rockfalls'], safety_factor=0.9)

if options["rf_clustering"]:
    dbscan_folder = utils.create_folder(project_folder, 'dbscan')
    e1ve2_DBSCAN_path = rf.dbscan(dbscan_folder, e1vse2_path, parameters, options)
#
# ''' Volume Calculation '''
