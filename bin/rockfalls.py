import matplotlib.pyplot as plt
from bin.utils import loadPC, savePC, get_file_name, create_folder
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import os

def threshold_filter(threshold, e1ve2_path):
    diff = loadPC(e1ve2_path)
    diff_filter = diff[diff[:,5] > threshold]
    return diff_filter

def dbscan_core(diff_filter, eps, min_samples):
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(diff_filter[:,[0,1,2]])
    labels = clustering.labels_.reshape((-1, 1))
    diff_cluster = np.append(diff_filter, labels, axis=1)
    diff_cluster = diff_cluster[diff_cluster[:, -1] >= 0]
    plt.scatter(diff_cluster[:, 0], diff_cluster[:, 2], c=diff_cluster[:, -1])
    plt.show()
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
def dbscan(dbscan_folder, e1ve2_path, threshold, eps, min_samples, save_rockfalls):
    diff_filter = threshold_filter(threshold, e1ve2_path)
    diff_cluster = dbscan_core(diff_filter, eps, min_samples)
    file_name = get_file_name(e1ve2_path)
    dbscan_path = savePC(os.path.join(dbscan_folder, file_name + '_dbscan.xyz'), diff_cluster)
    if save_rockfalls:
        onebyone(dbscan_folder, diff_cluster, file_name)
    database(dbscan_folder, diff_cluster, file_name)
    return dbscan_path