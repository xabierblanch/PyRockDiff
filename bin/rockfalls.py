import matplotlib.pyplot as plt

from bin.utils import loadPC, savePC, get_file_name
from sklearn.cluster import DBSCAN
import numpy as np
import os

threshold = 0.20
def threshold_filter(threshold, e1ve2_path):
    diff = loadPC(e1ve2_path)
    diff_filter = diff[diff[:,5] > threshold]
    return diff_filter

def dbscan_core(diff_filter, eps, min_samples):
    clustering = DBSCAN(eps=0.5, min_samples=14).fit(diff_filter[:,[0,1,2]])
    labels = clustering.labels_.reshape((-1, 1))
    diff_cluster = np.append(diff_filter, labels, axis=1)
    diff_cluster = diff_cluster[diff_cluster[:, -1] > 0]
    return diff_cluster

def dbscan(dbscan_folder, e1ve2_path, threshold, eps, min_samples):
    diff_filter = threshold_filter(threshold, e1ve2_path)
    diff_cluster = dbscan_core(diff_filter, eps, min_samples)
    file_name = get_file_name(e1ve2_path)
    dbscan_path = savePC(os.path.join(dbscan_folder, file_name + '_dbscan.xyz'), diff_cluster)
    return dbscan_path