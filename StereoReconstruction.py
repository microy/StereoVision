#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate stereo cameras
#


# External dependencies
import os
import sys
import PySide.QtGui as qtgui
import PyStereoVisionToolkit as psvtk

# Calibration pattern size
pattern_size = ( 9, 6 )
		
# Launch the stereo camera viewer
psvtk.Camera.UsbStereoViewer( pattern_size )

# Qt application
application = qtgui.QApplication( sys.argv )

# Create the widget for the stereo reconstruction
stereosgbm = psvtk.Disparity.StereoSGBM()

# Show the widget used to reconstruct the 3D mesh
stereosgbm.show()

sys.exit( application.exec_() )
