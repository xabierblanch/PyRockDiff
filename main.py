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

#V2
#TODO PointCloud rotation
#TODO DensityComput -> DBSCAN

''' Import libraries '''
import bin.utils as utils
import bin.registration as reg
from bin.Boundary3D import main_2Dcut
import bin.m3c2 as m3c2
import bin.canupo as cp
import bin.cleaning as cl
import bin.clustering as rf
import bin.volume as vl

paths, options, parameters, file = utils.select_json_file()

project_folder = utils.create_project_folders(paths['output_folder'], paths['inputs']['epoch1'], paths['inputs']['epoch2'], file)

log_path = utils.create_log(project_folder)

utils.start_code(options, parameters, paths)

if options['preprocessing']['transform_and_subsample']:
    print(f"\nConverting PointClouds to XYZ and subsampling using a spatial resolution of {parameters['subsampling']['spatial_resolution']}")
    XYZ_sub_folder = utils.create_folder(project_folder, '1_XYZ_sub')
    e1_sub_path = utils.transform_subsample(paths['CloudCompare'], paths['inputs']['epoch1'], XYZ_sub_folder, parameters['subsampling']['spatial_resolution'])
    e2_sub_path = utils.transform_subsample(paths['CloudCompare'], paths['inputs']['epoch2'], XYZ_sub_folder, parameters['subsampling']['spatial_resolution'])
else:
    e1_sub_path = paths['inputs']['epoch1']
    e2_sub_path = paths['inputs']['epoch2']

if options['preprocessing']['vegetation_filter']:
    print("\nData vegetation filtering")
    canupo_folder = utils.create_folder(project_folder, '1.2_canupo')
    e1_canupo_path = cp.canupo_core(paths['CloudCompare'], e1_sub_path, paths['inputs']['canupo_file'], canupo_folder)
    e2_canupo_path = cp.canupo_core(paths['CloudCompare'], e2_sub_path, paths['inputs']['canupo_file'], canupo_folder)
else:
    e1_canupo_path = e1_sub_path
    e2_canupo_path = e2_sub_path

if options['preprocessing']['outlier_filter']:
    print("\nStatistical outlier removal")
    clean_folder = utils.create_folder(project_folder, '1.3_clean')
    e1_filtered_path = cl.outlier_filter(e1_canupo_path, parameters['outlier_filter']['neighbors'], parameters['outlier_filter']['std_ratio'], clean_folder)
    e2_filtered_path = cl.outlier_filter(e2_canupo_path, parameters['outlier_filter']['neighbors'], parameters['outlier_filter']['std_ratio'], clean_folder)
else:
    e1_filtered_path = e1_canupo_path
    e2_filtered_path = e2_canupo_path

if options['registration']['fgr']:
    print("\nFast Global Registration")
    registration_folder = utils.create_folder(project_folder, '2_registration')
    e1_reg_path, e2_reg_path = reg.FGR_reg(e1_filtered_path, e2_filtered_path, registration_folder, parameters['registration']['fgr_iterations'], parameters['subsampling']['spatial_resolution'])
else:
    e1_reg_path = e1_filtered_path
    e2_reg_path = e2_filtered_path

if options['registration']['icp']:
    print("\nICP registration")
    registration_folder = utils.create_folder(project_folder, '2_registration')
    e1_reg_path, e2_reg_path = reg.ICP_reg(e1_reg_path, e2_reg_path, paths['CloudCompare'], parameters['registration']['icp_iterations'])

if options['analysis']['roi_cropping']:
    print("\nROI clipping")
    e1_RegCut_path, e2_RegCut_path = main_2Dcut(e1_reg_path, e2_reg_path, registration_folder)
else:
    e1_cut_path = e1_reg_path
    e2_cut_path = e2_reg_path

if options['analysis']['m3c2_distance']:
    print("\nM3C2 Computation")
    m3c2_folder = utils.create_folder(project_folder, '3_change_detection')
    e1e2_change_path = m3c2.m3c2_core(paths['CloudCompare'], e1_cut_path, e2_cut_path, paths['inputs']['m3c2_file'], m3c2_folder, paths['inputs']['epoch1'], paths['inputs']['epoch2'], parameters['subsampling']['spatial_resolution'], parameters['clustering']['change_threshold'])
else:
    e1e2_change_path = paths['inputs']['m3c2_result']

if options['analysis']['auto_parameters_dbscan']:
    print("\nAuto DBSCAN parameters computation")
    dbscan_folder = utils.create_folder(project_folder, '4_dbscan')
    parameters['clustering']['min_samples'], parameters['clustering']['eps'] = utils.auto_param(parameters['subsampling']['spatial_resolution'],0.65)

if options['analysis']['dbscan_clustering']:
    print("\nClustering (DBSCAN)")
    dbscan_folder = utils.create_folder(project_folder, '4_dbscan')
    e1ve2_DBSCAN_path = rf.dbscan(dbscan_folder, e1e2_change_path, parameters['clustering'])
else:
    e1ve2_DBSCAN_path = paths['inputs']['m3c2_result']

if options['analysis']['volume_calculation'] and e1ve2_DBSCAN_path:
    print("\nComputing volumes")
    volume_folder = utils.create_folder(project_folder, '5_volume')
    volumes_db = vl.volume(e1ve2_DBSCAN_path, volume_folder)

elif options['analysis']['volume_calculation']:
    print("\nNo clusters detected — volume calculation skipped.")

print("\n" + "="*50)
print("The code has finished running successfully!")
print("\nResults are available at: \033[94m{}\033[0m".format(project_folder))
print("Log can be found at: \033[92m{}\033[0m".format(log_path))
print("="*50 + "\n")