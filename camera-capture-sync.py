#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images synchronously
# from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
import collections, cv2, os, time
import ctypes as ct
import numpy as np


#
# Vimba frame structure
#
class VmbFrame( ct.Structure ) :
	
	# VmbFrame structure fields
	_fields_ = [('buffer', ct.POINTER(ct.c_char)),
			('bufferSize', ct.c_uint32),
			('context', ct.c_void_p * 4),
			('receiveStatus', ct.c_int32),
			('receiveFlags', ct.c_uint32),
			('imageSize', ct.c_uint32),
			('ancillarySize', ct.c_uint32),
			('pixelFormat', ct.c_uint32),
			('width', ct.c_uint32),
			('height', ct.c_uint32),
			('offsetX', ct.c_uint32),
			('offsetY', ct.c_uint32),
			('frameID', ct.c_uint64),
			('timestamp', ct.c_uint64)]
	
	# Initialize the image buffer
	def __init__( self, frame_size ) :

		self.buffer = ct.create_string_buffer( frame_size )
		self.bufferSize = ct.c_uint32( frame_size )




#
# Initialization
#

# Default image parameters from our cameras (AVT Manta G504B)
width = 2452
height = 2056
payloadsize = 5041312

# Camera handles
camera_1 = ct.c_void_p()
camera_2 = ct.c_void_p()

# Image frames
frame_1 = VmbFrame( payloadsize )
frame_2 = VmbFrame( payloadsize )

# Temporary image for display
image_temp = np.zeros( (height, 2*width), dtype=np.uint8 )

# Number of images saved
image_count = 0

# Frame per second counter
fps_counter = 0
fps_buffer = collections.deque( 10*[0], 10 )



#
# Vimba initialization
#
print( 'Vimba initialization...' )

# Get Vimba installation directory
vimba_path = "/" + "/".join(os.environ.get("GENICAM_GENTL64_PATH").split("/")[1:-3]) + "/VimbaC/DynamicLib/x86_64bit/libVimbaC.so"
	
# Load Vimba library
vimba = ct.cdll.LoadLibrary( vimba_path )

# Initialize the library
vimba.VmbStartup()
	
# Send discovery packet to GigE cameras
vimba.VmbFeatureCommandRun( ct.c_void_p(1), "GeVDiscoveryAllOnce" )




#
# Camera connection
#
print( 'Camera connection...' )

# Connect the cameras via their serial number
vimba.VmbCameraOpen( '50-0503323406', 1, ct.byref(camera_1) )
vimba.VmbCameraOpen( '50-0503326223', 1, ct.byref(camera_2) )

# Adjust packet size automatically on each camera
vimba.VmbFeatureCommandRun( camera_1, "GVSPAdjustPacketSize" )
vimba.VmbFeatureCommandRun( camera_2, "GVSPAdjustPacketSize" )

# Configure frame software trigger
vimba.VmbFeatureEnumSet( camera_1, "TriggerSource", "Software" )
vimba.VmbFeatureEnumSet( camera_2, "TriggerSource", "Software" )




#
# Start image acquisition
#
print( 'Start acquisition...' )

# Announce the frames
vimba.VmbFrameAnnounce( camera_1, ct.byref(frame_1), ct.sizeof(frame_1) )
vimba.VmbFrameAnnounce( camera_2, ct.byref(frame_2), ct.sizeof(frame_2) )

# Start capture engine
vimba.VmbCaptureStart( camera_1 )
vimba.VmbCaptureStart( camera_2 )

# Start acquisition
vimba.VmbFeatureCommandRun( camera_1, "AcquisitionStart" )
vimba.VmbFeatureCommandRun( camera_2, "AcquisitionStart" )



#
# Live display
#
while True :
	
	# Initialize the clock for counting the number of frames per second
	time_start = time.clock()

	# Queue frames
	vimba.VmbCaptureFrameQueue( camera_1, ct.byref(frame_1), None )
	vimba.VmbCaptureFrameQueue( camera_2, ct.byref(frame_2), None )
	
	# Send software trigger
	vimba.VmbFeatureCommandRun( camera_1, "TriggerSoftware" )
	vimba.VmbFeatureCommandRun( camera_2, "TriggerSoftware" )

	# Get frames back
	vimba.VmbCaptureFrameWait( camera_1, ct.byref(frame_1), 1000 )
	vimba.VmbCaptureFrameWait( camera_2, ct.byref(frame_2), 1000 )
	
	# Check frame validity
	if frame_1.receiveStatus or frame_2.receiveStatus :
		continue
	
	# Convert frames to numpy arrays
	image_1 = np.fromstring( frame_1.buffer[ 0 : payloadsize ], dtype=np.uint8 ).reshape( height, width )
	image_2 = np.fromstring( frame_2.buffer[ 0 : payloadsize ], dtype=np.uint8 ).reshape( height, width )

	# Prepare image for display
	image_temp[ 0:height, 0:width ] = image_1
	image_temp[ 0:height, width:2*width ] = image_2
	
	# Resize image for display
	image_final = cv2.resize( image_temp, None, fx=0.3, fy=0.3 )

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
		print( 'Save images {} to disk...'.format( image_count ) )
		cv2.imwrite( 'camera1-{:0>2}.png'.format(image_count), image_1 )
		cv2.imwrite( 'camera2-{:0>2}.png'.format(image_count), image_2 )
		
	# Frames per second counter
	fps_buffer.pop()
	fps_buffer.appendleft( time.clock() - time_start )
	fps_counter = 10.0 / sum( fps_buffer )


			
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

# Flush the frame queue
vimba.VmbCaptureQueueFlush( camera_1 )
vimba.VmbCaptureQueueFlush( camera_2 )

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
