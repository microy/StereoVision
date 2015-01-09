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
				
	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Start image acquisition
		self.capturing = True
		self.camera.CaptureStart( self.ImageCallback )
		
		# Keyboard interruption
		while self.capturing : pass

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
# Vimba camera viewer
#
class StereoViewer( object ) :
	
	#
	# Initialization
	#
	def __init__( self, camera_1, camera_2 ) :
		
		# Register the camera to display
		self.camera_1 = camera_1
		self.camera_2 = camera_2
	
		# Image parameters
		self.width = camera_1.width
		self.height = camera_1.height
		
		# Lock for data synchronisation
		self.lock = threading.Lock()

		# Live image of both cameras
		self.stereo_image = np.zeros( (self.height, 2*self.width), dtype=np.uint8 )
		
	#
	# Start capture and display image stream
	#
	def LiveDisplay( self ) :

		# Start image acquisition
		self.capturing = True
		self.camera_1.CaptureStart( self.ImageCallback_1 )
		self.camera_2.CaptureStart( self.ImageCallback_2 )
		
		# Keyboard interruption
		while self.capturing : pass

		# Stop image acquisition
		self.camera_1.CaptureStop()
		self.camera_2.CaptureStop()

		# Cleanup OpenCV
		cv2.destroyAllWindows()

	#
	# Display the current image for camera 1
	#
	def ImageCallback_1( self, image ) :
		
		# Lock the thread
		self.lock.acquire()
		
		# Put the current image in the combined image
		self.stereo_image[ 0:self.height, 0:self.width ] = image
		
		# Resize image for display
		image_displayed = cv2.resize( self.stereo_image, None, fx=0.3, fy=0.3 )
		
		# Release the thread
		self.lock.release()

		# Display the image (scaled down)
		cv2.imshow( "Stereo", image_displayed )

		# Keyboard interruption
		if ( cv2.waitKey(1) & 0xFF ) == 27 :
			self.capturing = False

	#
	# Display the current image for camera 2
	#
	def ImageCallback_2( self, image ) :
		
		# Lock the thread
		self.lock.acquire()
		
		# Put the current image in the combined image
		self.stereo_image[ 0:self.height, self.width:2*self.width ] = image

		# Resize image for display
		image_displayed = cv2.resize( self.stereo_image, None, fx=0.3, fy=0.3 )
		
		# Release the thread
		self.lock.release()

		# Display the image (scaled down)
		cv2.imshow( "Stereo", image_displayed )

		# Keyboard interruption
		if ( cv2.waitKey(1) & 0xFF ) == 27 :
			self.capturing = False
