import cv2
from screeninfo import get_monitors

class OpenCVWindowUtility:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenCVWindowUtility, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            monitor = get_monitors()[0]
            self.screen_width = monitor.width
            self.screen_height = monitor.height
            self._is_initialized = True

    def show_centered_window(self, window_name, image, window_width=None, window_height=None):
        if window_width is None or window_height is None:
            # Default window size to image size if not specified
            window_height, window_width = image.shape[:2]

        x_position = (self.screen_width - window_width) // 2
        y_position = (self.screen_height - window_height) // 2

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.moveWindow(window_name, x_position, y_position)
        cv2.imshow(window_name, image)

# Singleton Accessor
class Utility:
    @staticmethod
    def Instance():
        return OpenCVWindowUtility()

# # Usage example
# if __name__ == "__main__":
#     image = cv2.imread('path/to/your/image.jpg')
#     Utility.Instance().show_centered_window('Centered Image', image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
