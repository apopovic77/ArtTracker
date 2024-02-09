import numpy as np

class Triangulation:
    def __init__(self, vertices):
        self.vertices = vertices  # List of vertex coordinates

    def is_ear(self, i_prev, i_curr, i_next, indices):
        """Check if the vertex at index i_curr is an ear."""
        p_prev, p, p_next = self.vertices[i_prev], self.vertices[i_curr], self.vertices[i_next]
        
        # Define is_point_in_triangle inside is_ear
        def is_point_in_triangle(p, a, b, c):
            # Function to check if point p is inside triangle formed by a, b, c
            def sign(p1, p2, p3):
                return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

            b1 = sign(p, a, b) < 0.0
            b2 = sign(p, b, c) < 0.0
            b3 = sign(p, c, a) < 0.0

            return b1 == b2 == b3
        
        # Loop over all vertices and check if any are inside the triangle
        for i in indices:
            if i != i_prev and i != i_curr and i != i_next:
                if is_point_in_triangle(self.vertices[i], p_prev, p, p_next):
                    return False
        return True

    def triangulate_concave_polygon(self):
        """Triangulate the polygon defined by self.vertices."""
        indices = list(range(len(self.vertices)))  # Indices of the vertex list
        triangles = []  # To store indices of vertices forming each triangle

        while len(indices) > 3:
            for i in range(len(indices)):
                i_prev, i_curr, i_next = indices[i-1], indices[i], indices[(i+1) % len(indices)]
                
                if self.is_ear(i_prev, i_curr, i_next, indices):
                    # Add the current triangle's vertex indices
                    triangles.append([i_prev, i_curr, i_next])
                    del indices[i]  # Remove the ear's vertex index
                    break  # Found an ear, so break to restart the loop

        # Add the last triangle
        triangles.append(indices)  # Remaining indices form the final triangle

        return triangles
    # # Example usage
    # vertices = [(0, 0), (2, 0), (2, 2), (1, 1), (0, 2)]  # A simple concave shape
    # triangles = triangulate_concave_polygon(vertices)
    # for tri in triangles:
    #     print(tri)
