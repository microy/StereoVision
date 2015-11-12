# -*- coding:utf-8 -*-


#
# Module to capture images from USB cameras
#


#
# External dependencies
#
import threading
import cv2


#
# Thread to read the images from a USB camera
#
class UsbCamera( threading.Thread ) :

	#
	# Initialisation
	#
	def __init__( self, image_callback ) :

		# Initialize the thread
		super( UsbCamera, self ).__init__()

		# Function called when an image is received
		self.image_callback = image_callback

		# Initialize the camera
		self.camera = cv2.VideoCapture( 0 )

		# Set camera resolution
		self.camera.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
		self.camera.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )

		# Set camera frame rate
		self.camera.set( cv2.cv.CV_CAP_PROP_FPS, 25 )

	#
	# Thread main loop
	#
	def run( self ) :

		# Thread running
		self.running = True
		while self.running :

			# Capture image from the camera
			_, image = self.camera.read()

			# Send the image via the external callback function
			self.image_callback( image )

		# Release the camera
		self.camera.release()


#
# Thread to read images from two USB cameras
#
class StereoUsbCamera( threading.Thread ) :

	#
	# Initialisation
	#
	def __init__( self, image_callback ) :

		# Initialize the thread
		super( StereoUsbCamera, self ).__init__()

		# Function called when the images are received
		self.image_callback = image_callback

		# Initialize the cameras
		self.camera_left = cv2.VideoCapture( 0 )
		self.camera_right = cv2.VideoCapture( 1 )

		# Lower the camera frame rate and resolution
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FPS, 5 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FPS, 5 )

	#
	# Thread main loop
	#
	def run( self ) :

		# Thread running
		self.running = True
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
