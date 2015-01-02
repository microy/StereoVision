#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images asynchronously
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
# Frame callback function
#
def FrameCallback( camera, pFrame ) :

        # Variables from main application
        global vimba
        global frame_callback_function
        global image

        # Print frame informations
        print( 'Frame callback - Frame ID : {}...', pFrame.contents.frameID )
        
		# Check frame validity
        if pFrame.contents.receiveStatus :
                print('Frame status invalid...' )

		# Convert frames to numpy arrays
        image = np.fromstring( pFrame.contents.buffer[ 0 : payloadsize ], dtype=np.uint8 ).reshape( height, width )

		# Requeue the frame so it can be filled again
        vimba.VmbCaptureFrameQueue( camera, pFrame, frame_callback_function )





#
# Initialization
#

# Default image parameters from our cameras (AVT Manta G504B)
width = 2452
height = 2056
payloadsize = 5041312

# Camera handles
camera = ct.c_void_p()

# 3 image frames in the buffer
frames = []
for i in range( 3 ) :
	frames.append( VmbFrame( payloadsize ) )

# The current image
image = np.zeros( (height, width), dtype=np.uint8 )

# Number of images saved
image_count = 0

# Frame per second counter
fps_counter = 0
fps_buffer = collections.deque( 10*[0], 10 )

# Reference to frame callback function
frame_callback_function = ct.CFUNCTYPE( None, ct.c_void_p, ct.c_void_p )( FrameCallback )




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
vimba.VmbCameraOpen( '50-0503323406', 1, ct.byref(camera) )

# Adjust packet size automatically on each camera
vimba.VmbFeatureCommandRun( camera, "GVSPAdjustPacketSize" )

# Configure frame software trigger
vimba.VmbFeatureEnumSet( camera, "TriggerSource", "Freerun" )




#
# Start image acquisition
#
print( 'Start acquisition...' )

# Announce the frames
for i in range( 3 ) :
	vimba.VmbFrameAnnounce( camera, ct.byref(frames[i]), ct.sizeof(frames[i]) )

# Start capture engine
vimba.VmbCaptureStart( camera )

# Start acquisition
vimba.VmbFeatureCommandRun( camera, "AcquisitionStart" )

# Queue frames
for i in range( 3 ) :
	vimba.VmbCaptureFrameQueue( camera, ct.byref(frames[i]), frame_callback_function )




#
# Live display
#
while True :
	
	# Initialize the clock for counting the number of frames per second
	time_start = time.clock()
	
	# Resize image for display
	image_displayed = cv2.resize( image, None, fx=0.5, fy=0.5 )
	
	# Write FPS counter on the displayed image
	cv2.putText( image_displayed, '{:.2f} FPS'.format( fps_counter ), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255) )
	
	# Display the image (scaled down)
	cv2.imshow( "Stereo Cameras", image_displayed )
	
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
		cv2.imwrite( 'camera1-{:0>2}.png'.format(image_count), image )

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
vimba.VmbFeatureCommandRun( camera, "AcquisitionStop" )

# Stop capture engine
vimba.VmbCaptureEnd( camera )

# Flush the frame queue
vimba.VmbCaptureQueueFlush( camera )

# Revoke frames
vimba.VmbFrameRevokeAll( camera )




#
# Camera disconnection
#
print( 'Camera disconnection...' )

# Close the cameras
vimba.VmbCameraClose( camera )



#
# Vimba shutdown
#
print( 'Vimba shutdown...' )

# Release the library
vimba.VmbShutdown()
