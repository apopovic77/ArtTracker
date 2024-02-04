import cv2
import numpy as np
from CaptureWebCamImage import WebCamImage

# Initialize global variables
src_points = []  # to store source points
dst_points = []  # to store destination points
transform_matrix = None  # to store transformation matrix
img = None  # to store the original image

combined_image = None

def click_event(event, x, y, flags, param):
    global transform_matrix, src_points, dst_points, img

    if event == cv2.EVENT_LBUTTONDOWN:
        # For selecting source and destination points
        if param['mode'] == 'select_points':
            if len(param['points']) < 4:  # Ensure only 4 points are selected
                param['points'].append((x, y))
                cv2.circle(param['img'], (x, y), 5, (0, 255, 0), -1)
                cv2.imshow(param['window_name'], param['img'])

                if len(param['points']) == 4:
                    cv2.waitKey(500)  # Small delay to show the last point
                    if param['window_name'] == 'source':
                        # Once source points are selected, proceed to select destination points
                        blank_image = np.zeros_like(img)
                        write_text(blank_image, "Now, select a point on the source image to see its position on the transformed image 1. TL 2. TR 3. BR 4. BL",10,50) 
                        draw_lines(blank_image)
                        select_points(blank_image, 'destination', dst_points, 'select_points')
                    elif param['window_name'] == 'destination':
                        # After destination points are selected, apply the transformation
                        apply_perspective_transform(img, src_points, dst_points)

        # For selecting a single point on the source image to transform and display on the transformed image
        elif param['mode'] == 'select_single_point':
            if transform_matrix is not None:
                # Adjust the point's position considering the source image might be resized
                # Assuming the source image is displayed at half size
                adjusted_x, adjusted_y = x * 2, y * 2

                # Transform the selected point
                transformed_point = transform_point(transform_matrix, (adjusted_x, adjusted_y))

                # Draw the point on the destination image
                draw_point_on_transformed_image(transformed_point)


