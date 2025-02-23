import numpy as np
import plotly.graph_objects as go
from pointwise_experiments import spherical_to_cartesian, create_sphere_surface
from scipy.spatial import ConvexHull
from stl import mesh

def rotate_points(x, y, z, theta):
    # rotate points about the z-axis
    x_rot = x * np.cos(theta) - y * np.sin(theta)
    y_rot = x * np.sin(theta) + y * np.cos(theta)
    z_rot = z
    return x_rot, y_rot, z_rot

def create_gomboc_points():
    # clelie_const = 1.0
    # bulge_max = 0.3
    # bulge_power = 4 # lower power risks being concave at the poles
    # bulge_offset = -0.5 # makes the bulge peak lower than the equator
    # r0 = 1.0
    # n_bulges_vertical = 1
    # n_bulges_horizontal = 3
    # n_rings = 16
    # n_points_per_ring = 50

    clelie_const = 1.0
    bulge_max = 0.25
    bulge_power = 2 # lower power risks being concave at the poles
    bulge_offset = -0.5 # makes the bulge peak lower than the equator
    r0 = 1.0
    n_bulges_vertical = 1
    n_bulges_horizontal = 3
    n_rings = 3
    n_points_per_ring = 20

    theta_offsets = np.linspace(0, 2*np.pi, n_rings, endpoint=False)
    # bulge_maxes = bulge_max * np.cos(np.linspace(0, n_bulges_horizontal*np.pi, n_rings, endpoint=False))**2
    bulge_maxes = bulge_max * (np.cos(np.linspace(0, 2*n_bulges_horizontal*np.pi, n_rings, endpoint=False)) +1)
    final_x = np.zeros((0,))
    final_y = np.zeros((0,))
    final_z = np.zeros((0,))
    for i, (theta_offset, bulge_max) in enumerate(zip(theta_offsets, bulge_maxes)):
        if(i == 0):
            theta = np.linspace(0, np.pi, n_points_per_ring)
        else:
            # skip the first and last point to avoid double counting
            theta = np.linspace(np.pi/n_points_per_ring, np.pi-np.pi/n_points_per_ring, n_points_per_ring-2)
        phi = clelie_const * theta
        theta += theta_offset
        r = r0+bulge_max*(np.sin(phi)**bulge_power)*(np.cos(n_bulges_vertical*(phi-bulge_offset))**bulge_power)
        x, y, z = spherical_to_cartesian(r, theta, phi)
        final_x = np.hstack((final_x, x))
        final_y = np.hstack((final_y, y))
        final_z = np.hstack((final_z, z))

    return final_x, final_y, final_z


    clelie_const = 1.0
    bulge_max = 0.2
    bulge_offset = -0.5 # makes the bulge peak lower than the equator
    bulge_power = 4 # lower power risks being concave at the poles
    r0 = 1.0
    n_bulges = 1

    theta1 = np.linspace(-np.pi/2, np.pi/2, 50)
    theta2 = np.linspace(np.pi/2, 3*np.pi/2, 50)
    theta = np.hstack((theta1, theta2))
    print(theta.shape)
    phi = clelie_const*theta
    theta[50:] += np.pi
    r = r0 + np.abs(bulge_max*np.sin(phi + np.pi/2+bulge_offset)**bulge_power)
    x = r * np.cos(theta) * np.cos(phi)
    y = r * np.cos(theta) * np.sin(phi)
    z = r * np.sin(theta)
    return x, y, z



if __name__ == "__main__":
    x, y, z = create_gomboc_points()
    x_sphere, y_sphere, z_sphere = create_sphere_surface()

    # Combine points into (n,3) array for ConvexHull
    points = np.column_stack((x, y, z))
    hull = ConvexHull(points)

    print(hull.vertices.shape)
    print(hull.vertices[:10])
    if(x.shape != hull.vertices.shape):
        print(f"Warning: point-cloud is not convex. hull.vertices.shape: {hull.vertices.shape}, x.shape: {x.shape}")
    else:
        print("Point-cloud is convex.")

    stl_mesh = mesh.Mesh(np.zeros(hull.nsimplex, dtype=mesh.Mesh.dtype))
    for i, simplex in enumerate(hull.simplices):
        for j in range(3):
            stl_mesh.vectors[i][j] = points[simplex[j]]
    folder_path = '/home/arthur/Projects/gomboc/gomboc_stl'
    stl_mesh.save(folder_path + '/gomboc.stl')

    # Get triangular faces of convex hull
    hull_x = points[:,0]
    hull_y = points[:,1] 
    hull_z = points[:,2]

    # Add convex hull surface to plot data
    hull_surface = go.Mesh3d(
        x=hull_x, y=hull_y, z=hull_z, # full set of points to choose from (including those that are not convex)
        i=hull.simplices[:,0], # indices of the first point of each triangle face 
        j=hull.simplices[:,1], # indices of the second point of each triangle face
        k=hull.simplices[:,2], # indices of the third point of each triangle face
        opacity=0.5
    )

    fig = go.Figure(data=[
        go.Scatter3d(x=x, y=y, z=z, mode='markers'),
        # go.Surface(x=x_sphere, y=y_sphere, z=z_sphere, opacity=0.5),
        hull_surface
    ])
    fig.show()
