import matplotlib.pyplot as plt
import numpy as np

# Recursive function to draw the Sierpinski triangle fractal
def draw_fractal(ax, vertices, level):
    
    # Create an array of triangle vertices
    points = np.array(vertices)
    
    # Draw the triangle (only if level is 0)
    if level == 0:
        ax.fill(points[:,0], points[:,1], 'k')
    else:
        # Compute the midpoints of each side of the triangle
        s = np.sum(points, axis=0) / 3.0
        
        # Create new vertices for the smaller triangle
        new_vertices = [points[0], points[1], s]
        
        # Recursive call for each smaller triangle
        draw_fractal(ax, new_vertices, level - 1)
        draw_fractal(ax, [points[0], s, points[2]], level - 1)
        draw_fractal(ax, [s, points[1], points[2]], level - 1)

fig, ax = plt.subplots()

# Initial triangle vertices (forming a rough approximation of the top of a spade)
vertices = [[0, 1], [-1, -1], [1, -1]]

# Draw the fractal
draw_fractal(ax, vertices, level=4)

# Set the aspect of the plot to be equal
ax.set_aspect('equal')

# Show the plot
plt.show()
