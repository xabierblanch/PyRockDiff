# Authors of the code: Xabier Blanch and Antonio Abellan

# This software is based on the methodologies developed in the doctoral theses of:
# Antonio Abellán (2010):
# Manuel Royán (2015): https://diposit.ub.edu/dspace/handle/2445/68667
# Xabier Blanch (2023): https://diposit.ub.edu/dspace/handle/2445/189157
# Developed in the RISKNAT research group of the University of Barcelona.

# External software and libraries are used. Special mention to:
# CloudCompare: https://www.danielgm.net/cc/ - used under GNU General Public License (GPL)
# py4dgeo: https://github.com/3dgeo-heidelberg/py4dgeo - used under MIT License
# Open3D: https://www.open3d.org/ - used under MIT License

# You are free to use this software for any purpose. This freedom is being defined by the GNU General Public License (GPL).
''' Import libraries '''
import numpy as np
from tkinter.filedialog import askopenfilename
import bin.utils as utils
import open3d as o3d
print('\nPyRockFall is running\n')

''' Software parameters'''
PCload_visualization = True


''' Workflow '''

print('\nLoading PointCloud #1')
#pc1_path = askopenfilename(title = "Select PointCloud 1") #use open GUI
pc1_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Data_test\PCTest1.xyz" #use path file
utils.PCVisualization(pc1_path, enable=PCload_visualization)

print('\nLoading PointCloud #2')
#pc2_path = askopenfilename(title = "Select PointCloud 2") #use open GUI
pc2_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Data_test\PCTest2.xyz" #use path file
utils.PCVisualization(pc2_path, enable=PCload_visualization)

#Open CloudCompare for ICP aligment


#pc2 = utils.loadPC(pc2_path)
#pc1 = utils.loadPC(pc1_path)