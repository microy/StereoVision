#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture images asynchronously
# from two AVT Manta cameras with the Vimba SDK
#


#
# External dependencies
#
import Vimba
import collections, cv2, time
import ctypes as ct
import numpy as np





#
# Frame callback function
#
def FrameCallback( pCamera, pFrame ) :

	# Print frame informations
	print( 'Frame callback - Frame ID : {}...', pFrame.contents.frameID )

	# Check frame validity
	if pFrame.contents.receiveStatus :
		print('Frame status invalid...' )
		return

	# Convert frames to numpy arrays
	image = np.fromstring( pFrame.contents.buffer[ 0 : payloadsize ], dtype=np.uint8 ).reshape( height, width )
	
	# Process current image
	ProcessImage( image )

	# Requeue the frame so it can be filled again
	vimba.VmbCaptureFrameQueue( pCamera, pFrame, ct.byref(frame_callback_function) )


#
# Process the current image
#
def ProcessImage( image ) :
	
	# Resize image for display
	image_displayed = cv2.resize( image, None, fx=0.3, fy=0.3 )

	# Write FPS counter on the displayed image
#	cv2.putText( image_displayed, '{:.2f} FPS'.format( fps_counter ), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255) )

	# Display the image (scaled down)
	cv2.imshow( "Camera", image_displayed )

	# Frames per second counter
#	fps_buffer.pop()
#	fps_buffer.appendleft( time.clock() - time_start )
#	fps_counter = 10.0 / sum( fps_buffer )


#
# Asynchronous capture
#
def CaptureAsync() :
	
	# Default image parameters from our cameras (AVT Manta G504B)
	width = 2452
	height = 2056
	payloadsize = 5041312

	# Initialize the image
	image = np.zeros( (height, width), dtype=np.uint8 )	

	# Frame per second counter
	fps_counter = 1.0
	fps_buffer = collections.deque( 10*[1.0], 10 )

	# Reference to frame callback function
	frame_callback_function = ct.CFUNCTYPE( None, ct.c_void_p, ct.c_void_p )( FrameCallback )

	# Create 3 frames to fill in the camera buffer
	frames = []
	for i in range( 3 ) :
		frames.append( Vimba.VmbFrame( payloadsize ) )
	
	# Configure freerun trigger
	vimba.VmbFeatureEnumSet( camera.handle, "FrameStartTriggerMode", "Freerun" )

	# Announce the frames
	for i in range( 3 ) :
		vimba.VmbFrameAnnounce( camera.handle, ct.byref(frames[i]), ct.sizeof(frames[i]) )
		
	# Start capture engine
	vimba.VmbCaptureStart( camera.handle )

	# Queue frames
	for i in range( 3 ) :
		vimba.VmbCaptureFrameQueue( camera.handle, ct.byref(frames[i]), ct.byref(frame_callback_function) )

	# Initialize the clock for counting the number of frames per second
	time_start = time.clock()

	# Create an OpenCV window
	cv2.namedWindow( "Camera" )

	# Display the image (scaled down)
	cv2.imshow( "Camera", cv2.resize( image, None, fx=0.3, fy=0.3 ) )

	# Start acquisition
	vimba.VmbFeatureCommandRun( camera.handle, "AcquisitionStart" )

	# Live display
	while True :
		
		# Keyboard interruption
		key = cv2.waitKey(1) & 0xFF
		
		# Escape key
		if key == 27 :
			
			# Exit live display
			break
			
	# Cleanup OpenCV
	cv2.destroyWindow( "Camera" )



#
# Main program
#


# Vimba initialization
Vimba.VmbStartup()
vimba = Vimba.vimba

# Camera connection
camera = Vimba.VmbCamera( '50-0503323406' )

# Live asynchronous capture
CaptureAsync()

# Stop image acquisition
camera.CaptureStop()

# Camera disconnection
camera.Disconnect()

# Vimba shutdown
vimba.VmbShutdown()


