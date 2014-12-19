#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
import ctypes
import os
import cv2
import numpy
import time


#
# Vimba frame structure
#
class VmbFrame( ctypes.Structure ) :
	
	# VmbFrame structure fields
	_fields_ = [('buffer', ctypes.POINTER(ctypes.c_char)),
			('bufferSize', ctypes.c_uint32),
			('context', ctypes.c_void_p * 4),
			('receiveStatus', ctypes.c_int32),
			('receiveFlags', ctypes.c_uint32),
			('imageSize', ctypes.c_uint32),
			('ancillarySize', ctypes.c_uint32),
			('pixelFormat', ctypes.c_uint32),
			('width', ctypes.c_uint32),
			('height', ctypes.c_uint32),
			('offsetX', ctypes.c_uint32),
			('offsetY', ctypes.c_uint32),
			('frameID', ctypes.c_uint64),
			('timestamp', ctypes.c_uint64)]
	
	# Initialize the image buffer
	def __init__( self, frame_size ) :

		self.buffer = ctypes.create_string_buffer( frame_size )
		self.bufferSize = ctypes.c_uint32( frame_size )






#
# Initialization
#

# Default image parameters from our cameras (AVT Manta G504B)
width = 2452
height = 2056
payloadsize = 5041312

# Camera handles
camera_1 = ctypes.c_void_p()

# Image frames
frame_1 = VmbFrame( payloadsize )

# Number of images saved
image_count = 0

# Frame per second counter
frame_counter = 0
fps_counter = 0


#
# Vimba initialization
#
print( 'Vimba initialization...' )

# Get Vimba installation directory
vimba_path = "/" + "/".join(os.environ.get("GENICAM_GENTL64_PATH").split("/")[1:-3]) + "/VimbaC/DynamicLib/x86_64bit/libVimbaC.so"
	
# Load Vimba library
vimba = ctypes.cdll.LoadLibrary( vimba_path )

# Initialize the library
vimba.VmbStartup()
	
# Send discovery packet to GigE cameras
vimba.VmbFeatureCommandRun( ctypes.c_void_p(1), "GeVDiscoveryAllOnce" )


#
# Camera connection
#
print( 'Camera connection...' )

# Connect the cameras via their serial number
vimba.VmbCameraOpen( '50-0503323406', 1, ctypes.byref(camera_1) )

# Adjust packet size automatically on each camera
vimba.VmbFeatureCommandRun( camera_1, "GVSPAdjustPacketSize" )

# Configure frame software trigger
vimba.VmbFeatureEnumSet( camera_1, "TriggerSource", "Freerun" )



CMPFUNC = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_void_p )


def FrameCallback( camera, pFrame ) :

	print( 'Frame callback - Frame ID : {}...', pFrame.contents.frameID )

	# Check frame validity
	if pFrame.contents.receiveStatus :
		print(' Frame status invalid...' )

	# Convert frames to numpy arrays
	image_1 = numpy.fromstring( frame_1.buffer[ 0 : payloadsize ], dtype=numpy.uint8 ).reshape( height, width )

	# Resize image for display
	image_final = cv2.resize( image_1, None, fx=0.5, fy=0.5 )

	# Requeue the frame so it can be filled again
	vimba.VmbCaptureFrameQueue( camera, pFrame, ctypes.byref(CMPFUNC( FrameCallback )) )


frame_callback_function = CMPFUNC( FrameCallback )






#
# Start image acquisition
#
print( 'Start acquisition...' )

# Announce the frames
vimba.VmbFrameAnnounce( camera_1, ctypes.byref(frame_1), ctypes.sizeof(frame_1) )

# Start capture engine
vimba.VmbCaptureStart( camera_1 )

# Start acquisition
vimba.VmbFeatureCommandRun( camera_1, "AcquisitionStart" )

# Initialize the clock for counting the number of frames per second
time_start = time.clock()


for i in range(3) :
	
	# Queue frames
	vimba.VmbCaptureFrameQueue( camera_1, ctypes.byref(frame_1[i]), frame_callback_function )
	

# Live display
while True :
	
	# Queue frames
#	vimba.VmbCaptureFrameQueue( camera_1, ctypes.byref(frame_1), None )
	
	# Send software trigger
#	vimba.VmbFeatureCommandRun( camera_1, "TriggerSoftware" )

	# Get frames back
#	vimba.VmbCaptureFrameWait( camera_1, ctypes.byref(frame_1), 1000 )
	
	# Check frame validity
#	if frame_1.receiveStatus :
#		continue
	
	# Frames per second counter
	frame_counter += 1
	time_elapsed = time.clock() - time_start
	if time_elapsed > 0.5 :
		fps_counter = frame_counter / time_elapsed
		frame_counter = 0
		time_start = time.clock()
	
	# Write FPS counter on the displayed image
	cv2.putText( image_final, '{:.2f} FPS'.format( fps_counter ), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255) )
	
	# Display the image (scaled down)
	cv2.imshow( "Stereo Cameras", image_final )
	
	# Keyboard interruption
	key = cv2.waitKey(1) & 0xFF
	
	# Escape key
	if key == 27 :
		
		# Exit live display
		break
		
	# Space key
	elif key == 32 :
		
		# Save images to disk 
		image_count += 1
		print( 'Save image {} to disk...'.format( image_count ) )
		cv2.imwrite( 'camera1-{:0>2}.png'.format(image_count), image_1 )
			
# Cleanup OpenCV
cv2.destroyAllWindows()


#
# Stop image acquisition
#
print( 'Stop acquisition...' )

# Stop acquisition
vimba.VmbFeatureCommandRun( camera_1, "AcquisitionStop" )

# Stop capture engine
vimba.VmbCaptureEnd( camera_1 )

# Flush the frame queue
vimba.VmbCaptureQueueFlush( camera_1 )

# Revoke frames
vimba.VmbFrameRevokeAll( camera_1 )


#
# Camera disconnection
#
print( 'Camera disconnection...' )

# Close the cameras
vimba.VmbCameraClose( camera_1 )


#
# Vimba shutdown
#
print( 'Vimba shutdown...' )

# Release the library
vimba.VmbShutdown()
