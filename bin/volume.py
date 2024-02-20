from bin.utils import loadPC
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

e1ve2_DBSCAN_path = r"C:\Users\XBG\Desktop\test\PCTest2_1848_vs_PCTest1_2135\dbscan\PCTest2_1848_vs_PCTest1_2135_m3c2_dbscan.xyz"
pc = loadPC(e1ve2_DBSCAN_path)

def centroide(coordinates):
    centroide = coordinates.mean()
    return centroide
def calculate_area(points):
    x1=points[0,0]
    x2=points[1,0]
    x3=points[2,0]
    z1=points[0,2]
    z2=points[1,2]
    z3=points[2,2]
    area = abs((x1*(z2-z3) + x2*(z3-z1) + x3*(z1-z2)) / 2)
    return area
def volume(rockfall):
    tri = Delaunay(rockfall[:,[0,2]])
    vol_total = []
    area_total = []
    for triangle in tri.simplices:
        points = rockfall[triangle]
        area = calculate_area(points)
        vol = area * points[:,5].mean()
        area_total.append(area)
        vol_total.append(vol)
    vol_rockfall = sum(vol_total)
    area_rockfall = sum(area_total)
    return vol_rockfall, area_rockfall
def visualize_rockfall(tri):
    plt.triplot(rockfall[:, 0], rockfall[:, 2], tri.simplices)
    plt.plot(rockfall[:, 0], rockfall[:, 2], 'o')

for i in range(int(pc[:,-1].max())):
    rockfall = pc[pc[:,-1]==i]
    num_points = rockfall.shape[0]
    std_dev = rockfall[:,5].std()
    centroideX = centroide(rockfall[:,0])
    centroideY = centroide(rockfall[:,1])
    centroideZ = centroide(rockfall[:,2])
    volume, area = volume(rockfall)