def click_event2(event, x, y, flags, param):
    global transform_matrix, src_points, dst_points, img, combined_image

    # Check if we are within the left half of the combined image (source image area)
    if event == cv2.EVENT_LBUTTONDOWN and x < img.shape[1] // 2:
        # Adjust coordinates for the original scale of the source image
        original_x, original_y = x * 2, y * 2

        if transform_matrix is not None:
            # Transform the selected point
            transformed_point = transform_point(transform_matrix, (original_x, original_y))
            
            point_x, point_y = transformed_point[0] // 2, transformed_point[1] // 2
            cv2.circle(combined_image, (point_x - img.shape[1] // 2, point_y), 5, (0, 0, 255), -1)
            cv2.circle(combined_image, (point_x, point_y), 5, (0, 255, 255),1)



# def update_combined_image(selected_point=None):
#     global img, transform_matrix, combined_image
#     # Apply transformation to get the transformed image
#     transformed_img = cv2.warpPerspective(img, transform_matrix, (img.shape[1], img.shape[0]))
    
#     # Resize both images to half their size for side-by-side display
#     resized_src_image = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))
#     resized_transformed_image = cv2.resize(transformed_img, (transformed_img.shape[1] // 2, transformed_img.shape[0] // 2))
    
#     # If a point has been selected, draw it on the transformed image
#     if selected_point:
#         # Adjust point coordinates for the resized image
#         point_x, point_y = selected_point[0] // 2, selected_point[1] // 2
#         cv2.circle(resized_transformed_image, (point_x - img.shape[1] // 2, point_y), 5, (0, 0, 255), -1)
    
#     # Combine the images for side-by-side display
#     combined_image = np.hstack((resized_src_image, resized_transformed_image))
#     cv2.imshow("Combined Image", combined_image)

# def transform_point(matrix, point):
#     pt = np.array([point[0], point[1], 1], dtype="float32")
#     transformed_pt = np.dot(matrix, pt)
#     transformed_pt = transformed_pt / transformed_pt[2]
#     return (int(transformed_pt[0]), int(transformed_pt[1]))         

def select_points(image, window_name, points, mode):
    """
    Lets the user select points by clicking on the image.
    """
    cv2.namedWindow(window_name)
    cv2.imshow(window_name, image)
    
    cv2.setMouseCallback(window_name, click_event, {'img': image, 'window_name': window_name, 'points': points, 'mode': mode})
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def print_transform_details(src, dst, transform_matrix):
    # Convert numpy arrays to string in Python list format for pretty printing
    src_str = np.array2string(src, separator=', ').replace('\n', '\n' + ' ' * (len('src = np.array([') - 1))
    dst_str = np.array2string(dst, separator=', ').replace('\n', '\n' + ' ' * (len('dst = np.array([') - 1))
    matrix_str = np.array2string(transform_matrix, separator=', ').replace('\n', '\n' + ' ' * (len('transform_matrix = np.array([') - 1))
    
    # Print in Python code format
    print(f'src = np.array({src_str}, dtype=np.float32)')
    print(f'dst = np.array({dst_str}, dtype=np.float32)')
    print(f'transform_matrix = np.array({matrix_str}, dtype=np.float32)')


def apply_perspective_transform(image, src_points, dst_points):
    """
    Applies the perspective transformation and returns the transformation matrix.
    Also displays the transformed image alongside the source image.
    """
    global transform_matrix
    global combined_image
    src = np.float32(src_points)
    dst = np.float32(dst_points)
    transform_matrix = cv2.getPerspectiveTransform(src, dst)

    print_transform_details(src,dst, transform_matrix)





    transformed_image = cv2.warpPerspective(image, transform_matrix, (image.shape[1], image.shape[0]))
    
    # Resize source image to half its size for side-by-side display
    resized_src_image = cv2.resize(image, (image.shape[1] // 2, image.shape[0] // 2))
    
    # Resize transformed image to match the resized source image size for side-by-side display
    resized_transformed_image = cv2.resize(transformed_image, (image.shape[1] // 2, image.shape[0] // 2))
    
    # Combine images for side-by-side display
    combined_image = np.hstack((resized_src_image, resized_transformed_image))
    
    # Display the combined image
    cv2.imshow("Combined Image", combined_image)





    cv2.setMouseCallback("Combined Image", click_event2)
    

        # Example usage:
    # Assuming you have already calculated the transform_matrix
    # and you have a point (x, y) from the source image that you want to transform
    src_x, src_y = 100, 50  # Example source point
    transformed_x, transformed_y = get_transformed_point((src_x, src_y), transform_matrix)
    print(f"Transformed Point: ({transformed_x}, {transformed_y})")
 

    cv2.waitKey(0)
    cv2.destroyAllWindows()

   # Print the transformation matrix
    print("Transformation Matrix:")
    print(np.array_str(transform_matrix))
    print("\nTo use this matrix in another project, you can use the following code snippet:")
    print(f"transform_matrix = np.array({np.array_repr(transform_matrix)})")


def transform_point(matrix, point):
    """
    Transforms a single point using the transformation matrix.
    """
    pt = np.array([point[0], point[1], 1], dtype="float32")
    transformed_pt = np.dot(matrix, pt)
    transformed_pt = transformed_pt / transformed_pt[2]
    return (int(transformed_pt[0]), int(transformed_pt[1]))

def draw_point_on_transformed_image(point):
    global img, transform_matrix
    # Apply transformation to the full-size image
    transformed_img = cv2.warpPerspective(img, transform_matrix, (img.shape[1], img.shape[0]))
    # Draw the transformed point on the transformed image
    cv2.circle(transformed_img, point, 5, (0, 0, 255), -1)
    
    # Resize transformed image to match the resized source image size for side-by-side display
    resized_transformed_image = cv2.resize(transformed_img, (img.shape[1] // 2, img.shape[0] // 2))
    
    # Display the image with the point
    cv2.imshow("Transformed Image with Selected Point", resized_transformed_image)
    cv2.waitKey(1)  # Use cv2.waitKey(1) to refresh the window

def get_transformed_point(src_point, matrix):
    """
    Transforms a given point from the source image to its corresponding point
    on the warped image using the provided transformation matrix.

    Parameters:
    - src_point: A tuple (x, y) representing the point in the source image.
    - matrix: The transformation matrix obtained from the perspective transformation.

    Returns:
    - A tuple (x, y) representing the transformed point on the warped image.
    """
    # Convert the source point to homogeneous coordinates (x, y, 1)
    pt = np.array([src_point[0], src_point[1], 1], dtype="float32")
    
    # Apply the transformation matrix
    transformed_pt = np.dot(matrix, pt)
    
    # Convert back to Cartesian coordinates
    transformed_pt = transformed_pt / transformed_pt[2]
    
    return (int(transformed_pt[0]), int(transformed_pt[1]))


def write_text(destination, text, pos_x = 10, pos_y = 10):

    org = (pos_x, pos_y)  # Position at bottom left corner with a small margin
    font = cv2.FONT_HERSHEY_SIMPLEX  # Font style
    fontScale = 1  # Font scale
    color = (0, 255, 255)  # Text color in BGR (white)
    thickness = 2  # Text thickness
    lineType = cv2.LINE_AA  # Line type

    # Put text on the resized image
    cv2.putText(destination, text, org, font, fontScale, color, thickness, lineType)


def draw_lines(img):
        # Wait for the user to select a point on the source image for transformation
    scale = 1
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)

    # Drawing lines
    # For horizontal lines
    for i in range(1, 10):
        y = int(height * i / 10)
        cv2.line(img, (0, y), (width, y), (255, 255, 0), thickness=1)

    # For vertical lines
    for i in range(1, 10):
        x = int(width * i / 10)
        cv2.line(img, (x, 0), (x, height), (255, 255, 0), thickness=1)  

def main_workflow(img_path):
    global img
    img = cv2.imread(img_path)
    if img is None:
        print("Error loading image")
        return


    # #uncommet this if you want to capter an image from the webcam
    # path_to_save_dir = "/Users/apopovic/Downloads"
    # wcamimage = WebCamImage(path_to_save_dir)
    # path_to_final_image = wcamimage.Start()
    # print(f"Final saved image path: {path_to_final_image}")


    # Select source points on the original image
    draw_lines(img)
    write_text(img, "Select 4 points 1. TL 2. TR 3. BR 4. BL (MARK FLOOR)",10,50) 
    select_points(img, 'source', src_points, 'select_points')




if __name__ == "__main__":
    img_path = "/Users/apopovic/Downloads/saved_frame.jpg"  # Replace with the path to your image
    main_workflow(img_path)
