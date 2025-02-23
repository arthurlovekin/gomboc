import numpy as np
import plotly.graph_objects as go

def spherical_to_cartesian(radius, azimuth_angle, inclination_angle):
    """
    radius: Euclidean distance from the origin O to point P.
    azimuth_angle: signed angle from the x-axis (azimuth reference) to the orthogonal projection of the radial line segment OP on the x-y plane
    inclination_angle: signed angle from the z-axis (zenith reference) to the line segment OP.
    """
    x = radius * np.sin(inclination_angle) * np.cos(azimuth_angle)
    y = radius * np.sin(inclination_angle) * np.sin(azimuth_angle)
    z = radius * np.cos(inclination_angle)
    return x, y, z

def create_bulge_points(pts, bulge_max=0.2, bulge_offset=0.7, bulge_power=4, n_bulges=1):
    """
    create an array of points that can be added to a base radius in order to create a bulge
    This function
    1) is 0 at the start and end of the array (so that there is no bulge at the poles)
    2) allows you to control the maximum bulge amplitude (bulge_max) and the location of the bulge (bulge_offset)
    3) allows you to control the width of the bulge (bulge_power)
    """
    ### useful classes of functions:
    ## sin^2 (can't set the location of bulge and keep zeros at ends)
    #r = bulge_max*np.sin(pts)**bulge_power # lower power risks being concave at the poles

    ## sin(x)^a cos(x)^b (can set the location of bulge and keep zeros at ends easily)
    r = bulge_max*(np.sin(pts)**bulge_power)*(np.cos(n_bulges*(pts-bulge_offset))**bulge_power)

    ## Beta function (not implemented)
    return r

def create_clelie_points(clelie_const=1.0, theta_offset=0.0, bulge_max=0.2, bulge_offset=0.7, bulge_power=4, r0 = 1.0, n_points=50):
    theta = np.linspace(0, 2*np.pi, n_points)
    phi = clelie_const*theta
    theta += theta_offset
    r = r0 + create_bulge_points(pts=phi, bulge_max=0.2, bulge_offset=0.8, bulge_power=2, n_bulges=0.5, n_points=n_points)
    # r = r0 + bulge_max*np.sin(phi)**bulge_power # lower power risks being concave at the poles
    x, y, z = spherical_to_cartesian(r, theta, phi)
    return x, y, z


def create_sphere_surface(radius=1.0):
    theta_vals = np.linspace(0, 2*np.pi, 100)
    phi_vals = np.linspace(0, np.pi, 50)
    theta, phi = np.meshgrid(theta_vals, phi_vals)
    x, y, z = spherical_to_cartesian(radius, theta, phi)
    return x, y, z


if __name__ == "__main__":
    # Initial values
    clelie_const_init = 1.0
    theta_offset_init = 0.0
    x, y, z = create_clelie_points(clelie_const_init, theta_offset_init)
    sphere_x, sphere_y, sphere_z = create_sphere_surface()
    # x180, y180, z180 = create_clelie_curve(clelie_const_init, theta_offset_init + np.pi)
    x_test, y_test, z_test = spherical_to_cartesian(1, np.linspace(0, 2*np.pi, 100), np.ones((100,))*np.pi/2)
    fig = go.Figure(data=[
        go.Scatter3d(x=x, y=y, z=z, mode='markers'),
        # # go.Scatter3d(x=x180, y=y180, z=z180, mode='markers'),
        go.Surface(x=sphere_x, y=sphere_y, z=sphere_z, opacity=0.5),
        go.Scatter3d(x=x_test, y=y_test, z=z_test, mode='markers')
    ])
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-1.5, 1.5]),
            yaxis=dict(range=[-1.5, 1.5]),
            zaxis=dict(range=[-1.5, 1.5]),
            aspectmode='cube'  # Forces equal scaling for all axes
        )
    )

    # ## Pre-compute some curves so I can play with sliders 
    # # # (doesn't compute all N^2 possible combinations so it's a bit broken)
    # steps_c = []
    # for c_val in np.linspace(0, 4, 21):
    #     x_new, y_new, z_new = create_clelie_points(c_val, theta_offset_init)
    #     step = dict(
    #         method="update",
    #         args=[{"x": [x_new, sphere_x],
    #               "y": [y_new, sphere_y],
    #               "z": [z_new, sphere_z]}],
    #         label=f"{c_val:.1f}"
    #     )
    #     steps_c.append(step)

    # steps_d = []
    # for d_val in np.linspace(-np.pi, np.pi, 21):
    #     x_new, y_new, z_new = create_clelie_points(clelie_const_init, d_val)
    #     step = dict(
    #         method="update",
    #         args=[{"x": [x_new, sphere_x],
    #               "y": [y_new, sphere_y],
    #               "z": [z_new, sphere_z]}],
    #         label=f"{d_val:.1f}"
    #     )
    #     steps_d.append(step)

    # sliders = [
    #     dict(
    #         active=10,
    #         currentvalue={"prefix": "c: "},
    #         pad={"t": 70},
    #         steps=steps_c
    #     ),
    #     dict(
    #         active=10,
    #         currentvalue={"prefix": "d: "},
    #         pad={"t": 20},
    #         steps=steps_d
    #     )
    # ]

    # fig.update_layout(
    #     title='Edited Clelie Curves',
    #     autosize=True,
    #     sliders=sliders
    # )

    fig.show()
