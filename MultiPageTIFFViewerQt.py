""" MultiPageTIFFViewerQt.py: PyQt TIFF image stack viewer widget with mouse zoom/pan and frame slider.
"""

import os.path
import numpy as np
try:
    from PyQt5.QtCore import Qt, pyqtSignal, QT_VERSION_STR
    from PyQt5.QtWidgets import QWidget, QSlider, QPushButton, QLabel, QGridLayout, QFileDialog, QProgressDialog
except ImportError:
    try:
        from PyQt4.QtCore import Qt, pyqtSignal, QT_VERSION_STR
        from PyQt4.QtGui import QWidget, QSlider, QPushButton, QLabel, QGridLayout, QFileDialog, QProgressDialog
    except ImportError:
        raise ImportError("MultiPageTIFFViewerQt: Requires PyQt5 or PyQt4.")
from ImageViewerQt import ImageViewerQt
import tiffcapture
import qimage2ndarray


__author__ = "Marcel Goldschen-Ohm <marcel.goldschen@gmail.com>"
__version__ = "0.9.0"


class MultiPageTIFFViewerQt(QWidget):
    """ Multi-page TIFF image stack viewer using tiffcapture (https://github.com/cdw/TiffCapture).

    Uses ImageViewerQt (https://github.com/marcel-goldschen-ohm/ImageViewerQt) to display the stack frames
    and handle mouse interaction (pan, zoom, click signals).

    Uses qimage2ndarray (https://github.com/hmeine/qimage2ndarray) to convert the format of stack frames
    from NumPy ndarray to QImage as requried by ImageViewerQt.

    Frame traversal via a slider and arrow buttons.
    """
    frameChanged = pyqtSignal([], [int])

    def __init__(self):
        QWidget.__init__(self)

        # Handle to the image stack tiffcapture object.
        self._tiffCaptureHandle = None
        self.currentFrameIndex = None

        # Image frame viewer.
        self.viewer = ImageViewerQt()

        # Slider and arrow buttons for frame traversal.
        self.frameSlider = QSlider(Qt.Horizontal)
        self.prevFrameButton = QPushButton("<")
        self.nextFrameButton = QPushButton(">")
        self.currentFrameLabel = QLabel()

        self.prevFrameButton.clicked.connect(self.prevFrame)
        self.nextFrameButton.clicked.connect(self.nextFrame)
        self.frameSlider.valueChanged.connect(self.showFrame)

        # Layout.
        grid = QGridLayout(self)
        grid.addWidget(self.currentFrameLabel, 0, 0, 1, 3)
        grid.addWidget(self.viewer, 1, 0, 1, 3)
        grid.addWidget(self.prevFrameButton, 2, 0)
        grid.addWidget(self.frameSlider, 2, 1)
        grid.addWidget(self.nextFrameButton, 2, 2)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(0)

    def hasImageStack(self):
        """ Return whether or not an image stack is currently loaded.
        """
        return self._tiffCaptureHandle is not None

    def clearImageStack(self):
        """ Clear the current image stack if it exists.
        """
        if self._tiffCaptureHandle is not None:
            self.viewer.clearImage()
            self._tiffCaptureHandle = None

    def setImageStack(self, tiffCaptureHandle):
        """ Set the scene's current TIFF image stack to the input TiffCapture object.
        Raises a RuntimeError if the input tiffCaptureHandle has type other than TiffCapture.
        :type tiffCaptureHandle: TiffCapture
        """
        if type(tiffCaptureHandle) is not tiffcapture.TiffCapture:
            raise RuntimeError("MultiPageTIFFViewerQt.setImageStack: Argument must be a TiffCapture object.")
        self._tiffCaptureHandle = tiffCaptureHandle
        self.showFrame(0)

    def loadImageStackFromFile(self, fileName=''):
        """ Load an image stack from file.
        Without any arguments, loadImageStackFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageStackFromFile(fileName) will attempt to load the specified file directly.
        """
        if len(fileName) == 0:
            if QT_VERSION_STR[0] == '4':
                fileName = QFileDialog.getOpenFileName(self, "Open TIFF stack file.")
            elif QT_VERSION_STR[0] == '5':
                fileName, dummy = QFileDialog.getOpenFileName(self, "Open TIFF stack file.")
        fileName = str(fileName)
        if len(fileName) and os.path.isfile(fileName):
            self._tiffCaptureHandle = tiffcapture.opentiff(fileName)
            self.showFrame(0)

    def numFrames(self):
        """ Return the number of image frames in the stack.
        """
        if self._tiffCaptureHandle is not None:
            # !!! tiffcapture has length=0 for a single page TIFF.
            # If our handle is valid, we'll assume we have at least one image.
            return max([1, self._tiffCaptureHandle.length])
        return 0

    def getAllFrames(self):
        """ Return the entire image stack as a NumPy ndarray.
        !!! This currently ONLY works for grayscale image stacks that can be represented as 3D arrays.
        !!! For large image stacks this can be time and memory hungry.
        """
        if self._tiffCaptureHandle is None:
            return None
        imageWidth = self._tiffCaptureHandle.shape[0]
        imageHeight = self._tiffCaptureHandle.shape[1]
        numFrames = self.numFrames()
        entireStackArray = np.empty((imageWidth, imageHeight, numFrames))
        progress = QProgressDialog(self)
        progress.setLabelText("Loading TIFF image stack...")
        progress.setRange(0, numFrames)
        progress.setValue(0)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        for i, frame in enumerate(self._tiffCaptureHandle):
            entireStackArray[:,:,i] = frame
            progress.setValue(i)
            if progress.wasCanceled():
                return None
        progress.close()
        return entireStackArray

    def getFrame(self, i=None):
        """ Return the i^th image frame as a NumPy ndarray.
        If i is None, return the current image frame.
        """
        if self._tiffCaptureHandle is None:
            return None
        if i is None:
            i = self.currentFrameIndex
        if (i is None) or (i < 0) or (i >= self.numFrames()):
            return None
        return self._tiffCaptureHandle.find_and_read(i)

    def showFrame(self, i=None):
        """ Display the i^th frame in the viewer.
        Also update the frame slider position and current frame text.
        """
        frame = self.getFrame(i)
        if frame is None:
            return
        # Convert frame ndarray to a QImage.
        qimage = qimage2ndarray.array2qimage(frame, normalize=True)
        self.viewer.setImage(qimage)
        self.currentFrameIndex = i
        # Update frame slider position (hide frame slider if we only have one image frame).
        numFrames = self.numFrames()
        if numFrames > 1:
            self.frameSlider.setRange(1, numFrames)
            self.frameSlider.setValue(i)
            self.frameSlider.show()
            self.prevFrameButton.show()
            self.nextFrameButton.show()
            self.currentFrameLabel.setText(str(i+1) + "/" + str(numFrames))
            self.currentFrameLabel.show()
        else:
            self.frameSlider.hide()
            self.prevFrameButton.hide()
            self.nextFrameButton.hide()
            self.currentFrameLabel.hide()
        self.frameChanged.emit()
        self.frameChanged[int].emit(i)

    def prevFrame(self):
        """ Show previous frame in stack.
        """
        self.showFrame(self.currentFrameIndex - 1)

    def nextFrame(self):
        """ Show next frame in stack.
        """
        self.showFrame(self.currentFrameIndex + 1)


if __name__ == '__main__':
    import sys
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        try:
            from PyQt4.QtGui import QApplication
        except ImportError:
            raise ImportError("ImageViewerQt: Requires PyQt5 or PyQt4.")
    print('MultiPageTIFFViewerQt: Using Qt ' + QT_VERSION_STR)

    # Create the application.
    app = QApplication(sys.argv)

    # Create a TIFF stack viewer and load an image stack file to display.
    stackViewer = MultiPageTIFFViewerQt()
    stackViewer.loadImageStackFromFile()  # Pops up file dialog.

    # Load entire stack into memory as a 3D NumPy ndarray.
    entireStackArray = stackViewer.getAllFrames()
    print(entireStackArray.shape)

    # Show viewer and run application.
    stackViewer.show()
    sys.exit(app.exec_())
