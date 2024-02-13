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
print('\nPyRockFall is running\n')

''' Software parameters'''



''' Workflow '''
#load PointClouds (The software assume xyz file with one attribute: [x,y,z,A1])

print('\nPointCloud #1')
pc1_path = askopenfilename(title = "Select PointCloud 1") #use open GUI
#pc1_path = 'path' #use path file
pc1 = utils.loadPC(pc1_path)

print('\nPointCloud #2')
pc2_path = askopenfilename(title = "Select PointCloud 2") #use open GUI
#pc2_path = 'path' #use path file
pc2 = utils.loadPC(pc2_path)

#Open CloudCompare for ICP aligment

#use cloudcompare (open windows software)
#use Open3D (automatically)
