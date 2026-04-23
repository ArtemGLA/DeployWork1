import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
def plot(waypoints):

    fig = plt.figure()
    ax = plt.axes(projection="3d")

    x=[wp['lon'] for wp in waypoints]
    y=[wp['lat'] for wp in waypoints]
    z=[wp['alt'] for wp in waypoints]

    ax.plot3D(x, y, z, 'red')

    ax.scatter3D(x, y, z, c=z, cmap='cividis');

    plt.show()