#! /usr/bin/env python
# -*- coding:utf-8 -*-


#
# Show the images from a USB camera
#


#
# External dependencies
#
import sys
from PySide import QtGui
import VisionToolkit as vtk


#
# Main application
#
if __name__ == '__main__' :

    application = QtGui.QApplication( sys.argv )
    widget = vtk.UsbCameraWidget()
    widget.show()
    sys.exit( application.exec_() )
