import matplotlib.pyplot as plt

def plot(waypoints, result):
    """
    Построение 3D графика наикратчайшего пути.

    Parameters:
    waypoints: список точек
    result: список индексов точек
    """
    # Построение канваса
    ax = plt.axes(projection="3d")

    x=[waypoints[i-1]['lon'] for i in result['optimized_route']]
    y=[waypoints[i-1]['lat'] for i in result['optimized_route']]
    z=[waypoints[i-1]['alt'] for i in result['optimized_route']]

    # Построение линии
    ax.plot3D(x, y, z, 'red')

    # Построение точек
    ax.scatter3D(x, y, z, c=z, cmap='cividis');

    plt.show()