import cv2
import numpy as np

def draw_fractal(img, vertices, level):
    color = (255, 255, 255)  # white color

    if level == 0:
        cv2.polylines(img, [vertices.reshape((-1, 1, 2))], isClosed=True, color=color, thickness=2)
    else:
        s = np.mean(vertices[0:2], axis=0, dtype=np.int32)
        draw_fractal(img, np.array([vertices[0], s, vertices[2]], dtype=np.int32), level - 1)
        draw_fractal(img, np.array([s, vertices[1], (vertices[1] + vertices[2]) // 2], dtype=np.int32), level - 1)
        draw_fractal(img, np.array([vertices[2], (vertices[0] + vertices[2]) // 2, s], dtype=np.int32), level - 1)

# Create a black image
img = np.zeros((512, 512, 3), dtype=np.uint8)

# Define the initial triangle vertices
vertices = np.array([[256, 50], [50, 462], [462, 462]], dtype=np.int32)

# Draw the fractal
draw_fractal(img, vertices, level=4)

# Show the image
cv2.imshow('Fractal', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
