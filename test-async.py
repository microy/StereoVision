#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images asynchronously
# from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
import cv2
import ctypes as ct
import numpy as np
import Vimba
import Viewer


#
# Process the current image
#
def ProcessImage1( image ) :
	
	# Resize image for display
	image_displayed = cv2.resize( image, None, fx=0.3, fy=0.3 )

	# Display the image (scaled down)
	cv2.imshow( "Camera1", image_displayed )
	cv2.waitKey( 1 )


#
# Process the current image
#
def ProcessImage2( image ) :
	
	# Resize image for display
	image_displayed = cv2.resize( image, None, fx=0.3, fy=0.3 )

	# Display the image (scaled down)
	cv2.imshow( "Camera2", image_displayed )
	cv2.waitKey( 1 )



#
# Main program
#


# Vimba initialization
Vimba.VmbStartup()
vimba = Vimba.vimba

# Camera connection
camera1 = Vimba.VmbCamera( '50-0503323406' )
camera2 = Vimba.VmbCamera( '50-0503326223' )

# Live asynchronous capture
camera1.CaptureStart( ProcessImage1 )
camera2.CaptureStart( ProcessImage2 )

raw_input( 'Press enter...' )

# Cleanup OpenCV
cv2.destroyWindow( "Camera" )

# Stop image acquisition
camera1.CaptureStop()
camera2.CaptureStop()

# Camera disconnection
camera1.Disconnect()
camera2.Disconnect()

# Vimba shutdown
vimba.VmbShutdown()


