from stl import mesh
import numpy as np
import plotly.graph_objects as go

def check_face_supports_com(stl_mesh, com):
    """return a boolean np.array of size n_faces, that is True if the face supports the COM
    (only guaranteed to work for convex meshes)"""
    # (everything is in batches of size n_faces)
    edgeAB = stl_mesh.v1 - stl_mesh.v0 
    edgeBC = stl_mesh.v2 - stl_mesh.v1 
    edgeCA = stl_mesh.v0 - stl_mesh.v2 
    edge_normals_AB = np.cross(stl_mesh.normals, edgeAB)
    edge_normals_BC = np.cross(stl_mesh.normals, edgeBC)
    edge_normals_CA = np.cross(stl_mesh.normals, edgeCA)
    vectorAO = com - stl_mesh.v0 
    vectorBO = com - stl_mesh.v1 
    vectorCO = com - stl_mesh.v2 
    condition_AB = np.sum(vectorAO * edge_normals_AB, axis=1) >= 0 #row-wise dot product
    condition_BC = np.sum(vectorBO * edge_normals_BC, axis=1) >= 0 
    condition_CA = np.sum(vectorCO * edge_normals_CA, axis=1) >= 0
    condition_AO = np.sum(vectorAO * stl_mesh.normals, axis=1) <= 0 # outwards normal points away from COM
    face_supports_com = np.all(np.stack([condition_AB, condition_BC, condition_CA, condition_AO], axis=1), axis=1)
    # print(f"{np.sum(face_supports_com)}/{stl_mesh.data.shape[0]} Faces support the COM: {face_supports_com}")
    return face_supports_com

# Todo: use edge_idxs instead of face_idxs to avoid redundancy
def check_vertices_support_com(vertices, face_idxs, com):
    # Get an array of unique vertices
    n_vertices = vertices.shape[0]

    vertex_adjacency_list = [set() for _ in range(n_vertices)]
    for i, face in enumerate(face_idxs):
        for j in range(3):
            vertex_adjacency_list[face[j]].add(face_idxs[i, (j+1)%3])
            vertex_adjacency_list[face[j]].add(face_idxs[i, (j-1)%3])
    
    # # Check each vertex to see if it supports the COM
    # use the adjacency list to check all outgoung edges from vertex A
    vertex_supports_com = np.ones((n_vertices, ), dtype=np.bool) #(V,) # True if the vertex supports the COM
    for i, vertex in enumerate(vertices):
        vectorAO = com - vertex
        for other_vertex_idx in vertex_adjacency_list[i]:
            edgeAB = vertices[other_vertex_idx] - vertex
            vertex_supports_com[i] &= (np.dot(vectorAO, edgeAB) >= 0)
    
    return vertex_supports_com

def check_edges_support_com(stl_mesh,vertices, edge_idxs_vertices, edge_idxs_faces, face_idxs, com):
    n_edges = edge_idxs_vertices.shape[0]
    edge_supports_com = np.ones((n_edges, ), dtype=np.bool) #(E,) # True if the edge supports the COM

    # TODO: this is work that was already done when checking vertices
    for i, edge in enumerate(edge_idxs_vertices):
        edgeAB = vertices[edge[1]] - vertices[edge[0]]
        edgeBA = vertices[edge[0]] - vertices[edge[1]]
        vectorAO = com - vertices[edge[0]]
        vectorBO = com - vertices[edge[1]]
        edge_supports_com[i] &= (np.dot(vectorAO, edgeAB) >= 0)
        edge_supports_com[i] &= (np.dot(vectorBO, edgeBA) >= 0)
    
    # TODO: this is work that was already done when checking faces
    for i, edge in enumerate(edge_idxs_faces):
        face1 = stl_mesh[edge[0]]["vectors"] #(3,3)
        normal1 = stl_mesh[edge[0]]["normals"] #(3,)
        # get the vector that is oriented correctly
        edge_vector = vertices[edge[1]] - vertices[edge[0]]
        if ():
            edge_vector *= -1
        edge_normal1 = np.cross(normal1, edge_vector)
        edge_supports_com[i] &= (np.dot(vectorAO, edge_normal1) >= 0)

        
    return edge_supports_com

