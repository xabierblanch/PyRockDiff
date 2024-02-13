import numpy as np
import matplotlib.pyplot as plt
def loadPC(path):
    try:
        pc = np.loadtxt(path)
        print(f'Number of points: {pc.shape[0]} points')
        print(f'Number of columns {pc.shape[1]} columns')
        if pc.shape[1] > 4:
            print('Number of atributes > 4 - We will use attribute number for 4 for visualization')
    except:
        print('ERROR: Check that the PointCloud file fits the requirements')
        print(f'ERROR: {path}')
    return pc

def PCVisualization(pc, enable=False):
    plt.scatter3
