# -*- coding:utf-8 -*-


#
# Module to display live images from two cameras
#


#
# External dependencies
#
import threading
import cv2
import numpy as np
from PySide import QtCore
from PySide import QtGui
import VisionToolkit as vt


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


#
# Qt Widget to display the images from stereo cameras
#
class StereoCameraWidget( vt.CameraWidget ) :

	#
	# Initialisation
	#
	def __init__( self, parent = None, calibration = None ) :

		# Initialise QLabel
		super( StereoCameraWidget, self ).__init__( parent )

		# Store the calibration parameters
		self.calibration = calibration

		# Initialize the widget parameters
		self.setAlignment( QtCore.Qt.AlignCenter )
		self.setFixedSize( 1280, 480 )

		# Initialize the viewing parameters
		self.chessboard_enabled = False
		self.cross_enabled = False
		self.rectification_enabled = False
		self.disparity_enabled = False

		# StereoSGBM
		self.disparity = vt.StereoSGBM()

		# Point cloud viewer
		self.pointcloud_viewer = vt.PointCloudViewer()
		self.X, self.Y = np.meshgrid( np.arange( 320 ), np.arange( 240 ) )

		# Initialize the stereo cameras
		self.stereo_camera = StereoUsbCamera( self.ImageCallback )
		self.stereo_camera.start()

	#
	# Receive the images from the cameras, and process them
	#
	def ImageCallback( self, image_left, image_right ) :

		# Copy images for display
		image_left_displayed = np.array( image_left )
		image_right_displayed = np.array( image_right )

		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_left_displayed = vt.PreviewChessboard( image_left_displayed )
			image_right_displayed = vt.PreviewChessboard( image_right_displayed )

		# Display a cross in the middle of the image
		if self.cross_enabled :
			cv2.rectangle( image_left_displayed, (220, 100), (420, 380), (0, 255, 0), 2 )
			cv2.rectangle( image_right_displayed, (220, 100), (420, 380), (0, 255, 0), 2 )
			cv2.line( image_left_displayed, (320, 0), (320, 480), (0, 0, 255), 2 )
			cv2.line( image_left_displayed, (0, 240), (640, 240), (0, 0, 255), 2 )
			cv2.line( image_right_displayed, (320, 0), (320, 480), (0, 0, 255), 2 )
			cv2.line( image_right_displayed, (0, 240), (640, 240), (0, 0, 255), 2 )

		# Display the rectifed images
		if self.rectification_enabled and self.calibration :

			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = vt.StereoRectification( self.calibration, image_left, image_right, True )

			# Prepare image for display
			stereo_image = np.concatenate( rectified_images, axis=1 )
			stereo_image = cv2.cvtColor( stereo_image, cv2.COLOR_BGR2RGB )

		# Display the disparity image
		elif self.disparity_enabled and self.calibration :

			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = vt.StereoRectification( self.calibration, image_left, image_right )
			rectified_images = cv2.pyrDown( rectified_images[0] ), cv2.pyrDown( rectified_images[1] )

			# Compute the disparity
			self.disparity.ComputeDisparity( *rectified_images )

			# Display the dispariy image
			stereo_image = cv2.pyrUp( self.disparity.disparity_image )

			# Point cloud
			self.coordinates = np.array( (self.X.flatten(), self.Y.flatten(), self.disparity.disparity.flatten() * 0.5) ).T
			self.coordinates = self.coordinates.reshape(-1, 3)
			self.coordinates[:,1] = -self.coordinates[:,1]
			self.colors = np.array( cv2.cvtColor( rectified_images[0], cv2.COLOR_BGR2RGB ), dtype=np.float32 ) / 255
			self.colors = self.colors.reshape(-1, 3)
			self.pointcloud_viewer.LoadPointCloud( self.coordinates, self.colors )

		# Or display the stereo images
		else :

			# Prepare image for display
			stereo_image = np.concatenate( (image_left_displayed, image_right_displayed), axis=1 )
			stereo_image = cv2.cvtColor( stereo_image, cv2.COLOR_BGR2RGB )

		# Update the image in the widget
		self.update_image.emit( stereo_image )

	#
	# Close the widget
	#
	def closeEvent( self, event ) :

		# Stop image acquisition
		self.stereo_camera.running = False
		self.stereo_camera.join()

		# Close the widgets
		self.pointcloud_viewer.close()
		self.disparity.close()
		event.accept()
