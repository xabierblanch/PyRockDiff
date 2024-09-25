import matplotlib.pyplot as plt
from bin.utils import loadPC, savePC, get_file_name, create_folder, _print
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import os

def threshold_filter(threshold, e1e2_change_path):
    pc = loadPC(e1e2_change_path)
    _print(f'Filtering Point Cloud: Difference threshold: {threshold}')
    if threshold < 0:
        pc_filtered = pc[pc['m3c2_diff'] < threshold]
    if threshold > 0:
        pc_filtered = pc[pc['m3c2_diff'] > threshold]
    _print(f'Point Cloud after threshold filter: {pc_filtered.shape[0]} points')
    return pc_filtered

def dbscan_core(diff_filter, eps, min_samples):
    _print(f'Running DBSCAN algorithm for clustering the {diff_filter.shape[0]} points')
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(diff_filter[['x','y','z']])
    labels = clustering.labels_.reshape((-1, 1))
    labels_df = pd.DataFrame(labels, columns=['rockfall_label'])
    diff_cluster = pd.concat([diff_filter.reset_index(drop=True), labels_df], axis=1)
    diff_cluster = diff_cluster[diff_cluster['rockfall_label'] >= 0]
    # plt.scatter(diff_cluster[:, 0], diff_cluster[:, 2], c=diff_cluster[:, -1])
    # plt.show()
    _print(f'DBSCAN algorithm applied correctly: {diff_cluster.shape[0]} points in {diff_cluster["rockfall_label"].max()} clusters identified')
    return diff_cluster

def onebyone(dbscan_folder, diff_cluster, file_name):
    rockfalls_path = create_folder(dbscan_folder, 'rockfalls')
    rockfalls = max(diff_cluster[:, -1])
    for i in range(int(rockfalls)):
        rockfall = diff_cluster[diff_cluster[:, -1] == i]
        savePC(os.path.join(rockfalls_path, file_name + '_r' + str(i) + '.xyz'), rockfall)

def dbscan(dbscan_folder, e1e2_change_path, parameters, options):
    pc_filtered = threshold_filter(parameters['diff_threshold'], e1e2_change_path)
    diff_cluster = dbscan_core(pc_filtered, parameters['eps_rockfalls'], parameters['min_samples_rockfalls'])
    file_name = get_file_name(e1e2_change_path)
    dbscan_path = savePC(os.path.join(dbscan_folder, file_name + '__dbscan.xyz'), diff_cluster)
    # if options['cluster_db']:
    #     onebyone(dbscan_folder, diff_cluster, file_name)

    return dbscan_path, rockfall_db