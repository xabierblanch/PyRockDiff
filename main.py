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
from tkinter.filedialog import askopenfilename
import bin.utils as utils
import bin.registration as reg
from bin.Boundary3D import main_2Dcut
import open3d as o3d
import os

''' Parameters'''
PCload_visualization = False
voxel_size = 0.5  # downsampling for fast registration
ite = 4 # ICP iterations for fine adjustment

CloudComapare_path = "C:\Program Files\CloudCompare\cloudcompare.exe"
output_path = r"C:\Users\XBG\Desktop\test"

''' PointCloud Paths '''
#epoch1_path = askopenfilename(title = "Select PointCloud 1") #use open GUI
#epoch2_path = askopenfilename(title = "Select PointCloud 2") #use open GUI

epoch1_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Data_test\PCTest1.xyz" #use path file
epoch2_path = r"C:\Users\XBG\OneDrive - tu-dresden.de\XBG_Projects\2024_ICGC\Data_test\PCTest2.xyz" #use path file

utils.PCVisualization(epoch1_path, enable=PCload_visualization)
utils.PCVisualization(epoch2_path, enable=PCload_visualization)

''' Create folders '''
source_path, registration_path, m3c2_path = utils.folders(output_path, epoch1_path, epoch2_path)

'''Copy original PC'''
utils.copy_source(epoch1_path, epoch2_path, source_path)

''' Fast Registration '''
e1_Reg_path, e2_Reg_path = reg.fast_reg(voxel_size, epoch1_path, epoch2_path, registration_path)

''' ICP Registration '''
e1_Reg_path, e2_Reg_path = reg.ICP_CC(e1_Reg_path, e2_Reg_path, CloudComapare_path, ite)

'''' cut '''
e1_RegCut_path, e2_RegCut_path = main_2Dcut(e1_Reg_path, e2_Reg_path, registration_path)

''' M3C2 '''

