import matplotlib.pyplot as plt
from bin.utils import loadPC, savePC, get_file_name, create_folder
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import os

def threshold_filter(threshold, e1e2_change_path):
    pc = loadPC(e1e2_change_path)
    if threshold < 0:
        pc_filtered = pc[pc['m3c2_diff'] < threshold]
    if threshold > 0:
        pc_filtered = pc[pc['m3c2_diff'] > threshold]
    return pc_filtered

def dbscan_core(diff_filter, eps, min_samples):
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(diff_filter[['x','y','z']])
    labels = clustering.labels_.reshape((-1, 1))
    labels_df = pd.DataFrame(labels, columns=['rockfall_label'])
    diff_cluster = pd.concat([diff_filter.reset_index(drop=True), labels_df], axis=1)
    diff_cluster = diff_cluster[diff_cluster['rockfall_label'] >= 0]
    # plt.scatter(diff_cluster[:, 0], diff_cluster[:, 2], c=diff_cluster[:, -1])
    # plt.show()
    return diff_cluster

def onebyone(dbscan_folder, diff_cluster, file_name):
    rockfalls_path = create_folder(dbscan_folder, 'rockfalls')
    rockfalls = max(diff_cluster[:, -1])
    for i in range(int(rockfalls)):
        rockfall = diff_cluster[diff_cluster[:, -1] == i]
        savePC(os.path.join(rockfalls_path, file_name + '_r' + str(i) + '.xyz'), rockfall)

def database(dbscan_folder, diff_cluster, file_name):
    database = pd.DataFrame(diff_cluster[:,[0,1,2,5,-1]], columns=['x', 'y', 'z', 'diff', 'label'])
    database = database.groupby(['label']).median()
    database.to_csv(os.path.join(dbscan_folder, file_name + '.csv'))

def dbscan(dbscan_folder, e1e2_change_path, parameters, options):
    pc_filtered = threshold_filter(parameters['diff_threshold'], e1e2_change_path)
    diff_cluster = dbscan_core(pc_filtered, parameters['eps_rockfalls'], parameters['min_samples_rockfalls'])
    file_name = get_file_name(e1e2_change_path)
    dbscan_path = savePC(os.path.join(dbscan_folder, file_name + '_dbscan.xyz'), diff_cluster)
    if options['rockfalls_1by1']:
        onebyone(dbscan_folder, diff_cluster, file_name)
    database(dbscan_folder, diff_cluster, file_name)
    return dbscan_path