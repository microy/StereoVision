# -*- coding:utf-8 -*-

#
# Module to capture images from USB cameras
#

# External dependencies
import threading
import cv2

# Thread to read the images from two USB cameras
class UsbStereoCamera( threading.Thread ) :
	# Initialisation
	def __init__( self ) :
		# Initialize the thread
		super( UsbStereoCamera, self ).__init__()
		# Initialize the cameras
		self.camera_left = cv2.VideoCapture( 0 )
		self.camera_right = cv2.VideoCapture( 1 )
	# Return the image width
	@property
	def width( self ) :
		return self.camera_left.get( cv2.cv.CV_CAP_PROP_FRAME_WIDTH )
	# Return the image height
	@property
	def height( self ) :
		return self.camera_left.get( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT )
	# Start acquisition
	def StartCapture( self, image_callback ) :
		# Function called when the images are received
		self.image_callback = image_callback
		# Start the capture loop
		self.running = True
		self.start()
	# Stop acquisition
	def StopCapture( self ) :
		self.running = False
		self.join()
	# Thread main loop
	def run( self ) :
		# Thread running
		while self.running :
			# Capture images
			self.camera_left.grab()
			self.camera_right.grab()
			# Get the images
			_, image_left = self.camera_left.retrieve()
			_, image_right = self.camera_right.retrieve()
			# Send the image via the external callback function
			self.image_callback( image_left, image_right )
		# Release the cameras
		self.camera_left.release()
		self.camera_right.release()
