#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to calibrate stereo cameras
#


# External dependencies
import os
import PyStereoVisionToolkit as psvtk

# Calibration pattern size
pattern_size = ( 9, 6 )
		
# Create calibration directory
try : os.makedirs( 'Calibration' )
except OSError :
	if not os.path.isdir( 'Calibration' ) : raise

# Launch the stereo camera viewer
psvtk.Camera.UsbStereoViewer( pattern_size, True )

# Calibrate the stereo cameras
psvtk.Calibration.StereoCameraCalibration( 'Calibration', pattern_size )

