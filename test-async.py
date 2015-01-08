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


# Default image parameters from our cameras (AVT Manta G504B)
width = 2452
height = 2056
payloadsize = 5041312

# Reference to the frame callback functions
frame_callback_function1 = None
frame_callback_function2 = None


#
# Frame callback function
#
def FrameCallback1( pCamera, pFrame ) :

	# Print frame informations
#	print( 'Frame callback - Frame ID : {} - Status : {}...'.format(pFrame.contents.frameID, pFrame.contents.receiveStatus) )

	# Check frame validity
	if pFrame.contents.receiveStatus :
		print('Invalid frame received... {}'.format(pFrame.contents.receiveStatus) )

	# Convert frames to numpy arrays
	image = np.fromstring( pFrame.contents.buffer[ 0 : payloadsize ], dtype=np.uint8 ).reshape( height, width )
	
	# Process current image
	ProcessImage1( image )

	# Requeue the frame so it can be filled again
	vimba.VmbCaptureFrameQueue( pCamera, pFrame, frame_callback_function1 )


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
# Frame callback function
#
def FrameCallback2( pCamera, pFrame ) :

	# Check frame validity
	if pFrame.contents.receiveStatus :
		print('Invalid frame received... {}'.format(pFrame.contents.receiveStatus) )

	# Convert frames to numpy arrays
	image = np.fromstring( pFrame.contents.buffer[ 0 : payloadsize ], dtype=np.uint8 ).reshape( height, width )
	
	# Process current image
	ProcessImage2( image )

	# Requeue the frame so it can be filled again
	vimba.VmbCaptureFrameQueue( pCamera, pFrame, frame_callback_function2 )


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

# Reference to frame callback function
frame_callback_function1 = ct.CFUNCTYPE( None, ct.c_void_p, ct.POINTER(Vimba.VmbFrame) )( FrameCallback1 )
frame_callback_function2 = ct.CFUNCTYPE( None, ct.c_void_p, ct.POINTER(Vimba.VmbFrame) )( FrameCallback2 )

# Live asynchronous capture
#CaptureAsync()
camera1.CaptureStart( frame_callback_function1 )
camera2.CaptureStart( frame_callback_function2 )

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


