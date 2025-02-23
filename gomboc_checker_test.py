import numpy as np
from stl import mesh
import plotly.graph_objects as go

if __name__ == "__main__":
    # file_path = r"/home/arthur/Projects/gomboc/stl/Cube.stl"
    # file_path = r"/home/arthur/Projects/gomboc/stl/right_triangular_pyramid.stl"
    # file_path = r"/home/arthur/Projects/gomboc/stl/gomboc_binary.stl"
    file_path = r"/home/arthur/Projects/gomboc/stl/Moon.stl"

    mesh2 = mesh.Mesh.from_file(file_path)
    volume, com, inertia = mesh2.get_mass_properties()

    # Get an array of unique vertices
    vertices_set = set()
    for face in mesh2.data:
        vertices_set.add(tuple(face["vectors"][0]))
        vertices_set.add(tuple(face["vectors"][1]))
        vertices_set.add(tuple(face["vectors"][2]))
    vertices = np.array(list(vertices_set), dtype=np.float32) #(N,3)
    n_vertices = vertices.shape[0]

    ## For each face, find the indices of the three vertices that make up the face
    # (useful for plotting, and creating vertex adjacency list)
    n_faces = mesh2.data.shape[0]
    face_idxs = np.zeros((n_faces, 3), dtype=np.int32) #(n_faces,3)
    for i, face in enumerate(mesh2.data):
        for j, vertex in enumerate(face["vectors"]):
            face_idxs[i, j] = np.where(np.all(vertices == vertex, axis=1))[0][0]
    

    vertex_adjacency_list = [set() for _ in range(n_vertices)]
    for i, face in enumerate(face_idxs):
        for j in range(3):
            vertex_adjacency_list[face[j]].add(face_idxs[i, (j+1)%3])
            vertex_adjacency_list[face[j]].add(face_idxs[i, (j-1)%3])
    

    # # Check each vertex to see if it supports the COM
    # use the adjacency list to check all outgoung edges from vertex A
    vertex_supports_com = np.ones((n_vertices, ), dtype=np.bool) #(V,) # True if the vertex supports the COM
    for i, vertex in enumerate(vertices):
        edgeAO = com - vertex
        for other_vertex_idx in vertex_adjacency_list[i]:
            edgeAB = vertices[other_vertex_idx] - vertex
            vertex_supports_com[i] &= (np.dot(edgeAO, edgeAB) >= 0)

    # # TODO: Instead of storing vertex indices, I could just store a numpy array
    # # with the vertices themselves, or an array of the outgoing vectors
    # # outgoing_vectors: dict that maps each vertex index to an (X,3) array of outgoing vectors
    


    # # Get an array of unique edges 
    # # (order doesn't matter, so we sort indices to avoid duplicates)
    # edges_set_vertices = set()
    # for i, face in enumerate(face_idxs):
    #     edgeAB = face[0]
    # # Storing the edges as indices of vertices (without duplicates) is convenient 
    # # for plotting, storing the edges as indices of faces is convenient for checking
    # # which edges support the COM
    # n_edges = n_faces + n_vertices - 2 # Euler's formula
    # edge_vertex_idxs = np.zeros((n_edges, 2), dtype=np.int32) #(n_edges,2)
    # edge_face_idxs = np.zeros((n_edges, 2), dtype=np.int32) #(n_edges,2)
    # edge_idx = 0
    # for index_triplet in sorted(face_idxs):
    #     pass










