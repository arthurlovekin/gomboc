The popularized gomboc is not actually a gomboc, but such objects do exist. I want to find one, and 3d-print it.

Approaches:
1. Create a solid from a collection of half-planes (convex by construction). Then use gradient descent or other optimization to move the planes until they form a gomboc.
2. Brute force search across parameterizations of a solid. Intuitively, I think gombocs with no symmetry or radial symmetry (like a helix) are possible, but mirror symmetry makes it impossible.
3. Create a solid from a collection of points, each connected in triangles to their nearest neighbor. Use gradient descent or other optimization to move the points until they form a gomboc (note that convexity also has to be checked separately)

Testing framework:
The gomboc_checker takes in a stl file, and checks each face, edge, and vertex to see if a support vector through it intersects the center of mass (COM).
FOr the above methods, a more efficient loss function and verifier can probably be derived

Additional challenges:
- Make a gomboc that is entirely smooth ("1 face")
- Make a gomboc with the minimum number of polygonal faces
