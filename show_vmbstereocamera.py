#! /usr/bin/env python
# -*- coding:utf-8 -*-


#
# Show the images from two Allied Vision cameras
#


#
# External dependencies
#
import sys
import cv2
import numpy as np
#from PySide import QtGui
import VisionToolkit as vt


#
# Image callback function
#
def Callback( frame_left, frame_right ) :
	# Put images side by side
	stereo_image = np.concatenate( ( frame_left.image, frame_right.image ), axis = 1 )
	# Resize image for display
	stereo_image = cv2.resize( stereo_image, None, fx=0.4, fy=0.4 )
	# Display the stereo image
	cv2.imshow( 'StereoVision', stereo_image )
	cv2.waitKey( 1 )


#
# Main application
#
if __name__ == '__main__' :

#	application = QtGui.QApplication( sys.argv )
#	widget = vt.VmbStereoCameraWidget( '50-0503326223', '50-0503323406' )
#	widget.show()
#	sys.exit( application.exec_() )

	# Initialize the Vimba driver
	vt.VmbStartup()
	# Initialize the stereo cameras
	camera = vt.VmbStereoCamera( '50-0503326223', '50-0503323406' )
	# Connect the cameras
	camera.Open()
	# Start image acquisition
	camera.StartCapture( Callback )
	# Wait for user key press
	raw_input( 'Press enter to stop the capture...' )
	# Stop image acquisition
	camera.StopCapture()
	# Disconnect the camera
	camera.Close()
	# Shutdown Vimba
	vt.VmbShutdown()
	# Cleanup OpenCV
	cv2.destroyAllWindows()