# -*- coding:utf-8 -*- 


#
# Module to display live images from two cameras
#


#
# External dependencies
#
import cv2
import numpy as np
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyStereoVisionToolkit import Calibration
from PyStereoVisionToolkit import Disparity


#
# Qt Widget to display the images from stereo cameras
#
class StereoCameraWidget( QtGui.QLabel ) :

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
		self.disparity_enabled = False

		# StereoSGBM
		self.disparity = Disparity.StereoSGBM()
		
		# Initialize the stereo cameras
		self.camera_left = cv2.VideoCapture( 0 )
		self.camera_right = cv2.VideoCapture( 1 )

		# Lower the camera frame rate
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
		self.camera_left.set( cv2.cv.CV_CAP_PROP_FPS, 5 )
		self.camera_right.set( cv2.cv.CV_CAP_PROP_FPS, 5 )

		# Timer for capture
		self.timer = QtCore.QTimer( self )
		self.timer.timeout.connect( self.QueryFrame )
		self.timer.start( 1000 / 5 )

	#
	# Capture frames and display them
	#
	def QueryFrame( self ) :
		
		# Capture images
		self.camera_left.grab()
		self.camera_right.grab()

		# Get the images
		_, self.image_left = self.camera_left.retrieve()
		_, self.image_right = self.camera_right.retrieve()

		# Copy images for display
		image_left_displayed = np.array( self.image_left )
		image_right_displayed = np.array( self.image_right )

		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_left_displayed = Calibration.PreviewChessboard( image_left_displayed )
			image_right_displayed = Calibration.PreviewChessboard( image_right_displayed )

		# Display a cross in the middle of the image
		if self.cross_enabled :
			cv2.rectangle( image_left_displayed, (220, 100), (420, 380), (0, 255, 0), 2 )
			cv2.rectangle( image_right_displayed, (220, 100), (420, 380), (0, 255, 0), 2 )
			cv2.line( image_left_displayed, (320, 0), (320, 480), (0, 0, 255), 2 )
			cv2.line( image_left_displayed, (0, 240), (640, 240), (0, 0, 255), 2 )
			cv2.line( image_right_displayed, (320, 0), (320, 480), (0, 0, 255), 2 )
			cv2.line( image_right_displayed, (0, 240), (640, 240), (0, 0, 255), 2 )

		# Display the disparity image
		if self.disparity_enabled and self.calibration :
			
			# Undistort the images according to the stereo camera calibration parameters
			rectified_images = Calibration.StereoRectification( self.calibration, self.image_left, self.image_right, True )
			rectified_images = cv2.pyrDown( rectified_images[0] ), cv2.pyrDown( rectified_images[1] )
		
			# Compute the disparity
			self.disparity.ComputeDisparity( *rectified_images )
			
			# Display the dispariy image
			stereo_image = self.disparity.disparity_image
		
		# Or display the stereo images
		else :
			
			# Prepare image for display
			stereo_image = np.concatenate( (image_left_displayed, image_right_displayed), axis=1 )
			stereo_image = cv2.cvtColor( stereo_image, cv2.COLOR_BGR2RGB )
		
		# Set the image
		self.setPixmap( QtGui.QPixmap.fromImage( QtGui.QImage( stereo_image,
			stereo_image.shape[1], stereo_image.shape[0], QtGui.QImage.Format_RGB888 ) ) )
			
		# Update the widget
		self.update()
		
	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :
		
		# Stop image acquisition
		self.timer.stop()
		self.camera_left.release()
		self.camera_right.release()
		
		# Close the widgets
		self.disparity.close()
		event.accept()
