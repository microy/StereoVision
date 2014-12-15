#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
from ctypes import *
import os
import cv2
import numpy


#
# Image parameters from the camera
#
width = 2452
height = 2056
payloadsize = 5041312


#
# Vimba frame structure
#
class VmbFrame( Structure ) :
	
	_fields_ = [('buffer', POINTER(c_char)),
				('bufferSize', c_uint32),
				('context', c_void_p * 4),
				('receiveStatus', c_int32),
				('receiveFlags', c_uint32),
				('imageSize', c_uint32),
				('ancillarySize', c_uint32),
				('pixelFormat', c_uint32),
				('width', c_uint32),
				('height', c_uint32),
				('offsetX', c_uint32),
				('offsetY', c_uint32),
				('frameID', c_uint64),
				('timestamp', c_uint64)]
	
	def __init__( self ) :

		self.buffer = create_string_buffer( payloadsize )
		self.bufferSize = c_uint32( payloadsize )


#
# Main
#
if __name__ == "__main__" :
	
	
	# Temporary image for display
	image_displayed = numpy.zeros( (height, 2*width), dtype=numpy.uint8 )
	
	# Number of images saved
	image_count = 0

	#
	# Vimba initialization
	#
	print( 'Vimba initialization...' )

	# Get Vimba installation directory
	vimba_path = "/" + "/".join(os.environ.get("GENICAM_GENTL64_PATH").split("/")[1:-3]) + "/VimbaC/DynamicLib/x86_64bit/libVimbaC.so"
		
	# Load Vimba library
	vimba = cdll.LoadLibrary( vimba_path )
	
	# Initialize the library
	vimba.VmbStartup()
		

	#
	# Camera connection
	#
	print( 'Camera connection...' )
	
	# Initialize camera handles
	camera_1 = c_void_p()
	camera_2 = c_void_p()
	
	# Connect the cameras
	vimba.VmbCameraOpen( '10.129.11.231', 1, byref(camera_1) )
	vimba.VmbCameraOpen( '10.129.11.232', 1, byref(camera_2) )
	
	
	#
	# Start image acquisition
	#
	print( 'Start acquisition...' )
	
	# Prepare the frames
	frame_1 = VmbFrame()
	frame_2 = VmbFrame()
	
	# Announce the frames
	vimba.VmbFrameAnnounce( camera_1, byref(frame_1), sizeof(frame_1) )
	vimba.VmbFrameAnnounce( camera_2, byref(frame_2), sizeof(frame_2) )
	
	# Start capture engine
	vimba.VmbCaptureStart( camera_1 )
	vimba.VmbCaptureStart( camera_2 )

	# Queue frames
	vimba.VmbCaptureFrameQueue( camera_1, byref(frame_1), None )
	vimba.VmbCaptureFrameQueue( camera_2, byref(frame_2), None )
	
	# Start Acquisition
	vimba.VmbFeatureCommandRun( camera_1, "AcquisitionStart" )
	vimba.VmbFeatureCommandRun( camera_2, "AcquisitionStart" )

	# Live display
	while True :

		# Capture one frame synchronously
		vimba.VmbCaptureFrameWait( camera_1, byref(frame_1), 1000 )
		vimba.VmbCaptureFrameWait( camera_2, byref(frame_2), 1000 )
		
		# Check frame status
		if frame_1.receiveStatus or frame_2.receiveStatus :
			print( 'Frame dropped...' )
			continue

		# Convert images to numpy arrays
		image_1 = numpy.fromstring( frame_1.buffer[ 0 : payloadsize ], dtype=numpy.uint8 )
		image_1.shape = ( height, width )
		image_2 = numpy.fromstring( frame_2.buffer[ 0 : payloadsize ], dtype=numpy.uint8 )
		image_2.shape = ( height, width )

		# Prepare image for display
		image_displayed[ 0:height, 0:width ] = image_1
		image_displayed[ 0:height, width:2*width ] = image_2
		
		# Display the image
		cv2.imshow( "Cameras", cv2.resize( image_displayed, None, fx=0.2, fy=0.2 ) )
		
		# Keyboard interruption
		key = cv2.waitKey(0) & 0xFF
		
		# Escape key
		if key == 27 :
			
			# Exit
			break
			
		# Space key
		elif key == 32 :
			
			# Save images to disk
			image_count = image_count + 1
			print( 'Save images {} to disk...'.format( image_count ) )
			cv2.imwrite( 'camera1-{:0>2}.png'.format(image_count), image_1 )
			cv2.imwrite( 'camera2-{:0>2}.png'.format(image_count), image_2 )
				
	# Cleanup OpenCV
	cv2.destroyAllWindows()
	
	
	#
	# Stop image acquisition
	#
	print( 'Stop acquisition...' )

	# Stop acquisition
	vimba.VmbFeatureCommandRun( camera_1, "AcquisitionStop" )
	vimba.VmbFeatureCommandRun( camera_2, "AcquisitionStop" )
	
	# Stop capture engine
	vimba.VmbCaptureEnd( camera_1 )
	vimba.VmbCaptureEnd( camera_2 )

	# Revoke frames
	vimba.VmbFrameRevokeAll( camera_1 )
	vimba.VmbFrameRevokeAll( camera_2 )

	#
	# Camera disconnection
	#
	print( 'Camera disconnection...' )
	
	# Close the cameras
	vimba.VmbCameraClose( camera_1 )
	vimba.VmbCameraClose( camera_2 )


	#
	# Vimba shutdown
	#
	print( 'Vimba shutdown...' )
	
	# Release the library
	vimba.VmbShutdown()
