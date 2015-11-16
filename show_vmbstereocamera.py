#! /usr/bin/env python
# -*- coding:utf-8 -*-


#
# Show the images from two Allied Vision cameras
#


#
# External dependencies
#
import sys
from PySide import QtGui
import VisionToolkit as vt


#
# Main application
#
if __name__ == '__main__' :

	application = QtGui.QApplication( sys.argv )
	widget = vtk.VmbStereoCameraWidget( '50-0503326223', '50-0503323406' )
	widget.show()
	sys.exit( application.exec_() )
