from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel, QSizePolicy

class ImageDisplay(QLabel):
    def __init__(self):
        super().__init__()
        self._has_image = False
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    def set(self, filepath):
        self._has_image = True
        self._pixmap = QPixmap(filepath)
        self._resize()

    # Override
    def resizeEvent(self, event):
        if self._has_image:
            self._resize()

    # Scale the image properly
    def _resize(self):
        self.setPixmap(
            self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
