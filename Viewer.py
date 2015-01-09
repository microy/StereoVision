# -*- coding:utf-8 -*- 


#
# Module to display live images from AVT cameras
#


#
# External dependencies
#
import collections
import time
import threading
import cv2
import numpy as np
import Calibration



#
# Vimba camera viewer
#
class Viewer( object ) :
	
	#
	# Initialization
	#
	def __init__( self, camera ) :
		
		# Register the camera to display
		self.camera = camera
		
		# Lock for data synchronisation
#		self.lock = threading.Lock()
		
	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Start image acquisition
		self.capturing = True
		self.camera.CaptureStart( self.ImageCallback )
		
		# Start camera statistics thread
		camera_stats = CameraStatThread( self.camera )
		camera_stats.Start()
		
		# Keyboard interruption
		while self.capturing : pass

		# Stop camera statistics thread
		camera_stats.Stop()

		# Stop image acquisition
		self.camera.CaptureStop()

		# Cleanup OpenCV
		cv2.destroyWindow( self.camera.id_string )

	#
	# Display the current image
	#
	def ImageCallback( self, image ) :
		
		# Resize image for display
		image_displayed = cv2.resize( image, None, fx=0.3, fy=0.3 )

		# Display the image (scaled down)
		cv2.imshow( self.camera.id_string, image_displayed )

		# Keyboard interruption
		if ( cv2.waitKey(1) & 0xFF ) == 27 :
			self.capturing = False


#
# Live display
#
def LiveDisplay( camera ) :
	
	# Frame per second counter
	fps = FramePerSecondCounter()
	
	# Create an OpenCV window
	cv2.namedWindow( camera.id_string )

	# Start image acquisition
	camera.CaptureStart()
	
	# Start camera statistics thread
	camera_stats = CameraStatThread( camera )
	camera_stats.Start()
	
	#

	# Start live display
	while True :
		
		# Capture an image
		camera.CaptureFrame()
		
		# Count time taken for this frame
		fps.Tick()
		
		# Resize image for display
		image_live = cv2.resize( camera.image, None, fx=0.3, fy=0.3 )

		# Draw chessboard on the image
		Calibration.FindAndDrawChessboard( image_live )

		# Write FPS counter on the live image
		cv2.putText( image_live, '{:.2f} FPS'.format( fps.counter ), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255) )

		# Display the image
		cv2.imshow( camera.id_string, image_live )
		
		# Keyboard interruption
		if ( cv2.waitKey(1) & 0xFF ) == 27 : break

	# Cleanup OpenCV
	cv2.destroyWindow( camera.id_string )

	# Stop camera statistics thread
	camera_stats.Stop()

	# Stop image acquisition
	camera.CaptureStop()


#
# Live display stereo
#
def LiveDisplayStereo( camera_1, camera_2 ) :
	
	# Frame per second counter
	fps = FramePerSecondCounter()
	
	# Image parameters
	width = camera_1.width
	height = camera_1.height
	
	# Live image of both cameras
	image_tmp = np.zeros( (height, 2*width), dtype=np.uint8 )

	# Create an OpenCV window
	cv2.namedWindow( "Stereo Camera" )

	# Start camera statistics thread
	camera_stats_1 = CameraStatThread( camera_1 )
	camera_stats_2 = CameraStatThread( camera_2 )
	camera_stats_1.Start()
	camera_stats_2.Start()

	# Start image acquisition
	camera_1.CaptureStart()
	camera_2.CaptureStart()

	# Start live display
	while True :
		
		# Capture an image
		camera_1.CaptureFrame()
		camera_2.CaptureFrame()
		
		# Count time taken for these frames
		fps.Tick()

		# Prepare image for display
		image_tmp[ 0:height, 0:width ] = camera_1.image
		image_tmp[ 0:height, width:2*width ] = camera_2.image

		# Resize image for display
		image_live = cv2.resize( image_tmp, None, fx=0.3, fy=0.3 )

		# Write FPS counter on the live image
		cv2.putText( image_live, '{:.2f} FPS'.format( fps.counter ), (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255) )

		# Display the image
		cv2.imshow( "Stereo Camera", image_live )
		
		# Keyboard interruption
		if ( cv2.waitKey(1) & 0xFF ) == 27 : break

	# Cleanup OpenCV
	cv2.destroyWindow( "Stereo Camera" )

	# Stop camera statistics thread
	camera_stats_1.Stop()
	camera_stats_2.Stop()

	# Stop image acquisition
	camera_1.CaptureStop()
	camera_2.CaptureStop()


#
# Frame per second counter
#
class FramePerSecondCounter( object ) :
	

	#
	# Initialization
	#
	def __init__( self ) :
		
		self.buffer = collections.deque( 10*[1.0], 10 )
		self.time_start = time.clock()


	#
	# Register elapsed time
	#
	def Tick( self ) :
		
		self.buffer.pop()
		self.buffer.appendleft( time.clock() - self.time_start )
		self.counter = 10.0 / sum( self.buffer )
		self.time_start = time.clock()


#
# Camera statistics thread
#
class CameraStatThread( threading.Thread ) :
	
	
	#
	# Initialisation
	#
	def __init__( self, camera ) :
		
		# Initialise the thread
		threading.Thread.__init__( self )
		
		# Camera handle
		self.camera = camera
		
		# Abortion
		self.abort = False
		
	#
	# Start the thread
	#
	def Start( self ) :
		
		# Start the thread
		self.start()

	#
	# Stop the thread
	#
	def Stop( self ) :
		
		# Stop the thread
		self.abort = True
		self.join()

	#
	# Run the thread
	#
	def run( self ) :
		
		# Run in loop until aborted
		while not self.abort :
			
			# Sleep one second
			time.sleep( 1 )
		
			# Print camera statistics
			self.camera.PrintStats()
