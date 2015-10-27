# MultiPageTIFFViewerPyQt

A [PyQt](https://www.riverbankcomputing.com/software/pyqt/intro) (version 4 or 5) multi-page TIFF image stack viewer widget with mouse zoom and pan. The TIFF stack is loaded using [TiffCapture](https://github.com/cdw/TiffCapture), and the current stack frame is displayed using [ImageViewerPyQt](https://github.com/marcel-goldschen-ohm/ImageViewerPyQt) after converting the frame data format from a [NumPy](http://www.numpy.org) *ndarray* to *QImage* using [qimage2ndarray](https://github.com/hmeine/qimage2ndarray). Mouse interaction including zooming, panning and clicking is as described for [ImageViewerPyQt](https://github.com/marcel-goldschen-ohm/ImageViewerPyQt). A slider with arrow buttons allows traversal over the stack frames.

[TiffCapture](https://github.com/cdw/TiffCapture) only reads a single frame into memory at a time (the displayed frame), thus providing very fast load times even for large image stacks by eliminating the need to load the entire stack into memory first. In case you do need the entire stack in memory (e.g. for perfomring operations such as z projections), the getAllFrames() method reads the entire stack into memory as a [NumPy](http://www.numpy.org) *ndarray*. *!!! This currently ONLY works for grayscale image stacks that can be represented as 3D arrays.*

**Author**: Marcel Goldschen-Ohm  
**Email**:  <marcel.goldschen@gmail.com>  
**License**: MIT  
Copyright (c) 2015 Marcel Goldschen-Ohm  

## INSTALL

Everything's in `MultiPageTIFFViewerQt.py`. Just put it somewhere where your project can find it.

### Requires:

* [PyQt](https://www.riverbankcomputing.com/software/pyqt/intro) (version 4 or 5)
* [TiffCapture](https://github.com/cdw/TiffCapture)
* [qimage2ndarray](https://github.com/hmeine/qimage2ndarray)
* [ImageViewerPyQt](https://github.com/marcel-goldschen-ohm/ImageViewerPyQt)

On Mac OS X you can install Qt4 and PyQt4 via [Homebrew](http://brew.sh) as shown below:

    brew install qt
    brew install pyqt

[TiffCapture](https://github.com/cdw/TiffCapture) and [qimage2ndarray](https://github.com/hmeine/qimage2ndarray) can be installed via pip:

    pip install tiffcapture
    pip install qimage2ndarray

## A Simple Example

```python
import sys
try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    try:
        from PyQt4.QtGui import QApplication
    except ImportError:
        raise ImportError("Requires PyQt5 or PyQt4.")
from MultiPageTIFFViewerQt import MultiPageTIFFViewerQt


if __name__ == '__main__':
    # Create the QApplication.
    app = QApplication(sys.argv)
        
    # Create an image stack viewer widget.
    stackViewer = MultiPageTIFFViewerQt()
    
    # MultiPageTIFFViewerQt.viewer references
    # the stack viewer's ImageViewerQt child widget.
    # Thus, in this example we can set the
    # display and mouse interaction options
    # as described for ImageViewerQt via the
    # stackViewer.viewer reference.
    # Or just accept the defaults as we do here.
        
    # Load an image stack to be displayed.
    # With no arguments, loadImageStack() will popup
    # a file selection dialog. Optionally, you can
    # call loadImageStack(fileName) directly as well.
    stackViewer.loadImageStack()
    
    # Read the entire stack into memory.
    # For large stacks this can be time and memory hungry.
    # !!! ONLY do this if you REALLY NEED TO !!!
    # For example, if you need to do a z projection
    # over the stack. Otherwise, this is a waste
    # of time and memory, and it's NOT necessary
    # just to view the stack as subsequent frames
    # will be loaded as they're needed in the viewer.
    # !!! Currently, this ONLY works for grayscale image
    # stacks that can be represented as 3D arrays.
    # Uncomment the following line if you want this.
    #entireStackArray = stackViewer.getAllFrames()
        
    # Show the viewer and run the application.
    stackViewer.show()
    sys.exit(app.exec_())
```
