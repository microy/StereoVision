#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# StereoVision application
#

# External dependencies
import sys
from PySide import QtGui
import StereoVision as sv

# Main application
if __name__ == '__main__' :
	application = QtGui.QApplication( sys.argv )
	widget = sv.VmbStereoVision()
	widget.show()
	sys.exit( application.exec_() )
