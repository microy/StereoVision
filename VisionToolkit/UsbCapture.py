# -*- coding:utf-8 -*-

#
# Module to capture images from USB cameras
#

# External dependencies
import threading
import cv2

# Thread to read the images from a USB camera
class UsbCapture( threading.Thread ) :

	# Initialisation
	def __init__( self, image_callback ) :
		# Initialize the thread
		super( UsbCapture, self ).__init__()
		# Function called when an image is received
		self.image_callback = image_callback
		# Initialize the camera
		self.camera = cv2.VideoCapture( 0 )

	# Return the image width
	@property
	def width( self ) :
		return self.camera.get( cv2.cv.CV_CAP_PROP_FRAME_WIDTH )

	# Return the image height
	@property
	def height( self ) :
		return self.camera.get( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT )

	# Start acquisition
	def Start( self ) :
		self.running = True
		self.start()

	# Stop acquisition
	def Stop( self ) :
		self.running = False
		self.join()

	# Thread main loop
	def run( self ) :
		# Thread running
		while self.running :
			# Capture image from the camera
			_, image = self.camera.read()
			# Send the image via the external callback function
			self.image_callback( image )
		# Release the camera
		self.camera.release()

# Thread to read the images from two USB cameras
class UsbStereoCapture( threading.Thread ) :

	# Initialisation
	def __init__( self, image_callback ) :
		# Initialize the thread
		super( UsbStereoCapture, self ).__init__()
		# Function called when the images are received
		self.image_callback = image_callback
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
	def Start( self ) :
		self.running = True
		self.start()

	# Stop acquisition
	def Stop( self ) :
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