if __name__ == "__main__":
    file_path = r"/home/arthur/Projects/gomboc/stl/Cube.stl"
    # file_path = r"/home/arthur/Projects/gomboc/stl/right_triangular_pyramid.stl"
    # file_path = r"/home/arthur/Projects/gomboc/stl/gomboc_binary.stl"
    # file_path = r"/home/arthur/Projects/gomboc/stl/Moon.stl"
    # file_path = r"/home/arthur/Projects/gomboc/gomboc_stl/gomboc.stl"
    mesh2 = mesh.Mesh.from_file(file_path)
    volume, com, inertia = mesh2.get_mass_properties()
    face_supports_com = check_face_supports_com(mesh2, com)
    # print(f"{np.sum(face_supports_com)}/{mesh2.data.shape[0]} Faces support the COM: {face_supports_com}")
    
    # Get all unique vertices
    vertices_set = set()
    for face in mesh2.data:
        vertices_set.add(tuple(face["vectors"][0]))
        vertices_set.add(tuple(face["vectors"][1]))
        vertices_set.add(tuple(face["vectors"][2]))
    vertices = np.array(list(vertices_set), dtype=np.float32) #(N,3)
    n_vertices = vertices.shape[0]

    # For each face, find the indices of the three vertices that make up the face
    n_faces = mesh2.data.shape[0]
    face_idxs = np.zeros((n_faces, 3), dtype=np.int32) #(n_faces,3)
    for i, face in enumerate(mesh2.data):
        for j, vertex in enumerate(face["vectors"]):
            face_idxs[i, j] = np.where(np.all(vertices == vertex, axis=1))[0][0]
    
    vertices_support_com = check_vertices_support_com(vertices, face_idxs, com)
    # print(f"{np.sum(vertices_support_com)}/{n_vertices} vertices support the COM: {vertices_support_com}")

    # Get all unique edges. 
    edges_set_vertices = set()
    for i, face in enumerate(face_idxs):
        edges_set_vertices.add((min(face[0], face[1]), max(face[0], face[1])))
        edges_set_vertices.add((min(face[1], face[2]), max(face[1], face[2])))
        edges_set_vertices.add((min(face[2], face[0]), max(face[2], face[0])))
    edge_idxs_vertices = np.array(list(edges_set_vertices), dtype=np.int32) #(E,2)
    n_edges = edge_idxs_vertices.shape[0]
    print(f"{n_edges} edges should match n_faces + n_vertices - 2: {n_faces + n_vertices - 2}")

    # Tie each edge to the two faces that it belongs to
    # edges_to_faces = [[] for _ in range(n_edges)]

    # edges_support_com = check_edges_support_com(vertices, face_idxs, com)
    # print(f"{np.sum(edges_support_com)}/{n_edges} edges support the COM: {edges_support_com}")

    fig = go.Figure(data=[
        go.Scatter3d(
            x=[com[0]],
            y=[com[1]],
            z=[com[2]],
            mode="markers",
            marker=dict(size=10, color="black"),
        ),
        go.Scatter3d(
            x=vertices[:,0],
            y=vertices[:,1],
            z=vertices[:,2],
            mode="markers",
            marker=dict(
                size=8,
                color=["red" if support else "green" for support in vertices_support_com]
            )
        ),
        go.Mesh3d(
            x=vertices[:,0], 
            y=vertices[:,1], 
            z=vertices[:,2], 
            i=face_idxs[:,0], 
            j=face_idxs[:,1], 
            k=face_idxs[:,2],
            opacity=0.5,
            facecolor=["red" if support else "green" for support in face_supports_com],
            lighting=dict(
                ambient=0.3,
                diffuse=0.8,
                specular=0.5,
                roughness=0.5,
                fresnel=0.8
            ),
            lightposition=dict(
                x=100,
                y=100,
                z=100
            ),
            contour=dict(
                show=True,
                width=2
            )
        ),
    ])
    fig.update_layout(
        scene=dict(
            camera=dict(
                up=dict(x=0, y=1, z=0),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        )
    )
    fig.show()












