import matplotlib.pyplot as plt

from bin.utils import loadPC
from sklearn.cluster import DBSCAN
import numpy as np

threshold = 0.20
def threshold_filter(threshold, diff):
    diff = loadPC(e1ve2_path)
    diff_filter = diff[diff[:,5] > threshold]
    return diff_filter

def dbscan(diff_filter, eps, min_samples):
    clustering = DBSCAN(eps=0.5, min_samples=14).fit(diff_filter[:,[0,1,2]])
    labels = clustering.labels_.reshape((-1, 1))
    diff_cluster = np.append(diff_filter, labels, axis=1)
    diff_cluster = diff_cluster[diff_cluster[:, -1] > 0]
    plt.scatter(diff_cluster[:, 0], diff_cluster[:, 2], c=diff_cluster[:, -1])
    plt.show()
    return clustering

diff_filter = threshold_filter(threshold, e1ve2_path)
dbscan(diff_filter, 0.5, 15)
