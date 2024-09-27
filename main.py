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
#TODO Migrate from CloudCompare to other solutions
#TODO Compute the volume of the clusters
#TODO include verbososity option + Silent in cloudcompare
#TODO Create some log file
#TODO Move to Pandas to save/load files with headings
#TODO Function to check all paths before CC

''' Import libraries '''
import bin.utils as utils
import bin.registration as reg
from bin.Boundary3D import main_2Dcut
import bin.m3c2 as m3c2
import bin.canupo as cp
import bin.cleaning as cl
import bin.clustering as rf
import bin.volume as vl

pointCloud, options, parameters, paths, file = utils.select_json_file()

project_folder = utils.create_project_folders(paths['output'], pointCloud['e1'], pointCloud['e2'], file)

log_path = utils.create_log(project_folder)

utils.start_code(options, parameters, pointCloud, paths)

if options['transform_and_subsample']:
    XYZ_sub_folder = utils.create_folder(project_folder, '1_XYZ_sub')
    e1_sub_path = utils.transform_subsample(paths['CloudCompare'], pointCloud['e1'], XYZ_sub_folder, parameters['spatial_distance'])
    e2_sub_path = utils.transform_subsample(paths['CloudCompare'], pointCloud['e2'], XYZ_sub_folder, parameters['spatial_distance'])
else:
    e1_sub_path = pointCloud['e1']
    e2_sub_path = pointCloud['e2']

if options['vegetation_filter']:
    print("\nData vegetation filtering")
    canupo_folder = utils.create_folder(project_folder, '1.2_canupo')
    e1_canupo_path = cp.canupo_core(paths['CloudCompare'], e1_sub_path, paths['canupo_file'], canupo_folder)
    e2_canupo_path = cp.canupo_core(paths['CloudCompare'], e2_sub_path, paths['canupo_file'], canupo_folder)
else:
    e1_canupo_path = e1_sub_path
    e2_canupo_path = e2_sub_path

if options['cleaning_filtering']:
    clean_folder = utils.create_folder(project_folder, '1.3_clean')
    print("\nStatistical outlier removal")
    e1_filtered_path = cl.outlier_filter(e1_canupo_path, parameters['nb_neighbors_f'], parameters['std_ratio_f'], clean_folder)
    e2_filtered_path = cl.outlier_filter(e2_canupo_path, parameters['nb_neighbors_f'], parameters['std_ratio_f'], clean_folder)
else:
    e1_filtered_path = e1_canupo_path
    e2_filtered_path = e2_canupo_path

if options['fast_registration']:
    print("\nFast Global Registration")
    registration_folder = utils.create_folder(project_folder, '2_registration')
    e1_reg_path, e2_reg_path = reg.FGR_reg(parameters['voxel_size'], e1_filtered_path, e2_filtered_path, registration_folder, parameters['ite_FGR'])

if options['icp_registration']:
    print("\nICP registration")
    registration_folder = utils.create_folder(project_folder, '2_registration')
    e1_reg_path, e2_reg_path = reg.ICP_reg(e1_reg_path, e2_reg_path, paths['CloudCompare'], parameters['ite_ICP'])
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
    m3c2_folder = utils.create_folder(project_folder, '3_change_detection')
    e1e2_change_path = m3c2.m3c2_core(paths['CloudCompare'], e1_cut_path, e2_cut_path, paths['m3c2_param'], m3c2_folder, pointCloud['e1'], pointCloud['e2'])
else:
    e1e2_change_path = pointCloud['e1_e2']

if options['auto_parameters']:
    print("\nAuto DBSCAN parameters computation")
    dbscan_folder = utils.create_folder(project_folder, '4_dbscan')
    density_points, spatial_distance = utils.density(e1e2_change_path, paths['CloudCompare'], dbscan_folder)
    parameters['min_samples_rockfalls'] = utils.auto_param(density_points, parameters['eps_rockfalls'], safety_factor=0.9)

if options["rf_clustering"]:
    dbscan_folder = utils.create_folder(project_folder, '4_dbscan')
    e1ve2_DBSCAN_path = rf.dbscan(dbscan_folder, e1e2_change_path, parameters)
else:
    e1ve2_DBSCAN_path = pointCloud['e1_e2']

if options["rf_volume"]:
    volume_folder = utils.create_folder(project_folder, '5_volume')
    volumes_db = vl.volume(e1ve2_DBSCAN_path, volume_folder)

print("\n" + "="*50)
print("The code has finished running successfully!")
print("\nResults are available at: \033[94m{}\033[0m".format(project_folder))
print("Log can be found at: \033[92m{}\033[0m".format(log_path))
print("="*50 + "\n")