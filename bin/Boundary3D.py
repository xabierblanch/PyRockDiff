import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import os
import subprocess

epoch1_path = r"C:\Users\XBG\Desktop\test\PCTest1_vs_PCTest2\registration\PCTest1_reg.xyz"
epoch2_path =  r"C:\Users\XBG\Desktop\test\PCTest1_vs_PCTest2\registration\PCTest2_reg.xyz"
CloudComapare_path = "C:\Program Files\CloudCompare\cloudcompare.exe"

registration_path = r"C:\Users\XBG\Desktop\test\PCTest1_vs_PCTest2\registration"
e1_name = 'epoch1'
e2_name = 'epoch2'

epoch1 = np.loadtxt(epoch1_path)

hull  = ConvexHull(epoch1[:,[0,2]])
fig = plt.figure()
plt.scatter(epoch1[hull.vertices,0], epoch1[hull.vertices,2], s=10)
plt.scatter(epoch1[:,0], epoch1[:,2], c='r', s=0.001)
plt.show()

XY_list = []
sep = ' '
for point in hull.vertices:
    XY = str(epoch1[point,0]) + ' ' + str(epoch1[point,2])
    XY_list.append(XY)
n = len(XY_list)
XY_list = sep.join(XY_list)
dim = 'Y'

CC_ICP_Command = CloudComapare_path + ' -AUTO_SAVE OFF -C_EXPORT_FMT ASC -PREC 3 -o "' + \
                 epoch1_path + \
                 '" -o "' + \
                 epoch1_path + \
                 '" -CROP2D ' + dim + " " + str(n) + " " + XY_list +\
                 ' -SAVE_CLOUDS FILE ""' + \
                 os.path.join(registration_path, e1_name + '_reg_cut.xyz') + \
                 '" "' + \
                 os.path.join(registration_path, e2_name + '_reg_cut.xyz') + '""'

subprocess.run(CC_ICP_Command)
