import sys
import cv2
import gettext
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal

from .paths import path

# Configure the gettext module for translation
translations = gettext.translation('camera_application', localedir=path.locales, languages=['en_US', 'pt_BR'])
translations.install()

_ = translations.gettext

class CameraWindow(QMainWindow):
    """A simple camera capture application with cropping functionality.

    Args:
        capture_width_cm (float): The desired width of the capture area in centimeters.
        capture_height_cm (float): The desired height of the capture area in centimeters.
        dpi (int): The desired DPI (dots per inch) for image capture.

    Attributes:
        capture_width_cm (float): The width of the capture area in centimeters.
        capture_height_cm (float): The height of the capture area in centimeters.
        dpi (int): The DPI (dots per inch) for image capture.
        timer (QTimer): Timer for updating the camera frame.
        camera (cv2.VideoCapture): Camera object for capturing frames.
        cameraLabel (QLabel): QLabel widget for displaying the camera feed.
        captureButton (QPushButton): QPushButton for capturing images.

    Example:
        To create and run the camera application:

        >>> app = QApplication(sys.argv)
        >>> camera_window = CameraWindow(capture_width_cm=3, capture_height_cm=4, dpi=300)
        >>> camera_window.show()
        >>> sys.exit(app.exec_())

    """
    imageCaptured = pyqtSignal(QImage)

    def __init__(self, capture_width_cm, capture_height_cm, dpi, parent=None):
        super(CameraWindow, self).__init__(parent)

        self.capture_width_cm = capture_width_cm
        self.capture_height_cm = capture_height_cm
        self.dpi = dpi
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(100)  # Update frame every 100 milliseconds

        self.camera = cv2.VideoCapture(0)  # Open the default camera (usually the built-in webcam)

        self.initUI()

    def initUI(self):
        """Initialize the user interface of the camera application."""
        self.setWindowTitle(_('Camera Capture Window'))
        self.setGeometry(100, 100, self.getCaptureWidthPixels(), self.getCaptureHeightPixels())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.cameraLabel = QLabel(self)
        self.cameraLabel.setGeometry(0, 0, self.getCaptureWidthPixels(), self.getCaptureHeightPixels())
        layout.addWidget(self.cameraLabel)

        self.captureButton = QPushButton(_('Capture'), self)
        self.captureButton.clicked.connect(self.captureImage)
        layout.addWidget(self.captureButton)

        self.closeButton = QPushButton(_('Close'), self)
        self.closeButton.clicked.connect(self.closeWindow)
        layout.addWidget(self.closeButton)

        self.central_widget.setLayout(layout)

    def updateFrame(self):
        """Update the camera frame and display it on the QLabel."""
        ret, frame = self.camera.read()

        if ret:
            # Get coordinates of the cropping rectangle
            rect_x = (frame.shape[1] - self.getCaptureWidthPixels()) // 2
            rect_y = (frame.shape[0] - self.getCaptureHeightPixels()) // 2
            rect_width = self.getCaptureWidthPixels()
            rect_height = self.getCaptureHeightPixels()

            # Crop the image based on the cropping rectangle
            cropped_image = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]

            # Convert the cropped image to the BGR format
            cropped_image_bgr = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR)

            # Create a QImage from the cropped BGR image
            height, width, channel = cropped_image_bgr.shape
            bytes_per_line = 3 * width
            q_image = QImage(cropped_image_bgr.data.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.cameraLabel.setPixmap(pixmap)

    def captureAndSaveImage(self):
        """Capture an image and save it as 'captured_image.jpg'."""
        ret, frame = self.camera.read()

        if ret:
            # Get coordinates of the cropping rectangle
            rect_x = (frame.shape[1] - self.getCaptureWidthPixels()) // 2
            rect_y = (frame.shape[0] - self.getCaptureHeightPixels()) // 2
            rect_width = self.getCaptureWidthPixels()
            rect_height = self.getCaptureHeightPixels()

            # Crop the image based on the cropping rectangle
            cropped_image = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]

            cv2.imwrite("captured_image.jpg", cropped_image)

    def captureImage(self):
        """Capture an image and emit it using the imageCaptured signal."""
        ret, frame = self.camera.read()

        if ret:
            # Get coordinates of the cropping rectangle
            rect_x = (frame.shape[1] - self.getCaptureWidthPixels()) // 2
            rect_y = (frame.shape[0] - self.getCaptureHeightPixels()) // 2
            rect_width = self.getCaptureWidthPixels()
            rect_height = self.getCaptureHeightPixels()

            # Crop the image based on the cropping rectangle
            cropped_image = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]

            # Convert the cropped image to the BGR format
            cropped_image_bgr = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR)

            # Create a QImage from the cropped BGR image
            height, width, channel = cropped_image_bgr.shape
            bytes_per_line = 3 * width
            q_image = QImage(cropped_image_bgr.data.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)

            # Emit the captured image using the imageCaptured signal
            self.imageCaptured.emit(q_image)

    def closeEvent(self, event):
        """Release the camera when the application is closed."""
        self.camera.release()
        event.accept()

    def closeWindow(self):
        """Close the camera window."""
        self.camera.release()
        self.hide()

    def getCaptureWidthPixels(self):
        """Calculate the capture width in pixels based on DPI."""
        return int((self.capture_width_cm * self.dpi) / 2.54)

    def getCaptureHeightPixels(self):
        """Calculate the capture height in pixels based on DPI."""
        return int((self.capture_height_cm * self.dpi) / 2.54)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    offset = 1.3
    camera_window = CameraWindow(capture_width_cm=3/offset, capture_height_cm=4/offset, dpi=300)
    camera_window.show()
    sys.exit(app.exec_())

