import cv2

class WebcamInfo:
    """
    Provides access to webcam information, including width, height, and availability.

    Usage:
    webcam = WebcamInfo()
    if webcam.IsWebcamAvailable:
        print(f"Webcam resolution: {webcam.width}x{webcam.height}")
    print(f"Number of available webcams: {webcam.NumWebcamsAvailable}")
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._width = None
        self._height = None
        self._is_webcam_available = None
        self._num_webcams_available = None
        self._initialize_webcam()

    def _initialize_webcam(self):
        cap = cv2.VideoCapture(0)
        self._is_webcam_available = cap.isOpened()
        if self._is_webcam_available:
            ret, frame = cap.read()
            if ret:
                self._height, self._width = frame.shape[:2]
        cap.release()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def IsWebcamAvailable(self):
        return self._is_webcam_available


